import re

# 1. Update .env
with open("/home/opc/posthog-deployment/.env", "r") as f:
    env_content = f.read()

env_content = re.sub(r"^DOMAIN=.*$", "DOMAIN=ui-analyze.madcodelab.cloud", env_content, flags=re.MULTILINE)
env_content = re.sub(r"^SITE_URL=.*$", "SITE_URL=https://ui-analyze.madcodelab.cloud", env_content, flags=re.MULTILINE)

if "EXTRA_CSRF_TRUSTED_ORIGINS" not in env_content:
    env_content += "\nEXTRA_CSRF_TRUSTED_ORIGINS=\"https://ui-analyze.madcodelab.cloud,http://ui-analyze.madcodelab.cloud,http://localhost:8000,http://127.0.0.1:8000,https://localhost\"\n"

if "TRUST_ALL_PROXIES" not in env_content:
    env_content += "TRUST_ALL_PROXIES=true\n"

if "IS_BEHIND_PROXY" not in env_content:
    env_content += "IS_BEHIND_PROXY=true\n"

with open("/home/opc/posthog-deployment/.env", "w") as f:
    f.write(env_content)
print("Updated .env successfully.")

# 2. Update docker-compose.yml
with open("/home/opc/posthog-deployment/docker-compose.yml", "r") as f:
    compose = f.read()

# Caddy host fallback
compose = compose.replace("CADDY_HOST: \x27$DOMAIN, http://, https://\x27", "CADDY_HOST: \x27${CADDY_HOST:-$DOMAIN, http://, https://}\x27")

# Add to web environment
web_env_target = "SITE_URL: https://$DOMAIN"
replacement_web = """SITE_URL: https://$DOMAIN
            EXTRA_CSRF_TRUSTED_ORIGINS: ${EXTRA_CSRF_TRUSTED_ORIGINS:-https://ui-analyze.madcodelab.cloud,http://ui-analyze.madcodelab.cloud,http://localhost:8000,http://127.0.0.1:8000,https://localhost}
            TRUST_ALL_PROXIES: ${TRUST_ALL_PROXIES:-true}
            IS_BEHIND_PROXY: ${IS_BEHIND_PROXY:-true}"""

compose = compose.replace(web_env_target, replacement_web)

with open("/home/opc/posthog-deployment/docker-compose.yml", "w") as f:
    f.write(compose)
print("Updated docker-compose.yml successfully.")
