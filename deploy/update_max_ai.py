import re
import os

# 1. Update patches/views.py
views_path = "/home/opc/posthog-deployment/patches/views.py"
with open(views_path, "r", encoding="utf-8") as f:
    v_content = f.read()

v_content = v_content.replace(
    '"anthropic_available": bool(os.environ.get("ANTHROPIC_API_KEY")),',
    '"anthropic_available": bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")),'
)
with open(views_path, "w", encoding="utf-8") as f:
    f.write(v_content)
print("✓ Updated patches/views.py")

# 2. Update patches/hogai_llm.py
hogai_path = "/home/opc/posthog-deployment/patches/hogai_llm.py"
with open(hogai_path, "r", encoding="utf-8") as f:
    h_content = f.read()

target = 'class MaxChatAnthropic(MaxChatMixin, ChatAnthropic):'
redirect_code = '''class MaxChatAnthropic(MaxChatMixin, ChatAnthropic):
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
'''

if target in h_content and '__new__' not in h_content[h_content.find(target):h_content.find(target)+400]:
    h_content = h_content.replace(target, redirect_code, 1)
    with open(hogai_path, "w", encoding="utf-8") as f:
        f.write(h_content)
    print("✓ Updated patches/hogai_llm.py with MaxChatAnthropic -> MaxChatOpenAI routing")
else:
    print("Target already updated or not found in hogai_llm.py")
