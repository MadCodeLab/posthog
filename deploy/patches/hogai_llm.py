import os
import datetime
from collections.abc import (  # noqa: F401 — Sequence resolves inherited langchain field annotations lazily in this namespace
    Mapping,
    Sequence,
)
from functools import cached_property
from typing import Any, ClassVar, cast

from django.conf import settings

import pytz
import anthropic
import structlog
from asgiref.sync import sync_to_async
from langchain_anthropic import ChatAnthropic
import json
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import LLMResult
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.runnables import ensure_config
from langchain_openai import ChatOpenAI
from prometheus_client import Counter
from pydantic import BaseModel, ConfigDict

from posthog.models import Team, User
from posthog.settings import CLOUD_DEPLOYMENT

logger = structlog.get_logger(__name__)

BILLING_SKIPPED_COUNTER = Counter(
    "posthog_ai_billing_skipped_total",
    "Number of AI generations where billing was skipped due to workflow-level override (e.g., impersonation)",
    ["model"],
)

PROJECT_ORG_USER_CONTEXT_PROMPT = """
You are currently in project {{{project_name}}}, which is part of the {{{organization_name}}} organization.
The user's name appears to be {{{user_full_name}}} ({{{user_email}}}). Feel free to use their first name when greeting. DO NOT use this name if it appears possibly fake.
All PostHog app URLs must use root-relative paths starting with `/`, without a domain (no us.posthog.com, eu.posthog.com, app.posthog.com), and omit the `/project/:id/` prefix. Never include `/-/` in URLs. Never use relative paths like `../` or `./` — always start with `/`.
Use Markdown with descriptive anchor text, for example "[Cohorts view](/cohorts)".

Key URL patterns:
- Dashboard: `/dashboard/<id>`, e.g. `/dashboard/12345`
- Insights: `/insights/<short_id>`, e.g. `/insights/abc123`
- Settings: `/settings/<section-id>` where section IDs use hyphens, e.g. `/settings/organization-members`, `/settings/environment-replay`, `/settings/user-api-keys`. Section IDs are a fixed set, so never guess one because it sounds plausible; if you are not certain an ID is real, link `/settings` and name the section in the anchor text. Members and invites are organization-level (`/settings/organization-members`); there is no project members page, and per-project access is `/settings/environment-access-control`.
- Data management: `/data-management/events`, `/data-management/properties`
- Billing: `/organization/billing`
- Skills: `/skills`
Current time in the project's timezone, {{{project_timezone}}}: {{{project_datetime}}}.
When skill tools (`list_llm_skills`, `get_llm_skill`) are in your available tools, for topics such as user acquisition (UA), marketing, paid ads (Meta/Facebook/Instagram, TikTok, Apple Search Ads/ASA, Google App Campaigns), ROAS, ad creative design/hooks, mobile measurement partner (MMP like AppsFlyer/Adjust) setup, or subscription analysis (RevenueCat), always consult and follow the stored skills using `list_llm_skills` and `get_llm_skill` (e.g. `ads-router`, `meta-campaign-setup`, `tiktok-creative-strategy`, `campaign-profitability`, etc.). Only invoke tools that are present in your active tool list.
When the user communicates in Vietnamese, always respond in natural, helpful Vietnamese.
{{#person_on_events_enabled}}
Person-on-events mode is enabled. When querying `person.properties.*` on the events table, values reflect what was set at the time the event was ingested, not the person's current value. The same person can have different property values across different events. Do not suggest workarounds for "query-time" person properties.
{{/person_on_events_enabled}}
{{^person_on_events_enabled}}
Person properties are query-time in this project. `person.properties.*` on the events table always returns the person's current (latest) value, regardless of when the event occurred.
{{/person_on_events_enabled}}
""".strip()

# https://platform.openai.com/docs/guides/flex-processing
OPENAI_FLEX_MODELS = ["o3", "o4-mini", "gpt5", "gpt5-mini", "gpt5-nano"]

# Map "http://", "https://", and "all://" to None in Client's mounts to bypass proxies for MaxChatAnthropic.
_BYPASS_PROXY_MOUNTS: dict[str, None] = {"http://": None, "https://": None, "all://": None}

from django.db.models.signals import post_save
from django.dispatch import receiver


def seed_team_skills(team: Team) -> None:
    try:
        from products.skills.backend.models.community_skills import CommunitySkill, CommunitySkillFile
        from products.skills.backend.models.skills import LLMSkill, LLMSkillFile

        if LLMSkill.objects.filter(team=team, deleted=False).exists():
            return

        admin_user = User.objects.filter(is_staff=True).first() or User.objects.first()
        comm_skills = list(CommunitySkill.objects.filter(deleted=False))
        if not comm_skills:
            return

        for cs in comm_skills:
            skill = LLMSkill.objects.create(
                team=team,
                name=cs.name,
                description=cs.description,
                body=cs.body,
                license=cs.license,
                compatibility=cs.compatibility,
                allowed_tools=cs.allowed_tools,
                metadata=cs.metadata,
                category=getattr(cs, "category", ""),
                version=1,
                is_latest=True,
                created_by=admin_user,
            )
            files = list(CommunitySkillFile.objects.filter(skill=cs))
            if files:
                LLMSkillFile.objects.bulk_create(
                    [
                        LLMSkillFile(
                            skill=skill,
                            path=f.path,
                            content=f.content,
                            content_type=f.content_type,
                        )
                        for f in files
                    ]
                )
        logger.info("Auto-seeded skills for team", team_id=team.id, team_name=team.name, count=len(comm_skills))
    except Exception as e:
        logger.error("Failed to auto-seed skills for team", team_id=team.id, error=str(e))


@receiver(post_save, sender=Team)
def auto_seed_skills_on_new_team(sender, instance: Team, created: bool, **kwargs):
    if created:
        seed_team_skills(instance)



class MaxChatMixin(BaseModel):
    # We don't want to validate Django models here.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user: User
    team: Team
    max_retries: int | None = None
    stream_usage: bool | None = None
    conversation_start_dt: datetime.datetime | None = None
    """
    The datetime of the start of the conversation. If not provided, the current time will be used.
    """
    billable: bool = False
    """
    Whether the generation will be marked as billable in the usage report for calculating AI billing credits.
    """
    inject_context: bool = True
    """
    Whether to inject project/org/user context into the system prompt.
    Set to False to disable automatic context injection.
    """
    posthog_properties: dict[str, Any] | None = None
    """
    Additional PostHog properties to be added to the $ai_generation event.
    These will be merged with the standard properties like $ai_billable and team_id.
    """
    posthog_provider: ClassVar[str]

    def model_post_init(self, __context: Any) -> None:
        if self.max_retries is None:
            self.max_retries = 3
        if self.stream_usage is None:
            self.stream_usage = True

    def _get_project_org_user_variables(self) -> dict[str, Any]:
        """Note: this function may perform Postgres queries on `self._team`, `self._team.organization`, and `self._user`."""
        seed_team_skills(self.team)
        project_timezone = self.team.timezone
        adjusted_dt = self.conversation_start_dt or datetime.datetime.now()
        project_datetime = adjusted_dt.astimezone(tz=pytz.timezone(project_timezone))

        region = CLOUD_DEPLOYMENT or "US"
        if region in ["US", "EU"]:
            region = region.lower()
        else:
            region = "us"

        return {
            "project_name": self.team.name,
            "project_timezone": project_timezone,
            "project_datetime": project_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "organization_name": self.team.organization.name,
            "user_full_name": self.user.get_full_name(),
            "user_email": self.user.email,
            "deployment_region": region,
            "person_on_events_enabled": self.team.person_on_events_querying_enabled,
        }

    @sync_to_async
    def _aget_project_org_user_variables(self) -> dict[str, Any]:
        return self._get_project_org_user_variables()

    def _get_project_org_system_message(self, project_org_user_variables: dict[str, Any]) -> BaseMessage:
        return SystemMessagePromptTemplate.from_template(
            PROJECT_ORG_USER_CONTEXT_PROMPT, template_format="mustache"
        ).format(**project_org_user_variables)

    def _enrich_messages(self, messages: list[list[BaseMessage]], project_org_user_variables: dict[str, Any]):
        messages = messages.copy()
        for i in range(len(messages)):
            message_sublist = messages[i]
            # In every sublist (which becomes a separate generation) insert our shared prompt at the very end
            # of the system messages block
            for msg_index, msg in enumerate(message_sublist):
                if isinstance(msg, SystemMessage):
                    continue  # Keep going
                else:
                    # Here's our end of the system messages block
                    copied_list = message_sublist.copy()
                    copied_list.insert(msg_index, self._get_project_org_system_message(project_org_user_variables))
                    messages[i] = copied_list
                    break
        return messages

    def _get_effective_billable(self) -> bool:
        """
        Determine the effective billable status for this generation.
        Combines model-level billable setting with workflow-level override from config.
        When is_agent_billable is False (e.g., impersonated sessions), billing is skipped
        regardless of the model's billable setting.
        """
        config = ensure_config()
        is_agent_billable = (config.get("configurable") or {}).get("is_agent_billable", True)

        effective_billable = self.billable and is_agent_billable

        if self.billable and not is_agent_billable:
            # This is really annoying given the interface differences between model providers
            # Once we are behind a proxy, this can be simplified.
            model_name = getattr(self, "model", None) or getattr(self, "model_name", "unknown")
            BILLING_SKIPPED_COUNTER.labels(model=model_name).inc()
            logger.warning("Billing skipped for generation due to workflow-level override")

        return effective_billable

    def _with_posthog_properties(
        self,
        kwargs: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a shallow copy of kwargs with PostHog properties, billable flag, and team_id injected into metadata."""
        new_kwargs = dict(kwargs or {})
        metadata = dict(new_kwargs.get("metadata") or {})

        posthog_props = dict(self.posthog_properties or {})
        posthog_props["$ai_billable"] = self._get_effective_billable()
        posthog_props["team_id"] = self.team.id
        posthog_props.setdefault("ai_product", "posthog_ai")

        metadata.setdefault("ls_provider", self.posthog_provider)
        metadata["posthog_properties"] = posthog_props
        new_kwargs["metadata"] = metadata

        return new_kwargs


class MaxChatOpenAI(MaxChatMixin, ChatOpenAI):
    """PostHog-tuned subclass of ChatOpenAI.

    This subclass automatically injects project, organization, and user context as the final part of the system prompt.
    It also makes sure we retry automatically in case of an OpenAI API error.
    If billable is set to True, the generation will be marked as billable in the usage report for calculating AI billing credits.
    If inject_context is set to False, no context will be included in the system prompt.
    """

    posthog_provider: ClassVar[str] = "openai"

    def __init__(self, **kwargs: Any):
        env_model = os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high")
        if env_model:
            kwargs["model"] = env_model
            kwargs.pop("model_name", None)
        if "base_url" not in kwargs and getattr(settings, "OPENAI_BASE_URL", None):
            kwargs["base_url"] = settings.OPENAI_BASE_URL
        if "openai_api_base" not in kwargs and getattr(settings, "OPENAI_BASE_URL", None):
            kwargs["openai_api_base"] = settings.OPENAI_BASE_URL
        if "api_key" not in kwargs and getattr(settings, "OPENAI_API_KEY", None):
            kwargs["api_key"] = settings.OPENAI_API_KEY
        kwargs.pop("betas", None)
        kwargs.pop("thinking", None)
        kwargs.pop("bypass_proxy", None)
        if "model_kwargs" in kwargs and isinstance(kwargs["model_kwargs"], dict):
            kwargs["model_kwargs"].pop("output_config", None)
        super().__init__(**kwargs)

    def get_num_tokens_from_messages(
        self,
        messages: list[Any],
        tools: Any = None,
        **kwargs: Any,
    ) -> int:
        kwargs.pop("thinking", None)
        try:
            return super().get_num_tokens_from_messages(messages, tools=tools)
        except Exception:
            total_chars = sum(len(str(getattr(m, "content", ""))) for m in messages)
            return max(1, total_chars // 4)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if settings.IN_EVAL_TESTING and not self.service_tier and self.model_name in OPENAI_FLEX_MODELS:
            self.service_tier = "flex"  # 50% cheaper than default tier, but slower

    def _enrich_responses_api_model_kwargs(self, project_org_user_variables: dict[str, Any]) -> None:
        """Mutate the provided model_kwargs dict in-place, ensuring the project/org/user context is present.

        If the caller has already supplied ``instructions`` we append our context; otherwise we set ``instructions``
        from scratch. This function is intentionally side-effectful and returns ``None``.
        """

        system_msg_content = str(self._get_project_org_system_message(project_org_user_variables).content)

        if self.model_kwargs.get("instructions"):
            # Append to existing instructions
            self.model_kwargs["instructions"] = f"{system_msg_content}\n\n{self.model_kwargs['instructions']}"
        else:
            # Initialise instructions if absent or falsy
            self.model_kwargs["instructions"] = system_msg_content

    def _sanitize_tool_messages(self, messages: list[list[BaseMessage]]) -> list[list[BaseMessage]]:
        sanitized_batches = []
        for batch in messages:
            tool_id_to_name = {}
            for msg in batch:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tc_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
                        tc_name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                        if tc_id and tc_name:
                            tool_id_to_name[tc_id] = tc_name

            new_batch = []
            for msg in batch:
                # 1. Chuyen doi HumanMessage chua Anthropic tool_result sang ToolMessage chuan OpenAI
                if isinstance(msg, HumanMessage) and isinstance(msg.content, list):
                    regular_text_parts = []
                    for item in msg.content:
                        if isinstance(item, dict) and item.get("type") == "tool_result":
                            t_id = item.get("tool_use_id")
                            t_name = tool_id_to_name.get(t_id, "tool")
                            t_content = item.get("content", "")
                            if not isinstance(t_content, str):
                                t_content = json.dumps(t_content, ensure_ascii=False)
                            new_batch.append(ToolMessage(content=t_content, tool_call_id=t_id, name=t_name))
                        elif isinstance(item, dict) and item.get("type") == "text":
                            regular_text_parts.append(item.get("text", ""))
                        elif isinstance(item, str):
                            regular_text_parts.append(item)
                    if regular_text_parts:
                        new_batch.append(HumanMessage(content="\n".join(regular_text_parts)))
                elif isinstance(msg, AIMessage):
                    # Don dep cac khoi text cua Anthropic trong AIMessage
                    if isinstance(msg.content, list):
                        text_parts = []
                        for item in msg.content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                            elif isinstance(item, str):
                                text_parts.append(item)
                        msg.content = "\n".join(text_parts) if text_parts else ""
                    new_batch.append(msg)
                elif isinstance(msg, ToolMessage) or getattr(msg, "type", "") == "tool":
                    t_id = getattr(msg, "tool_call_id", None)
                    t_name = getattr(msg, "name", None)
                    if not t_name and t_id and t_id in tool_id_to_name:
                        msg.name = tool_id_to_name[t_id]
                    new_batch.append(msg)
                else:
                    new_batch.append(msg)

            try:
                import sys
                print("=== HOGAI SANITIZED MESSAGES BATCH ===", file=sys.stderr)
                for m in new_batch:
                    print(
                        f"ROLE={getattr(m, 'type', '?')} | NAME={getattr(m, 'name', None)} | TOOL_CALL_ID={getattr(m, 'tool_call_id', None)} | TOOL_CALLS={getattr(m, 'tool_calls', None)} | CONTENT={str(getattr(m, 'content', ''))[:120]}",
                        file=sys.stderr,
                    )
                print("=== END HOGAI MESSAGES ===", file=sys.stderr)
            except Exception:
                pass
            sanitized_batches.append(new_batch)
        return sanitized_batches

    def _filter_undeclared_tool_calls(self, result: LLMResult, kwargs: dict[str, Any]) -> None:
        tools_arg = kwargs.get("tools")
        if not tools_arg or not isinstance(tools_arg, (list, tuple)):
            return

        allowed_tool_names: set[str] = set()
        for t in tools_arg:
            if isinstance(t, dict):
                name = t.get("function", {}).get("name") or t.get("name")
                if name:
                    allowed_tool_names.add(name)
            elif hasattr(t, "name"):
                allowed_tool_names.add(t.name)

        if not allowed_tool_names:
            return

        for gen_list in getattr(result, "generations", []):
            for gen in gen_list:
                msg = getattr(gen, "message", None)
                if not msg:
                    continue
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    msg.tool_calls = [
                        tc for tc in msg.tool_calls
                        if isinstance(tc, dict) and tc.get("name") in allowed_tool_names
                    ]
                add_kwargs = getattr(msg, "additional_kwargs", None)
                if isinstance(add_kwargs, dict) and "tool_calls" in add_kwargs:
                    raw_tc_list = add_kwargs.get("tool_calls")
                    if isinstance(raw_tc_list, list):
                        add_kwargs["tool_calls"] = [
                            rtc for rtc in raw_tc_list
                            if isinstance(rtc, dict) and rtc.get("function", {}).get("name") in allowed_tool_names
                        ]

    def generate(
        self,
        messages: list[list[BaseMessage]],
        *args,
        **kwargs,
    ) -> LLMResult:
        if self.inject_context:
            project_org_user_variables = self._get_project_org_user_variables()
            if self.use_responses_api:
                self._enrich_responses_api_model_kwargs(project_org_user_variables)
            else:
                messages = self._enrich_messages(messages, project_org_user_variables)

        messages = self._sanitize_tool_messages(messages)
        kwargs = self._with_posthog_properties(kwargs)

        result = super().generate(messages, *args, **kwargs)
        self._filter_undeclared_tool_calls(result, kwargs)
        return result

    async def agenerate(
        self,
        messages: list[list[BaseMessage]],
        *args,
        **kwargs,
    ) -> LLMResult:
        if self.inject_context:
            project_org_user_variables = await self._aget_project_org_user_variables()
            if self.use_responses_api:
                self._enrich_responses_api_model_kwargs(project_org_user_variables)
            else:
                messages = self._enrich_messages(messages, project_org_user_variables)

        messages = self._sanitize_tool_messages(messages)
        kwargs = self._with_posthog_properties(kwargs)

        result = await super().agenerate(messages, *args, **kwargs)
        self._filter_undeclared_tool_calls(result, kwargs)
        return result


class MaxChatAnthropic(MaxChatMixin, ChatAnthropic):
    def __new__(cls, *args, **kwargs):
        env_model = os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high")
        ant_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not ant_key.startswith("sk-ant-api") or env_model:
            excluded_keys = {"betas", "thinking", "bypass_proxy", "anthropic_api_key", "anthropic_api_url", "default_headers"}
            clean_kwargs = {k: v for k, v in kwargs.items() if k not in excluded_keys}
            clean_kwargs["model"] = env_model
            if getattr(settings, "OPENAI_BASE_URL", None):
                clean_kwargs["base_url"] = settings.OPENAI_BASE_URL
            return MaxChatOpenAI(*args, **clean_kwargs)
        return super().__new__(cls)

    """PostHog-tuned subclass of ChatAnthropic.

    This subclass automatically injects project, organization, and user context as the final part of the system prompt.
    It also makes sure we retry automatically in case of errors.
    """

    posthog_provider: ClassVar[str] = "anthropic"

    bypass_proxy: bool = False
    """
    If True, bypasses egress proxies (HTTP_PROXY/etc)—use for private LLM gateway; if False, default behavior.
    """

    @cached_property
    def _client(self) -> anthropic.Client:
        if not self.bypass_proxy:
            # Defer to upstream so the lru_cache'd httpx client and default proxy behavior are preserved.
            return cast(anthropic.Client, ChatAnthropic._client.func(self))  # type: ignore[attr-defined]
        return anthropic.Client(
            **self._client_params,
            http_client=anthropic.DefaultHttpxClient(**self._bypass_http_client_kwargs()),
        )

    @cached_property
    def _async_client(self) -> anthropic.AsyncClient:
        if not self.bypass_proxy:
            return cast(anthropic.AsyncClient, ChatAnthropic._async_client.func(self))  # type: ignore[attr-defined]
        return anthropic.AsyncClient(
            **self._client_params,
            http_client=anthropic.DefaultAsyncHttpxClient(**self._bypass_http_client_kwargs()),
        )

    def _bypass_http_client_kwargs(self) -> dict[str, Any]:
        """Builds kwargs for ``anthropic.DefaultHttpxClient`` / ``DefaultAsyncHttpxClient`` to bypass the Smokescreen egress proxy without altering other SDK defaults.

        Instead of using ``trust_env=False``, which is ineffective due to SDK internals, we set ``mounts={"http://": None, "https://": None, "all://": None}`` to override environment proxy settings. This approach preserves all other Anthropic SDK connection defaults, such as timeouts, pool limits, and transport settings.

        This depends on the SDK merging the ``mounts`` kwarg on top of its proxy settings and retaining its defaults—guarded by tests in ``test_llm.py``.
        """

        client_params = self._client_params
        kwargs: dict[str, Any] = {
            "base_url": client_params["base_url"],
            "mounts": dict(_BYPASS_PROXY_MOUNTS),
        }
        if "timeout" in client_params:
            # Forward the caller's timeout (langchain-anthropic always sets this key, even when
            # the value is None) so the bypass path matches the non-bypass path's timeout exactly.
            kwargs["timeout"] = client_params["timeout"]
        return kwargs

    def generate(
        self,
        messages: list[list[BaseMessage]],
        *args,
        **kwargs,
    ) -> LLMResult:
        if self.inject_context:
            project_org_user_variables = self._get_project_org_user_variables()
            messages = self._enrich_messages(messages, project_org_user_variables)

        messages = self._sanitize_tool_messages(messages)
        kwargs = self._with_posthog_properties(kwargs)

        result = super().generate(messages, *args, **kwargs)
        self._filter_undeclared_tool_calls(result, kwargs)
        return result

    async def agenerate(
        self,
        messages: list[list[BaseMessage]],
        *args,
        **kwargs,
    ) -> LLMResult:
        if self.inject_context:
            project_org_user_variables = await self._aget_project_org_user_variables()
            messages = self._enrich_messages(messages, project_org_user_variables)

        messages = self._sanitize_tool_messages(messages)
        kwargs = self._with_posthog_properties(kwargs)

        result = await super().agenerate(messages, *args, **kwargs)
        self._filter_undeclared_tool_calls(result, kwargs)
        return result


try:
    from ee.hogai.chat_agent.memory import nodes as memory_nodes
    from ee.hogai.chat_agent.memory import parsers as memory_parsers
    from langchain_core.messages import AIMessage

    orig_check_memory = memory_parsers.check_memory_collection_completed

    def safe_check_memory_collection_completed(response: Any) -> AIMessage | None:
        if isinstance(response, AIMessage):
            if response.tool_calls:
                response.tool_calls = [
                    tc for tc in response.tool_calls
                    if isinstance(tc, dict) and tc.get("name") in {"core_memory_append", "core_memory_replace"}
                ]
            if "[Done]" in response.content or not response.tool_calls:
                return None
        return response

    memory_parsers.check_memory_collection_completed = safe_check_memory_collection_completed
    memory_nodes.check_memory_collection_completed = safe_check_memory_collection_completed

    orig_collector_tools_arun = memory_nodes.MemoryCollectorToolsNode.arun

    async def safe_collector_tools_arun(self, state, config):
        node_messages = state.memory_collection_messages or []
        if node_messages:
            last_message = node_messages[-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                last_message.tool_calls = [
                    tc for tc in last_message.tool_calls
                    if isinstance(tc, dict) and tc.get("name") in {"core_memory_append", "core_memory_replace"}
                ]
                if not last_message.tool_calls:
                    return memory_nodes.PartialAssistantState(memory_collection_messages=node_messages)
        try:
            return await orig_collector_tools_arun(self, state, config)
        except (KeyError, ValueError):
            return memory_nodes.PartialAssistantState(memory_collection_messages=node_messages)

    memory_nodes.MemoryCollectorToolsNode.arun = safe_collector_tools_arun
except Exception:
    pass

