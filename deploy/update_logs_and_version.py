import json
import re

VERSION = "20260908_1455"

vocab = {
    # Logs scene
    "Monitor and analyze your logs to understand and fix issues.": "Theo dõi và phân tích nhật ký để thấu hiểu và xử lý sự cố.",
    "Search every log from your stack in one place": "Tìm kiếm mọi dòng nhật ký từ toàn bộ hệ thống của bạn tại một nơi tập trung",
    "Send logs from any OpenTelemetry-compatible client over OTLP. No PostHog-specific packages needed. Filter by severity and attributes, query with SQL, and set alerts on the lines that matter.": "Gửi nhật ký từ bất kỳ client tương thích OpenTelemetry nào qua OTLP. Không cần cài thêm gói riêng của PostHog. Lọc theo mức độ nghiêm trọng và thuộc tính, truy vấn bằng SQL và thiết lập cảnh báo cho các dòng quan trọng.",
    "Your log stream, once connected": "Luồng nhật ký của bạn, sau khi kết nối",
    "Live logs": "Nhật ký trực tiếp",
    "Live logsdữ liệu mẫu": "Nhật ký trực tiếp (dữ liệu mẫu)",
    "service: all": "dịch vụ: tất cả",
    "service: all1,204 lines": "dịch vụ: tất cả · 1.204 dòng",
    "Log attributes": "Thuộc tính nhật ký",
    "Filter to errors only to inspect the failing request.": "Lọc chỉ các lỗi để kiểm tra yêu cầu bị thất bại.",
    "warn": "Cảnh báo",
    "info": "Thông tin",
    "error": "Lỗi",
    "critical": "Nghiêm trọng",
    "debug": "Gỡ lỗi",
    "lines": "dòng",
    "Viewer": "Trình xem nhật ký",
    "Services": "Dịch vụ",
    "Alerts": "Cảnh báo",
    "Anomalies": "Bất thường",
    "Transformations": "Chuyển đổi",
    "Configuration": "Cấu hình",
    "Feedback": "Phản hồi",
    "No baseline yet": "Chưa có đường cơ sở",
    "Choose a service": "Chọn một dịch vụ",
    "Try again": "Thử lại",
    "No logs to chart": "Không có nhật ký nào để vẽ biểu đồ",
    "Log volume per hour from": "Khối lượng nhật ký mỗi giờ từ",
    "Log volume by series": "Khối lượng nhật ký theo chuỗi",
    "Learning baseline": "Đang học đường cơ sở",
    "Show more": "Hiển thị thêm",
    "Observed": "Đã ghi nhận",
    "First seen": "Xuất hiện lần đầu",
    "The expected range starts": "Phạm vi dự kiến bắt đầu từ",

    # Logs Sample events
    "checkout-api request completed in 42 ms": "checkout-api: yêu cầu hoàn tất trong 42 ms",
    "web cache hit for /api/products": "web: bộ nhớ đệm khớp cho /api/products",
    "checkout-api retrying payment provider call (attempt 2)": "checkout-api: đang thử lại gọi nhà cung cấp thanh toán (lần 2)",
    "checkout-api payment failed: card_declined": "checkout-api: thanh toán thất bại: card_declined (thẻ bị từ chối)",
    "web GET /api/products 200": "web: GET /api/products 200 (thành công)",
    "checkout-api upstream timeout after 3000 ms": "checkout-api: hết thời gian chờ dịch vụ thượng nguồn sau 3000 ms",

    # Tracing
    "Tracing": "Truy vết phân tán (Tracing)",
    "Monitor and analyze your traces to understand performance and dependencies.": "Theo dõi và phân tích truy vết để nắm bắt hiệu năng và các phụ thuộc dịch vụ.",
    "Search every trace across your stack": "Tìm kiếm mọi truy vết trên toàn bộ ngăn xếp công nghệ của bạn",
    "Your trace stream, once connected": "Luồng truy vết của bạn, sau khi kết nối",
    "Live traces": "Truy vết trực tiếp",
    "Trace attributes": "Thuộc tính truy vết",
    "Spans": "Đoạn truy vết (Spans)",
    "Service map": "Bản đồ dịch vụ",
    "Latency": "Độ trễ",
    "Duration": "Thời lượng",

    # LLM Observability / AI Monitoring
    "Generations": "Lượt sinh phản hồi",
    "Cost": "Chi phí",
    "Tokens": "Số lượng Token",
    "Input tokens": "Token đầu vào",
    "Output tokens": "Token đầu ra",
    "Model": "Mô hình",
    "Provider": "Nhà cung cấp",
    "Total cost": "Tổng chi phí",
    "Average latency": "Độ trễ trung bình",
    "Error rate": "Tỷ lệ lỗi",
    "User feedback": "Phản hồi của người dùng"
}

vi_path = "/home/opc/posthog-deployment/i18n/locales/vi.json"
en_path = "/home/opc/posthog-deployment/i18n/locales/en.json"

with open(vi_path, "r", encoding="utf-8") as f:
    vi_data = json.load(f)

with open(en_path, "r", encoding="utf-8") as f:
    en_data = json.load(f)

for k, v in vocab.items():
    vi_data[k] = v
    if k not in en_data:
        en_data[k] = k

with open(vi_path, "w", encoding="utf-8") as f:
    json.dump(vi_data, f, ensure_ascii=False, indent=2)

with open(en_path, "w", encoding="utf-8") as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

with open("/home/opc/posthog-deployment/i18n/locales/vi.js", "w", encoding="utf-8") as f:
    f.write("window.__POSTHOG_I18N_VI__ = " + json.dumps(vi_data, ensure_ascii=False, indent=2) + ";\nif (window.PostHogI18n && window.PostHogI18n.registerLocale) { window.PostHogI18n.registerLocale(\"vi\", window.__POSTHOG_I18N_VI__); }\n")

with open("/home/opc/posthog-deployment/i18n/locales/en.js", "w", encoding="utf-8") as f:
    f.write("window.__POSTHOG_I18N_EN__ = " + json.dumps(en_data, ensure_ascii=False, indent=2) + ";\nif (window.PostHogI18n && window.PostHogI18n.registerLocale) { window.PostHogI18n.registerLocale(\"en\", window.__POSTHOG_I18N_EN__); }\n")

# Cập nhật posthog-i18n.js để loadLocale có cache buster
i18n_path = "/home/opc/posthog-deployment/i18n/posthog-i18n.js"
with open(i18n_path, "r", encoding="utf-8") as f:
    i18n_content = f.read()

i18n_content = re.sub(r"fetch\(`/static/locales/\$\{code\}\.json.*?\`\)", f"fetch(`/static/locales/${{code}}.json?v={VERSION}`)", i18n_content)

with open(i18n_path, "w", encoding="utf-8") as f:
    f.write(i18n_content)

# Cập nhật head.html với cache buster mới
head_path = "/home/opc/posthog-deployment/custom_templates/head.html"
with open(head_path, "r", encoding="utf-8") as f:
    head_content = f.read()

head_content = re.sub(r"posthog-i18n\.css\?v=[^\"]+", f"posthog-i18n.css?v={VERSION}", head_content)
head_content = re.sub(r"locales/en\.js\?v=[^\"]+", f"locales/en.js?v={VERSION}", head_content)
head_content = re.sub(r"locales/vi\.js\?v=[^\"]+", f"locales/vi.js?v={VERSION}", head_content)
head_content = re.sub(r"posthog-i18n\.js\?v=[^\"]+", f"posthog-i18n.js?v={VERSION}", head_content)

with open(head_path, "w", encoding="utf-8") as f:
    f.write(head_content)

print(f"Cập nhật thành công toàn bộ hệ thống lên phiên bản {VERSION}!")
print("Tổng số từ vựng trong vi.json:", len(vi_data))
