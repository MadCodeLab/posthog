import re

# 1. Update .env
with open("/home/opc/posthog-deployment/.env", "r") as f:
    env_content = f.read()

def set_env(key, val, text):
    pattern = rf"^{key}=.*$"
    if re.search(pattern, text, flags=re.MULTILINE):
        return re.sub(pattern, f"{key}={val}", text, flags=re.MULTILINE)
    else:
        return text + f"\n{key}={val}\n"

env_content = set_env("OPENAI_API_KEY", "sk-ag-3ee0c0193e3f3cae358e75fca84984b3a505d2ac", env_content)
env_content = set_env("OPENAI_BASE_URL", "https://ecommerce-reduction-hearing-whenever.trycloudflare.com/v1", env_content)

with open("/home/opc/posthog-deployment/.env", "w") as f:
    f.write(env_content)
print("Updated .env with OpenAI credentials.")

# 2. Update docker-compose.yml
with open("/home/opc/posthog-deployment/docker-compose.yml", "r") as f:
    compose = f.read()

# Make sure OPENAI_BASE_URL is passed to web, worker, temporal-django-worker
if "OPENAI_BASE_URL:" not in compose:
    target = "OPENAI_API_KEY: ${OPENAI_API_KEY:-}"
    replacement = "OPENAI_API_KEY: ${OPENAI_API_KEY:-}\n            OPENAI_BASE_URL: ${OPENAI_BASE_URL:-https://api.openai.com/v1}"
    compose = compose.replace(target, replacement)
    with open("/home/opc/posthog-deployment/docker-compose.yml", "w") as f:
        f.write(compose)
    print("Updated docker-compose.yml with OPENAI_BASE_URL.")
else:
    print("docker-compose.yml already has OPENAI_BASE_URL.")
