import re
import os

print('Applying patches to /home/opc/posthog-deployment/patches...')

# 1. completions.py
comp_path = '/home/opc/posthog-deployment/patches/completions.py'
with open(comp_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'(def hit_openai\([^)]*response_format:\s*dict\[str,\s*Any\]\s*\|\s*None\s*=\s*None,)\s*(\)\s*->\s*OpenAICompletion:)',
    r'\1\n    model: str | None = None,\2',
    content
)
old_call = 'result = openai_client.chat.completions.create(\n        model="gpt-4.1-mini",'
new_call = 'effective_model = model or os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high")\n    result = openai_client.chat.completions.create(\n        model=effective_model,'
if old_call in content:
    content = content.replace(old_call, new_call)
else:
    content = re.sub(
        r'result\s*=\s*openai_client\.chat\.completions\.create\(\s*model="[^"]+",',
        'effective_model = model or os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high")\n    result = openai_client.chat.completions.create(\n        model=effective_model,',
        content
    )
with open(comp_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ Patched completions.py')

# 2. wizard_http.py
wiz_path = '/home/opc/posthog-deployment/patches/wizard_http.py'
with open(wiz_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'SETUP_WIZARD_DEFAULT_MODEL = "gpt-5-mini"',
    'SETUP_WIZARD_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high")',
    content
)
content = re.sub(
    r'OPENAI_SUPPORTED_MODELS = \{[^}]+\}',
    'OPENAI_SUPPORTED_MODELS = {"o4-mini", "gpt-5-mini", "gpt-5-nano", "gpt-5", "gemini-3.8-flash-high", os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high")}',
    content
)
content = content.replace(
    'if value not in ALL_SUPPORTED_MODELS:',
    'if value not in ALL_SUPPORTED_MODELS and value != os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high"):'
)
content = content.replace(
    'elif model in OPENAI_SUPPORTED_MODELS:',
    'elif model in OPENAI_SUPPORTED_MODELS or model == os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high"):'
)
content = content.replace(
    'result = openai.chat.completions.create(\n                model=model,',
    'effective_model = os.getenv("OPENAI_MODEL", model)\n            result = openai.chat.completions.create(\n                model=effective_model,'
)
with open(wiz_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ Patched wizard_http.py')

# 3. session_recordings_openai_client.py
srec_path = '/home/opc/posthog-deployment/patches/session_recordings_openai_client.py'
with open(srec_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'if not settings.DEBUG and not is_cloud():',
    'if not settings.DEBUG and not is_cloud() and not os.environ.get("OPENAI_API_KEY"):'
)
with open(srec_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ Patched session_recordings_openai_client.py')

# 4. llm_endpoint.py
llm_end_path = '/home/opc/posthog-deployment/patches/llm_endpoint.py'
with open(llm_end_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'if not settings.DEBUG and not is_cloud():',
    'if not settings.DEBUG and not is_cloud() and not os.environ.get("OPENAI_API_KEY"):'
)
old_direct = '''    direct_key = os.environ.get("OPENAI_API_KEY")
    if not direct_key:
        raise Exception("OPENAI_API_KEY is not configured")
    return FlexFirstChatOpenAI(
        model=model, api_key=direct_key, timeout=timeout, max_retries=max_retries, service_tier=service_tier
    )'''

new_direct = '''    effective_model = os.getenv("OPENAI_MODEL", model)
    direct_key = os.environ.get("OPENAI_API_KEY")
    if not direct_key:
        raise Exception("OPENAI_API_KEY is not configured")
    return FlexFirstChatOpenAI(
        model=effective_model,
        api_key=direct_key,
        base_url=settings.OPENAI_BASE_URL,
        timeout=timeout,
        max_retries=max_retries,
        service_tier=service_tier,
    )'''

content = content.replace(old_direct, new_direct)
content = content.replace(
    'return FlexFirstChatOpenAI(\n            model=model,',
    'effective_model = os.getenv("OPENAI_MODEL", model)\n        return FlexFirstChatOpenAI(\n            model=effective_model,'
)
with open(llm_end_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ Patched llm_endpoint.py')

# 5. hogai_llm.py
hogai_path = '/home/opc/posthog-deployment/patches/hogai_llm.py'
with open(hogai_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '    posthog_provider: ClassVar[str] = "openai"'
replacement = '''    posthog_provider: ClassVar[str] = "openai"

    def __init__(self, **kwargs: Any):
        env_model = os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high")
        if env_model:
            kwargs["model"] = env_model
            kwargs.pop("model_name", None)
        if "base_url" not in kwargs and getattr(settings, "OPENAI_BASE_URL", None):
            kwargs["base_url"] = settings.OPENAI_BASE_URL
        if "openai_api_base" not in kwargs and getattr(settings, "OPENAI_BASE_URL", None):
            kwargs["openai_api_base"] = settings.OPENAI_BASE_URL
        super().__init__(**kwargs)'''

if target in content and '__init__' not in content[content.find(target):content.find(target)+300]:
    content = content.replace(target, replacement, 1)

with open(hogai_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ Patched hogai_llm.py')

# 6. summarization_openai.py
sum_path = '/home/opc/posthog-deployment/patches/summarization_openai.py'
with open(sum_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'return request_client.chat.completions.create(\n            model=str(model),',
    'effective_model = os.getenv("OPENAI_MODEL", str(model))\n        return request_client.chat.completions.create(\n            model=effective_model,'
)
with open(sum_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ Patched summarization_openai.py')

# 7. csp_reporting.py
csp_path = '/home/opc/posthog-deployment/patches/csp_reporting.py'
with open(csp_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'llm_response = OpenAI\(posthog_client=posthoganalytics\.default_client\)\.chat\.completions\.create\(\s*model="[^"]+",',
    'llm_response = OpenAI(posthog_client=posthoganalytics.default_client, base_url=settings.OPENAI_BASE_URL).chat.completions.create(\n            model=os.getenv("OPENAI_MODEL", "gemini-3.8-flash-high"),',
    content
)
with open(csp_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('✓ Patched csp_reporting.py')

print('All patches applied successfully!')
