import json
import re

new_translations = {
    # Project Homepage & Max AI Header / Prompts
    "What can I help you with?": "Tôi có thể giúp gì cho bạn?",
    "/ for commands": "/ để xem lệnh",
    "or / for commands": "hoặc / để xem lệnh",
    "Tab to search": "Nhấn Tab để tìm kiếm",
    "Ask PostHog AI": "Hỏi PostHog AI",
    "ASK POSTHOG AI": "HỎI POSTHOG AI",
    "PINNED DASHBOARDS": "BẢNG ĐIỀU KHIỂN ĐÃ GHIM",
    "Pinned dashboards": "Bảng điều khiển đã ghim",
    "Your starter dashboard": "Bảng điều khiển khởi đầu của bạn",
    "Learn": "Tài liệu hướng dẫn",
    "manage AI settings.": "quản lý cài đặt AI.",
    "manage AI settings": "quản lý cài đặt AI",
    "PostHog AI uses third-party LLM providers (Alphabet, Anthropic, Microsoft, and OpenAI). Your data will not be used for training third-party models. If you'd rather disable this feature,": "PostHog AI sử dụng các nhà cung cấp LLM bên thứ ba (Alphabet, Anthropic, Microsoft và OpenAI). Dữ liệu của bạn sẽ không bị dùng để huấn luyện mô hình bên thứ ba. Nếu bạn muốn tắt tính năng này,",
    "PostHog AI uses third-party LLM providers": "PostHog AI sử dụng các nhà cung cấp LLM bên thứ ba",

    # Max AI Suggestions & Categories
    "Run a funnel analysis": "Phân tích phễu chuyển đổi",
    "Conversion and drop-off across the Pirate Metrics (AARRR)": "Tỷ lệ chuyển đổi và rời bỏ theo mô hình Pirate Metrics (AARRR)",
    "Check retention": "Kiểm tra tỷ lệ giữ chân người dùng",
    "How many users came back over the last two weeks": "Có bao nhiêu người dùng quay lại trong 2 tuần qua",
    "Find popular pages": "Tìm các trang phổ biến nhất",
    "Your most visited pages and screens": "Các trang và màn hình được truy cập nhiều nhất",
    "See top referrers": "Xem nguồn giới thiệu hàng đầu",
    "Where your traffic is coming from": "Lưu lượng truy cập của bạn đến từ đâu",
    "Write a SQL query": "Viết câu truy vấn SQL",
    "Query any of your data with HogQL": "Truy vấn bất kỳ dữ liệu nào của bạn bằng HogQL",
    "Explore your warehouse": "Khám phá kho dữ liệu của bạn",
    "Query your synced external data sources": "Truy vấn các nguồn dữ liệu bên ngoài đã đồng bộ",
    "Find your top events": "Tìm các sự kiện hàng đầu của bạn",
    "Your most frequent events this week": "Các sự kiện diễn ra nhiều nhất trong tuần này",
    "Count active users": "Đếm số lượng người dùng hoạt động",
    "Weekly active users with SQL": "Số người dùng hoạt động hàng tuần (WAU) bằng SQL",
    "Find recordings": "Tìm kiếm bản ghi phiên",
    "Filter replays by user or action": "Lọc video xem lại theo người dùng hoặc hành động",
    "Summarize sessions": "Tóm tắt các phiên người dùng",
    "What happened across recent replays": "Những gì đã diễn ra trong các bản ghi gần đây",
    "Spot friction": "Phát hiện điểm khó khăn/ức chế",
    "Rage-clicks, dead-clicks, and confusion": "Nhấp chuột tức giận (rage click), nhấp chuột chết và sự nhầm lẫn",
    "Watch error sessions": "Xem các phiên gặp lỗi",
    "Replays where users hit an error": "Video xem lại của những người dùng gặp lỗi",
    "Find impactful errors": "Tìm các lỗi nghiêm trọng nhất",
    "The exceptions hitting the most users": "Các lỗi ngoại lệ ảnh hưởng đến nhiều người dùng nhất",
    "Triage new issues": "Phân loại các vấn đề mới",
    "Errors first seen this week": "Các lỗi xuất hiện lần đầu trong tuần này",
    "Explain an error": "Giải thích một lỗi",
    "Likely cause and where it fires": "Nguyên nhân có thể xảy ra và vị trí phát sinh lỗi",
    "See error replays": "Xem video các phiên gặp lỗi",
    "Roll out a feature": "Triển khai một tính năng",
    "Gradually release a feature behind a flag": "Phát hành dần dần một tính năng qua cờ tính năng",
    "Create a multivariate flag": "Tạo cờ tính năng đa biến",
    "Test several variants of a feature": "Thử nghiệm nhiều biến thể khác nhau của một tính năng",
    "Audit your flags": "Kiểm tra toàn bộ cờ tính năng",
    "Find stale or risky feature flags": "Tìm các cờ tính năng cũ hoặc có rủi ro",
    "Review flag usage": "Xem lại mức độ sử dụng cờ tính năng",
    "Which flags are still being evaluated": "Những cờ tính năng nào vẫn đang được đánh giá",
    "Design an A/B test": "Thiết kế một thử nghiệm A/B",
    "Set up an experiment to test a change": "Thiết lập một thử nghiệm để đánh giá một thay đổi",
    "Review a running test": "Đánh giá một thử nghiệm đang chạy",
    "Check your experiments are set up correctly": "Kiểm tra xem các thử nghiệm của bạn đã thiết lập đúng chưa",
    "Interpret results": "Phân tích và diễn giải kết quả",
    "Significance and what to do next": "Mức độ ý nghĩa thống kê và các bước tiếp theo",
    "Size an experiment": "Tính toán quy mô thử nghiệm",
    "How long it needs to run for significance": "Thời gian cần chạy để đạt mức ý nghĩa thống kê",
    "Launch an NPS survey": "Tạo khảo sát đo lường NPS",
    "Collect Net Promoter Score from your users": "Thu thập chỉ số Net Promoter Score từ người dùng",
    "Run a CSAT survey": "Tạo khảo sát mức độ hài lòng CSAT",
    "Measure customer satisfaction": "Đo lường mức độ hài lòng của khách hàng",
    "Measure product-market fit": "Đo lường mức độ phù hợp sản phẩm - thị trường (PMF)",
    "Ask how users would feel without your product": "Hỏi xem người dùng sẽ cảm thấy thế nào nếu không còn sản phẩm của bạn",
    "Analyze survey responses": "Phân tích câu trả lời khảo sát",
    "Surface themes to prioritize what to build": "Tổng hợp các chủ đề nổi bật để ưu tiên tính năng cần phát triển",
    "Create a feature flag": "Tạo cờ tính năng",
    "How flags work and how to set one up": "Tìm hiểu cách cờ tính năng hoạt động và cách thiết lập",
    "Watch session replays": "Xem lại bản ghi phiên",
    "Where to find recordings of real user sessions": "Nơi tìm các bản ghi phiên hoạt động thực tế của người dùng",
    "Set up an experiment": "Thiết lập thử nghiệm A/B",
    "Get help configuring your first A/B test": "Nhận trợ giúp cấu hình thử nghiệm A/B đầu tiên của bạn",
    "Understand autocapture": "Tìm hiểu về tính năng tự động thu thập (Autocapture)",
    "What events PostHog collects automatically": "Những sự kiện nào PostHog tự động thu thập",
    "Capture exceptions": "Thu thập các lỗi ngoại lệ",
    "Send errors to error tracking": "Gửi thông tin lỗi đến tính năng Theo dõi lỗi",

    # Chat Bar & Thread UI
    "Ask a question": "Đặt một câu hỏi",
    "Ask follow-up": "Đặt câu hỏi tiếp theo",
    "Thinking…": "Đang suy nghĩ…",
    "This thread was shared with you by": "Cuộc trò chuyện này được chia sẻ với bạn bởi",
    "Research mode is a free beta feature with lower daily limits": "Chế độ nghiên cứu là tính năng beta miễn phí với giới hạn hàng ngày thấp hơn",
    "Up next": "Tiếp theo",
    "Save": "Lưu",
    "Cancel": "Hủy",
    "Edit message": "Chỉnh sửa tin nhắn",
    "Remove from queue": "Xóa khỏi hàng đợi",
    "Message cannot be empty": "Tin nhắn không được để trống",
    "I need some input first": "Vui lòng nhập nội dung trước",
    "Cancelling...": "Đang hủy...",
    "Please accept AI data processing": "Vui lòng chấp nhận xử lý dữ liệu AI",

    # Error Panel (khi chưa setup)
    "PostHog AI isn't set up yet": "PostHog AI chưa được thiết lập",
    "PostHog AI runs on your own LLM provider key. Set": "PostHog AI chạy bằng khóa nhà cung cấp LLM của riêng bạn. Thiết lập",
    "for this instance and restart PostHog to start chatting.": "cho phiên bản này và khởi động lại PostHog để bắt đầu trò chuyện.",
    "On a hobby deploy, add the key to your .env file and run ./bin/upgrade-hobby, or set it during install.": "Trên bản triển khai cá nhân (hobby), hãy thêm khóa vào tệp .env của bạn và khởi động lại PostHog.",
    "Configuring environment variables": "Cấu hình các biến môi trường"
}

# 1. Update vi.json
json_path = "/home/opc/posthog-deployment/i18n/locales/vi.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for k, v in new_translations.items():
    data[k] = v

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✓ Updated vi.json (total keys: {len(data)})")

# 2. Update vi.js
js_path = "/home/opc/posthog-deployment/i18n/locales/vi.js"
js_content = f"""(function() {{
    window.__POSTHOG_I18N_LOCALES__ = window.__POSTHOG_I18N_LOCALES__ || {{}};
    window.__POSTHOG_I18N_LOCALES__['vi'] = {json.dumps(data, ensure_ascii=False, indent=2)};
}})();
"""
with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print("✓ Updated vi.js")

# 3. Update posthog-i18n.js to support dynamic patterns like "Hello {name}" and "What can I help you with?"
i18n_engine_path = "/home/opc/posthog-deployment/i18n/posthog-i18n.js"
with open(i18n_engine_path, "r", encoding="utf-8") as f:
    engine_code = f.read()

# Pattern addition in translateText:
pattern_target = 'const translated = currentDict[trimmed];'
pattern_injection = '''const translated = currentDict[trimmed];
        if (translated) return translated;

        // Dynamic patterns: "Hello {Name}" -> "Xin chào {Name}"
        if (currentLang === 'vi') {
            const helloMatch = trimmed.match(/^Hello\\s+([A-Za-z0-9_\\s\\p{L}]+)$/u);
            if (helloMatch) {
                return 'Xin chào ' + helloMatch[1];
            }
            if (trimmed.startsWith('What can I help you with?')) {
                return trimmed.replace('What can I help you with?', 'Tôi có thể giúp gì cho bạn?').replace('/ for commands', '/ để xem lệnh');
            }
        }'''

if pattern_target in engine_code and 'helloMatch' not in engine_code:
    engine_code = engine_code.replace(pattern_target, pattern_injection, 1)
    with open(i18n_engine_path, "w", encoding="utf-8") as f:
        f.write(engine_code)
    print("✓ Updated posthog-i18n.js with dynamic pattern translation (Hello {name})")
else:
    print("Dynamic pattern already present or target not found in posthog-i18n.js")

# 4. Bump Cache Buster in head.html
head_path = "/home/opc/posthog-deployment/custom_templates/head.html"
with open(head_path, "r", encoding="utf-8") as f:
    head_code = f.read()

new_version = "20260908_1215"
head_code = re.sub(r'v=\d{8}_\d{4}', f'v={new_version}', head_code)
with open(head_path, "w", encoding="utf-8") as f:
    f.write(head_code)
print(f"✓ Bumped cache buster in head.html to v={new_version}")

