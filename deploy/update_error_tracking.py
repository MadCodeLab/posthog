import json
import re

VERSION = "20260908_1502"

error_tracking_vocab = {
    # Error Tracking Scene
    "No issues found": "Không tìm thấy sự cố nào",
    "Try changing the date range, changing the filters or removing the assignee.": "Hãy thử thay đổi khoảng thời gian, điều chỉnh bộ lọc hoặc bỏ chọn người được phân công.",
    "No issues match the specified filters": "Không có sự cố nào khớp với các bộ lọc đã chọn",
    "volume": "Khối lượng",
    "Volume": "Khối lượng",
    "occurrences": "Số lần xuất hiện",
    "Occurrences": "Số lần xuất hiện",
    "occurrence": "lần xuất hiện",
    "sessions": "phiên",
    "Sessions": "Phiên người dùng",
    "users": "người dùng",
    "Users": "Người dùng",
    "issue": "sự cố",
    "issues": "các sự cố",
    "Issues": "Các sự cố",
    "Assign": "Phân công",
    "Assignee": "Người được phân công",
    "assignee": "người được phân công",
    "Unassign": "Hủy phân công",
    "All statuses": "Tất cả trạng thái",
    "Status": "Trạng thái",
    "status": "trạng thái",
    "active": "Đang hoạt động",
    "resolved": "Đã giải quyết",
    "suppressed": "Đã ẩn",
    "mixed": "Hỗn hợp",
    "Mark as": "Đánh dấu là",
    "Merge": "Hợp nhất",
    "Merge Issues": "Hợp nhất các sự cố",
    "Select at least two issues to merge": "Chọn ít nhất hai sự cố để hợp nhất",
    "Hide from search": "Ẩn khỏi tìm kiếm",
    "Configure quick filters": "Cấu hình bộ lọc nhanh",
    "Sort by": "Sắp xếp theo",
    "Sort order": "Thứ tự sắp xếp",
    "Direction": "Chiều sắp xếp",
    "Descending": "Giảm dần",
    "Ascending": "Tăng dần",
    "Cancel issue reload": "Hủy tải lại danh sách sự cố",
    "Reload issues": "Tải lại danh sách sự cố",
    "Unnamed issue": "Sự cố chưa đặt tên",
    "Load more issues": "Tải thêm sự cố",
    "Open in Error tracking": "Mở trong phần Theo dõi lỗi",
    "Error tracking data unavailable": "Dữ liệu theo dõi lỗi không khả dụng",
    "The error tracking search could not be completed": "Không thể hoàn tất tìm kiếm theo dõi lỗi",
    "First seen": "Xuất hiện lần đầu",
    "Last seen": "Xuất hiện lần cuối",
    "Open all": "Mở tất cả",
    "Any assignee": "Bất kỳ người phân công nào",
    "Any status": "Bất kỳ trạng thái nào",
    "Internal accounts": "Tài khoản nội bộ",
    "Filter test accounts": "Lọc tài khoản thử nghiệm",
    "Severity": "Mức độ nghiêm trọng",
    "Quick filters": "Bộ lọc nhanh",
    "No $session_id was set for any event in this issue": "Không có $session_id nào được đặt cho sự kiện trong sự cố này"
}

vi_path = "/home/opc/posthog-deployment/i18n/locales/vi.json"
en_path = "/home/opc/posthog-deployment/i18n/locales/en.json"

with open(vi_path, "r", encoding="utf-8") as f:
    vi_data = json.load(f)

with open(en_path, "r", encoding="utf-8") as f:
    en_data = json.load(f)

count = 0
for k, v in error_tracking_vocab.items():
    if k not in vi_data or vi_data[k] != v:
        vi_data[k] = v
        en_data[k] = k
        count += 1

print(f"Đã thêm/cập nhật {count} từ vựng cho Error Tracking")

with open(vi_path, "w", encoding="utf-8") as f:
    json.dump(vi_data, f, ensure_ascii=False, indent=2)

with open(en_path, "w", encoding="utf-8") as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

with open("/home/opc/posthog-deployment/i18n/locales/vi.js", "w", encoding="utf-8") as f:
    f.write("window.__POSTHOG_I18N_VI__ = " + json.dumps(vi_data, ensure_ascii=False, indent=2) + ";\nif (window.PostHogI18n && window.PostHogI18n.registerLocale) { window.PostHogI18n.registerLocale(\"vi\", window.__POSTHOG_I18N_VI__); }\n")

with open("/home/opc/posthog-deployment/i18n/locales/en.js", "w", encoding="utf-8") as f:
    f.write("window.__POSTHOG_I18N_EN__ = " + json.dumps(en_data, ensure_ascii=False, indent=2) + ";\nif (window.PostHogI18n && window.PostHogI18n.registerLocale) { window.PostHogI18n.registerLocale(\"en\", window.__POSTHOG_I18N_EN__); }\n")

# Cập nhật cache buster trong head.html
head_path = "/home/opc/posthog-deployment/custom_templates/head.html"
with open(head_path, "r", encoding="utf-8") as f:
    head_content = f.read()

head_content = re.sub(r"posthog-i18n\.css\?v=[^\"]+", f"posthog-i18n.css?v={VERSION}", head_content)
head_content = re.sub(r"locales/en\.js\?v=[^\"]+", f"locales/en.js?v={VERSION}", head_content)
head_content = re.sub(r"locales/vi\.js\?v=[^\"]+", f"locales/vi.js?v={VERSION}", head_content)
head_content = re.sub(r"posthog-i18n\.js\?v=[^\"]+", f"posthog-i18n.js?v={VERSION}", head_content)

with open(head_path, "w", encoding="utf-8") as f:
    f.write(head_content)

# Cập nhật posthog-i18n.js để fetch có cache buster
i18n_path = "/home/opc/posthog-deployment/i18n/posthog-i18n.js"
with open(i18n_path, "r", encoding="utf-8") as f:
    i18n_content = f.read()

i18n_content = re.sub(r"fetch\(`/static/locales/\$\{code\}\.json.*?\`\)", f"fetch(`/static/locales/${{code}}.json?v={VERSION}`)", i18n_content)

with open(i18n_path, "w", encoding="utf-8") as f:
    f.write(i18n_content)

print(f"Hoàn tất cập nhật phiên bản {VERSION}!")
print("Tổng số từ vựng trong vi.json:", len(vi_data))
