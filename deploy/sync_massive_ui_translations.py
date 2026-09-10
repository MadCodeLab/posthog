import json
import re

VERSION = "20260908_1530"

# Kho từ điển siêu toàn diện cho toàn bộ các màn hình PostHog
massive_vocab = {
    # 1. Insights & Phân tích dữ liệu (Trends, Funnels, Retention, Paths...)
    "AI analysis": "Phân tích bằng AI",
    "Get AI-powered insights about your data, including trends, patterns, and actionable recommendations.": "Nhận phân tích dữ liệu chuyên sâu bằng AI, bao gồm các xu hướng, mẫu hình và đề xuất hữu ích.",
    "None (i.e. no value)": "Không có (tức không có giá trị)",
    "None": "Không có",
    "Trends": "Xu hướng",
    "Funnels": "Phễu chuyển đổi",
    "Retention": "Tỷ lệ giữ chân",
    "User paths": "Đường dẫn người dùng",
    "Paths": "Đường dẫn luồng người dùng",
    "Stickiness": "Độ gắn kết",
    "Lifecycle": "Vòng đời người dùng",
    "SQL": "Trình chỉnh sửa SQL",
    "Formula": "Công thức",
    "Formulas": "Các công thức",
    "Breakdown by": "Phân tách theo",
    "Add breakdown": "Thêm tiêu chí phân tách",
    "Compare to previous period": "So sánh với kỳ trước",
    "Compare to": "So sánh với",
    "Add step": "Thêm bước",
    "Add graph series": "Thêm chuỗi biểu đồ",
    "Event name": "Tên sự kiện",
    "Action name": "Tên hành động",
    "Filter by": "Lọc theo",
    "Total volume": "Tổng khối lượng",
    "Unique users": "Người dùng duy nhất",
    "Weekly active users": "Người dùng hoạt động hàng tuần",
    "Monthly active users": "Người dùng hoạt động hàng tháng",
    "Daily active users": "Người dùng hoạt động hàng ngày",
    "Conversion rate": "Tỷ lệ chuyển đổi",
    "Time to convert": "Thời gian chuyển đổi",
    "Dropped off": "Rời khỏi phễu",
    "Completed": "Đã hoàn thành",
    "Bar chart": "Biểu đồ cột",
    "Line chart": "Biểu đồ đường",
    "Area chart": "Biểu đồ miền",
    "Pie chart": "Biểu đồ tròn",
    "Table": "Bảng dữ liệu",
    "World map": "Bản đồ thế giới",
    "Number": "Số liệu tổng quan",
    "Cumulative": "Tích lũy",
    "Linear": "Tuyến tính",
    "Logarithmic": "Logarit",
    "Display": "Hiển thị",
    "Chart type": "Loại biểu đồ",
    "Interval": "Khoảng thời gian",
    "Aggregation": "Phương pháp tổng hợp",
    "Save as": "Lưu thành",
    "Discard changes": "Hủy thay đổi",
    "Add to dashboard": "Thêm vào bảng điều khiển",
    "Generate AI summary": "Tạo tóm tắt bằng AI",
    "Summarize with AI": "Tóm tắt dữ liệu với AI",
    "Ask PostHog AI": "Hỏi trợ lý PostHog AI",
    "Exploration": "Khám phá chuyên sâu",
    "Configure chart": "Cấu hình biểu đồ",
    "Y-axis": "Trục Y",
    "X-axis": "Trục X",
    "Show values on series": "Hiển thị giá trị trên chuỗi",
    "Percent stack view": "Hiển thị xếp chồng theo phần trăm",
    "Total": "Tổng cộng",
    "Average": "Trung bình",
    "Median": "Trung vị",
    "Minimum": "Tối thiểu",
    "Maximum": "Tối đa",
    "90th percentile": "Phân vị 90",
    "95th percentile": "Phân vị 95",
    "99th percentile": "Phân vị 99",

    # 2. Cài đặt (Settings) & Quản lý Tổ chức, Dự án
    "Project settings": "Cài đặt dự án",
    "Organization settings": "Cài đặt tổ chức",
    "Team members": "Thành viên nhóm",
    "Billing": "Thanh toán & Gói cước",
    "Authentication": "Xác thực & Bảo mật",
    "Integrations": "Tích hợp dịch vụ",
    "Webhooks": "Webhooks gửi thông báo",
    "API keys": "Khóa API",
    "Authorized domains": "Tên miền được ủy quyền",
    "Environment": "Môi trường",
    "Environments": "Các môi trường",
    "Project name": "Tên dự án",
    "Organization name": "Tên tổ chức",
    "Delete project": "Xóa dự án",
    "Danger zone": "Vùng nguy hiểm",
    "Roles": "Vai trò & Quyền hạn",
    "Permissions": "Phân quyền",
    "Invite members": "Mời thành viên",
    "Pending invites": "Lời mời đang chờ",
    "Audit logs": "Nhật ký kiểm tra hệ thống",
    "Access control": "Kiểm soát quyền truy cập",
    "Personal API keys": "Khóa API cá nhân",
    "Project API key": "Khóa API dự án",

    # 3. Phân tích AI & Giám sát LLM (LLM Observability)
    "Generations": "Lượt sinh nội dung",
    "Cost": "Chi phí",
    "Tokens": "Số lượng Token",
    "Input tokens": "Token đầu vào",
    "Output tokens": "Token đầu ra",
    "Model": "Mô hình",
    "Provider": "Nhà cung cấp",
    "Total cost": "Tổng chi phí",
    "Average latency": "Độ trễ trung bình",
    "Error rate": "Tỷ lệ lỗi",
    "User feedback": "Phản hồi người dùng",
    "Prompt": "Câu nhắc (Prompt)",
    "Prompts": "Các câu nhắc",
    "Traces": "Truy vết thực thi",
    "Span": "Đoạn truy vết",
    "Spans": "Các đoạn truy vết",

    # 4. Dữ liệu & Kho lưu trữ (Data Warehouse, Pipelines, Batch Exports)
    "Data warehouse": "Kho dữ liệu",
    "Data pipelines": "Đường ống dữ liệu",
    "Batch exports": "Xuất dữ liệu hàng loạt",
    "Sources": "Nguồn dữ liệu",
    "Destinations": "Đích dữ liệu",
    "Transformations": "Chuyển đổi dữ liệu",
    "Schema": "Cấu trúc dữ liệu (Schema)",
    "Schemas": "Các cấu trúc dữ liệu",
    "Sync frequency": "Tần suất đồng bộ",
    "Last sync": "Lần đồng bộ gần nhất",
    "Sync now": "Đồng bộ ngay",
    "Paused": "Đã tạm dừng",
    "Active": "Đang hoạt động",
    "Failed": "Thất bại",

    # 5. Bản ghi phiên (Session Replay) & Heatmaps & Web Analytics
    "Console logs": "Nhật ký bảng điều khiển",
    "Network requests": "Các yêu cầu mạng",
    "DOM events": "Sự kiện DOM",
    "Mobile recordings": "Bản ghi di động",
    "Trigger groups": "Nhóm kích hoạt ghi phiên",
    "Click & scroll heatmaps": "Bản đồ nhiệt nhấp chuột & cuộn trang",
    "Heatmaps": "Bản đồ nhiệt (Heatmaps)",
    "Web analytics": "Phân tích trang web",
    "Bounce rate": "Tỷ lệ thoát trang",
    "Scroll depth": "Độ sâu cuộn trang",
    "Session duration": "Thời lượng phiên",
    "Top pages": "Các trang hàng đầu",
    "Top sources": "Nguồn lưu lượng hàng đầu",
    "Top devices": "Thiết bị hàng đầu",
    "Top browsers": "Trình duyệt hàng đầu",
    "Top countries": "Quốc gia hàng đầu",

    # 6. Các hành động & Thao tác phổ biến (Actions & Common UI)
    "Copy to clipboard": "Sao chép vào khay nhớ tạm",
    "Start typing...": "Bắt đầu nhập...",
    "Please enter the new name": "Vui lòng nhập tên mới",
    "Good call!": "Lựa chọn tuyệt vời!",
    "No override": "Không ghi đè",
    "Initial UTM source": "Nguồn UTM ban đầu",
    "Initial UTM medium": "Phương tiện UTM ban đầu",
    "Initial UTM campaign": "Chiến dịch UTM ban đầu",
    "Install the package": "Cài đặt gói thư viện",
    "Initialize PostHog": "Khởi tạo PostHog",
    "Send events": "Gửi sự kiện",
    "Configure PostHog": "Cấu hình PostHog",
    "Dismiss": "Bỏ qua",
    "Save changes": "Lưu thay đổi",
    "Discard": "Hủy bỏ",
    "Apply": "Áp dụng",
    "Cancel": "Hủy",
    "Confirm": "Xác nhận",
    "Delete": "Xóa",
    "Edit": "Chỉnh sửa",
    "Rename": "Đổi tên",
    "Duplicate": "Nhân bản",
    "Export": "Xuất dữ liệu",
    "Share": "Chia sẻ",
    "Copy link": "Sao chép liên kết",
    "Refresh": "Làm mới",
    "Download": "Tải xuống",
    "Upload": "Tải lên",
    "Search...": "Tìm kiếm...",
    "Select an option": "Chọn một mục",
    "No options": "Không có lựa chọn nào",
    "No data": "Không có dữ liệu",
    "No results": "Không có kết quả",
    "Loading...": "Đang tải dữ liệu...",
    "Loading data...": "Đang tải dữ liệu...",
    "No recording selected": "Chưa chọn bản ghi nào",
    "No session ID found": "Không tìm thấy ID phiên",
    "Undo": "Hoàn tác",
    "Redo": "Làm lại",
    "Close": "Đóng",
    "Back": "Quay lại",
    "Next": "Tiếp theo",
    "Finish": "Hoàn thành",
    "Skip": "Bỏ qua bước này",
    "Required": "Bắt buộc",
    "Optional": "Không bắt buộc",
    "Default": "Mặc định",
    "Custom": "Tùy chỉnh"
}

# 1. Đọc tệp hiện tại
vi_path = "/home/opc/posthog-deployment/i18n/locales/vi.json"
en_path = "/home/opc/posthog-deployment/i18n/locales/en.json"

with open(vi_path, "r", encoding="utf-8") as f:
    vi_data = json.load(f)

with open(en_path, "r", encoding="utf-8") as f:
    en_data = json.load(f)

added = 0
for k, v in massive_vocab.items():
    if k not in vi_data or vi_data[k] != v:
        vi_data[k] = v
        en_data[k] = k
        added += 1

print(f"Đã nạp thêm/cập nhật {added} từ khóa toàn diện vào bộ từ điển!")

# Lưu vi.json và en.json
with open(vi_path, "w", encoding="utf-8") as f:
    json.dump(vi_data, f, ensure_ascii=False, indent=2)

with open(en_path, "w", encoding="utf-8") as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

# Lưu vi.js và en.js
with open("/home/opc/posthog-deployment/i18n/locales/vi.js", "w", encoding="utf-8") as f:
    f.write("window.__POSTHOG_I18N_VI__ = " + json.dumps(vi_data, ensure_ascii=False, indent=2) + ";\nif (window.PostHogI18n && window.PostHogI18n.registerLocale) { window.PostHogI18n.registerLocale(\"vi\", window.__POSTHOG_I18N_VI__); }\n")

with open("/home/opc/posthog-deployment/i18n/locales/en.js", "w", encoding="utf-8") as f:
    f.write("window.__POSTHOG_I18N_EN__ = " + json.dumps(en_data, ensure_ascii=False, indent=2) + ";\nif (window.PostHogI18n && window.PostHogI18n.registerLocale) { window.PostHogI18n.registerLocale(\"en\", window.__POSTHOG_I18N_EN__); }\n")

# 2. Cập nhật posthog-i18n.js để thêm quy tắc regex Computed và cache buster
i18n_file = "/home/opc/posthog-deployment/i18n/posthog-i18n.js"
with open(i18n_file, "r", encoding="utf-8") as f:
    i18n_content = f.read()

# Kiểm tra nếu chưa có Computed regex
if "const computedMatch" not in i18n_content:
    computed_regex_block = """
            // 4b. Đã tính toán lần cuối: "Computed 2 hours ago", "Computed 2 giờ trước", "Computed a few seconds ago"
            const computedMatch = norm.match(/^Computed\\s*(.*)$/i);
            if (computedMatch) {
                const rest = computedMatch[1].trim();
                const restTrans = lookupDict(rest, 'vi') || rest;
                let timeStr = restTrans;
                if (restTrans === rest) {
                    timeStr = rest.replace(/a few seconds ago/i, 'vài giây trước')
                                  .replace(/just now/i, 'vừa xong')
                                  .replace(/an? hour ago/i, '1 giờ trước')
                                  .replace(/(\\d+)\\s+hours?\\s+ago/i, '$1 giờ trước')
                                  .replace(/(\\d+)\\s+days?\\s+ago/i, '$1 ngày trước')
                                  .replace(/(\\d+)\\s+minutes?\\s+ago/i, '$1 phút trước');
                }
                return 'Đã tính toán ' + timeStr;
            }
"""
    # Chèn ngay sau refreshMatch block
    i18n_content = i18n_content.replace(
        "return 'Làm mới lần cuối ' + (restTrans === rest && rest.includes('ago') ? rest.replace('a few seconds ago', 'vài giây trước').replace('an hour ago', '1 giờ trước') : restTrans);\n            }",
        "return 'Làm mới lần cuối ' + (restTrans === rest && rest.includes('ago') ? rest.replace('a few seconds ago', 'vài giây trước').replace('an hour ago', '1 giờ trước') : restTrans);\n            }" + computed_regex_block
    )

# Cập nhật cache buster trong fetch
i18n_content = re.sub(r"fetch\(`/static/locales/\$\{code\}\.json.*?\`\)", f"fetch(`/static/locales/${{code}}.json?v={VERSION}`)", i18n_content)

with open(i18n_file, "w", encoding="utf-8") as f:
    f.write(i18n_content)

# 3. Cập nhật head.html với cache buster mới
head_file = "/home/opc/posthog-deployment/custom_templates/head.html"
with open(head_file, "r", encoding="utf-8") as f:
    head_content = f.read()

head_content = re.sub(r"posthog-i18n\.css\?v=[^\"]+", f"posthog-i18n.css?v={VERSION}", head_content)
head_content = re.sub(r"locales/en\.js\?v=[^\"]+", f"locales/en.js?v={VERSION}", head_content)
head_content = re.sub(r"locales/vi\.js\?v=[^\"]+", f"locales/vi.js?v={VERSION}", head_content)
head_content = re.sub(r"posthog-i18n\.js\?v=[^\"]+", f"posthog-i18n.js?v={VERSION}", head_content)

with open(head_file, "w", encoding="utf-8") as f:
    f.write(head_content)

print(f"Toàn bộ hệ thống i18n đã được nâng cấp lên phiên bản: {VERSION}")
print("Tổng số từ vựng trong vi.json hiện tại:", len(vi_data))
