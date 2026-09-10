import re

# 1. Cập nhật patches/signup.py
signup_file = "/home/opc/posthog-deployment/patches/signup.py"
with open(signup_file, "r", encoding="utf-8") as f:
    code = f.read()

# Chặn SignupViewset
target_signup = """class SignupViewset(generics.CreateAPIView):
    serializer_class = SignupSerializer
    # Enables E2E testing of signup flow
    permission_classes = (permissions.AllowAny,) if settings.E2E_TESTING else (CanCreateOrg,)
    throttle_classes = [] if settings.E2E_TESTING else [SignupIPThrottle]"""

replacement_signup = """class SignupViewset(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = (permissions.AllowAny,)
    throttle_classes = []

    def create(self, request, *args, **kwargs):
        raise exceptions.PermissionDenied("Chức năng đăng ký tài khoản đã bị vô hiệu hóa.")"""

if target_signup in code:
    code = code.replace(target_signup, replacement_signup)
    print("Đã vô hiệu hóa SignupViewset")

# Chặn SocialSignupViewset
target_social = """class SocialSignupViewset(generics.CreateAPIView):
    serializer_class = SocialSignupSerializer
    permission_classes = (CanCreateOrg,)"""

replacement_social = """class SocialSignupViewset(generics.CreateAPIView):
    serializer_class = SocialSignupSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        raise exceptions.PermissionDenied("Chức năng đăng ký tài khoản đã bị vô hiệu hóa.")"""

if target_social in code:
    code = code.replace(target_social, replacement_social)
    print("Đã vô hiệu hóa SocialSignupViewset")

with open(signup_file, "w", encoding="utf-8") as f:
    f.write(code)

# 2. Cập nhật docker-compose.yml để mount patches/signup.py
compose_file = "/home/opc/posthog-deployment/docker-compose.yml"
with open(compose_file, "r", encoding="utf-8") as f:
    compose = f.read()

mount_line = "            - ./patches/signup.py:/code/posthog/api/signup.py:ro\n"
if "./patches/signup.py" not in compose:
    compose = compose.replace(
        "            - ./patches/views.py:/code/posthog/views.py:ro\n",
        "            - ./patches/views.py:/code/posthog/views.py:ro\n" + mount_line
    )
    with open(compose_file, "w", encoding="utf-8") as f:
        f.write(compose)
    print("Đã thêm mount patches/signup.py vào docker-compose.yml")

# 3. Cập nhật posthog-i18n.css để ẩn triệt để nút đăng ký
css_file = "/home/opc/posthog-deployment/i18n/posthog-i18n.css"
with open(css_file, "r", encoding="utf-8") as f:
    css_content = f.read()

hide_signup_css = """
/* Ẩn hoàn toàn tính năng đăng ký tài khoản */
[data-attr="signup"],
p:has([data-attr="signup"]),
a[href*="/signup"],
a[href*="signup"],
.signup-link,
[data-attr="signup-email"],
[data-attr="signup-submit"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
"""

if "data-attr=\"signup\"" not in css_content:
    css_content += hide_signup_css
    with open(css_file, "w", encoding="utf-8") as f:
        f.write(css_content)
    print("Đã thêm CSS ẩn nút đăng ký")

# 4. Cập nhật posthog-i18n.js để chặn và redirect /signup về /login
js_file = "/home/opc/posthog-deployment/i18n/posthog-i18n.js"
with open(js_file, "r", encoding="utf-8") as f:
    js_content = f.read()

redirect_snippet = """
    // Tự động chuyển hướng về /login nếu người dùng truy cập /signup
    if (window.location.pathname.startsWith('/signup') || window.location.pathname.startsWith('/sign-up')) {
        window.location.replace('/login');
    }

    // Tự động gỡ bỏ các nút / liên kết đăng ký khỏi DOM
    function removeSignupElements() {
        try {
            const signupLinks = document.querySelectorAll('[data-attr="signup"], a[href*="/signup"]');
            signupLinks.forEach(el => {
                const p = el.closest('p');
                if (p) p.remove();
                else el.remove();
            });
        } catch (e) {}
    }
"""

if "removeSignupElements" not in js_content:
    # Chèn vào đầu hàm init hoặc scanAndTranslate
    js_content = js_content.replace(
        "function scanAndTranslate(root) {",
        "function scanAndTranslate(root) {\n        removeSignupElements();"
    )
    # Chèn định nghĩa hàm ở trước scanAndTranslate
    js_content = js_content.replace(
        "function scanAndTranslate(root) {",
        redirect_snippet + "\n    function scanAndTranslate(root) {"
    )
    with open(js_file, "w", encoding="utf-8") as f:
        f.write(js_content)
    print("Đã cập nhật posthog-i18n.js với logic xóa nút đăng ký và redirect")

# 5. Cập nhật cache buster
head_file = "/home/opc/posthog-deployment/custom_templates/head.html"
with open(head_file, "r", encoding="utf-8") as f:
    head_content = f.read()

VERSION = "20260908_1600"
head_content = re.sub(r"v=20260908_[0-9]+", f"v={VERSION}", head_content)

with open(head_file, "w", encoding="utf-8") as f:
    f.write(head_content)

print(f"Hoàn tất! Đã nâng cấp toàn hệ thống lên phiên bản {VERSION}")
