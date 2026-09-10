import json
import re

vi_path = '/home/opc/posthog-deployment/i18n/locales/vi.json'
vi_js_path = '/home/opc/posthog-deployment/i18n/locales/vi.js'
en_path = '/home/opc/posthog-deployment/i18n/locales/en.json'
en_js_path = '/home/opc/posthog-deployment/i18n/locales/en.js'
i18n_js_path = '/home/opc/posthog-deployment/i18n/posthog-i18n.js'
head_html_path = '/home/opc/posthog-deployment/custom_templates/head.html'

with open(vi_path, 'r', encoding='utf-8') as f:
    vi_data = json.load(f)

with open(en_path, 'r', encoding='utf-8') as f:
    en_data = json.load(f)

all_new_terms = {
    # -------------------------------------------------------------
    # 1. STARTER DASHBOARD & DEFAULT TILES
    # -------------------------------------------------------------
    "👋 Start here": "👋 Bắt đầu tại đây",
    "Start here": "Bắt đầu tại đây",
    "Everything below is captured automatically (pageviews, clicks, sessions, and location), so this dashboard fills in from day one with no extra setup. The headline numbers will feel familiar; the retention and funnel tiles are where you point PostHog at your own events. Edit any tile, or duplicate the dashboard to make it your own.": "Mọi thứ dưới đây được thu thập tự động (lượt xem trang, nhấp chuột, phiên và vị trí), vì vậy bảng điều khiển này có dữ liệu ngay từ ngày đầu tiên mà không cần thiết lập thêm. Các con số chính sẽ rất quen thuộc; các ô tỷ lệ giữ chân và phễu là nơi bạn liên kết PostHog với các sự kiện của riêng mình. Chỉnh sửa bất kỳ ô nào hoặc nhân bản bảng điều khiển để tùy biến theo nhu cầu.",
    "Active users (last 30 days)": "Người dùng hoạt động (30 ngày qua)",
    "Unique people who used your app in the last 30 days. A quick pulse on your overall reach.": "Số người dùng duy nhất đã sử dụng ứng dụng của bạn trong 30 ngày qua. Nhịp đo nhanh về phạm vi tiếp cận tổng thể.",
    "Sessions (last 7 days)": "Số phiên (7 ngày qua)",
    "Distinct visits in the last 7 days. A session groups everything one person does in a single sitting.": "Các lượt truy cập riêng biệt trong 7 ngày qua. Một phiên gom nhóm toàn bộ hoạt động của một người trong một lần truy cập.",
    "Pageviews (last 7 days)": "Lượt xem trang (7 ngày qua)",
    "Total pages viewed in the last 7 days, repeat views included. The classic traffic-volume number.": "Tổng số trang đã xem trong 7 ngày qua, bao gồm cả các lượt xem lặp lại. Chỉ số lưu lượng truy cập kinh điển.",
    "Are people coming back?": "Người dùng có quay lại không?",
    "Active users show your trend; retention shows how many return after their first visit. The clearest sign your product is sticky.": "Người dùng hoạt động thể hiện xu hướng; tỷ lệ giữ chân cho biết có bao nhiêu người quay lại sau lần truy cập đầu tiên. Dấu hiệu rõ ràng nhất cho thấy sản phẩm của bạn có sức gắn kết cao.",
    "Daily active users (DAUs)": "Người dùng hoạt động hàng ngày (DAU)",
    "Unique people who use your app each day. Watch for steady growth or sudden drops.": "Số người dùng duy nhất sử dụng ứng dụng của bạn mỗi ngày. Theo dõi sự tăng trưởng đều đặn hoặc sụt giảm bất thường.",
    "Weekly active users (WAUs)": "Người dùng hoạt động hàng tuần (WAU)",
    "Unique people who use your app each week. Smooths out daily noise to show the underlying trend.": "Số người dùng duy nhất sử dụng ứng dụng mỗi tuần. Giảm thiểu biến động hàng ngày để thể hiện xu hướng cốt lõi.",
    "How many people come back week after week after their first visit. The clearest signal of whether your product is sticky.": "Có bao nhiêu người quay lại tuần này qua tuần khác sau lần truy cập đầu tiên. Tín hiệu rõ ràng nhất xem sản phẩm của bạn có giữ chân được người dùng hay không.",
    "Where your visitors come from": "Khách truy cập đến từ đâu",
    "The sites and channels sending people to your app.": "Các trang web và kênh giới thiệu người dùng đến ứng dụng của bạn.",
    "Which sites send you the most visitors, like search, social, and direct. Your acquisition channels at a glance.": "Những trang web mang lại nhiều khách truy cập nhất, như tìm kiếm, mạng xã hội và trực tiếp. Tổng quan nhanh các kênh thu hút người dùng.",
    "Turning visits into actions": "Biến lượt truy cập thành hành động",
    "A funnel from page view to click. Swap in your own events (signup, purchase, upgrade) to measure real conversion.": "Một phễu chuyển đổi từ lượt xem trang đến lượt nhấp. Thay thế bằng các sự kiện của riêng bạn (đăng ký, mua hàng, nâng cấp) để đo lường chuyển đổi thực tế.",
    "Visit to interaction funnel": "Phễu từ truy cập đến tương tác",
    "Of people who land on a page, how many go on to interact. Replace these steps with your own events to track real conversions.": "Trong số người dùng truy cập trang, có bao nhiêu người tiếp tục tương tác. Thay thế các bước này bằng sự kiện của riêng bạn để theo dõi chuyển đổi thực tế.",
    "There are no matching events for this query": "Không có sự kiện nào khớp với truy vấn này",
    "Try changing the date range, or pick another action, event or breakdown.": "Hãy thử đổi khoảng thời gian, hoặc chọn hành động, sự kiện hay phân tích khác.",
    "What to do next": "Các bước tiếp theo",
    "You've got the numbers. Watch how people actually behave, explore raw events, or dig into traffic and acquisition.": "Bạn đã có các con số. Giờ hãy xem cách người dùng thực sự hành động, khám phá các sự kiện thô hoặc đi sâu vào lưu lượng và nguồn thu hút.",
    "How people use your app at a glance: traffic, retention, where visitors come from, and whether they take action. Built from automatically captured events, so it works on day one. Swap in your own events to make it yours.": "Tổng quan cách người dùng sử dụng ứng dụng: lưu lượng, tỷ lệ giữ chân, nguồn truy cập và các hành động họ thực hiện. Xây dựng từ sự kiện tự động thu thập, sẵn sàng hoạt động ngay ngày đầu. Thay thế bằng sự kiện của bạn để tùy biến.",

    # -------------------------------------------------------------
    # 2. INSIGHTS SCENE & AI OBSERVABILITY INSIGHTS
    # -------------------------------------------------------------
    "Track, analyze, and experiment with user behavior.": "Theo dõi, phân tích và thử nghiệm hành vi của người dùng.",
    "All insights": "Tất cả thông tin chi tiết",
    "My insights": "Thông tin chi tiết của tôi",
    "Last viewed": "Xem lần cuối",
    "Generations by HTTP status": "Lượt tạo theo trạng thái HTTP",
    "Generation latency by model (median)": "Độ trễ sinh nội dung theo mô hình (trung vị)",
    "AI Errors": "Lỗi AI",
    "Failed AI generation calls": "Các lệnh gọi sinh AI thất bại",
    "AI ErrorsFailed AI generation calls": "Lỗi AI: Các lệnh gọi sinh AI thất bại",
    "Generation calls": "Lệnh gọi sinh nội dung",
    "Cost by model (USD)": "Chi phí theo mô hình (USD)",
    "Cost per user (USD)": "Chi phí trên mỗi người dùng (USD)",
    "Cost per user (USD)Average cost for each generative AI user active in the data point's period.": "Chi phí trên mỗi người dùng (USD): Chi phí trung bình cho mỗi người dùng Generative AI hoạt động trong kỳ.",
    "Average cost for each generative AI user active in the data point's period.": "Chi phí trung bình cho mỗi người dùng Generative AI hoạt động trong kỳ.",
    "Total cost (USD)": "Tổng chi phí (USD)",
    "Generative AI users": "Người dùng Generative AI",
    "Generative AI usersTo count users, set distinct_id in LLM tracking.": "Người dùng Generative AI: Để đếm người dùng, hãy thiết lập distinct_id trong theo dõi LLM.",
    "To count users, set distinct_id in LLM tracking.": "Để đếm người dùng, hãy thiết lập distinct_id trong theo dõi LLM.",
    "Visit to interaction funnelOf people who land on a page, how many go on to interact. Replace these steps with your own events to track real conversions.": "Phễu từ truy cập đến tương tác: Trong số người dùng truy cập trang, có bao nhiêu người tiếp tục tương tác. Thay thế bằng sự kiện của bạn để đo lường chuyển đổi.",
    "Nguồn giới thiệu hàng đầuWhich sites send you the most visitors, like search, social, and direct. Your acquisition channels at a glance.": "Nguồn giới thiệu hàng đầu: Những trang web mang lại nhiều khách truy cập nhất. Tổng quan nhanh các kênh thu hút.",
    "Tỷ lệ giữ chânHow many people come back week after week after their first visit. The clearest signal of whether your product is sticky.": "Tỷ lệ giữ chân: Bao nhiêu người quay lại tuần này qua tuần khác sau lần truy cập đầu tiên. Dấu hiệu rõ ràng nhất về sự gắn kết của sản phẩm.",
    "Weekly active users (WAUs)Unique people who use your app each week. Smooths out daily noise to show the underlying trend.": "Người dùng hoạt động hàng tuần (WAU): Số người dùng duy nhất mỗi tuần. Thể hiện xu hướng cốt lõi.",
    "Daily active users (DAUs)Unique people who use your app each day. Watch for steady growth or sudden drops.": "Người dùng hoạt động hàng ngày (DAU): Số người dùng duy nhất mỗi ngày. Theo dõi tăng trưởng hoặc sụt giảm.",
    "Pageviews (last 7 days)Total pages viewed in the last 7 days, repeat views included. The classic traffic-volume number.": "Lượt xem trang (7 ngày qua): Tổng số trang đã xem trong 7 ngày qua. Chỉ số lưu lượng kinh điển.",
    "Sessions (last 7 days)Distinct visits in the last 7 days. A session groups everything one person does in a single sitting.": "Số phiên (7 ngày qua): Các lượt truy cập riêng biệt trong 7 ngày qua.",
    "Active users (last 30 days)Unique people who used your app in the last 30 days. A quick pulse on your overall reach.": "Người dùng hoạt động (30 ngày qua): Số người dùng duy nhất trong 30 ngày qua.",

    # -------------------------------------------------------------
    # 3. WEB ANALYTICS SCENE
    # -------------------------------------------------------------
    "Analyze your web analytics data to understand website performance and user behavior.": "Phân tích dữ liệu web analytics để hiểu rõ hiệu suất trang web và hành vi của người dùng.",
    "Web vitals": "Chỉ số Web Vitals",
    "Page reports": "Báo cáo trang",
    "Installation Health": "Tình trạng cài đặt",
    "Customize channel types": "Tùy chỉnh loại kênh",
    "Channel Type": "Loại kênh",
    "Device Type": "Loại thiết bị",
    "Device type": "Loại thiết bị",
    "Unknown": "Không xác định",
    "Path": "Đường dẫn",
    "Size": "Quy mô",
    "Mean": "Trung bình",
    "Active Hours": "Giờ hoạt động",
    "Data shown in timezone: UTC (UTC±0:00)": "Dữ liệu hiển thị theo múi giờ: UTC (UTC±0:00)",
    "Track your conversions": "Theo dõi chuyển đổi của bạn",
    "Goals show how many visitors complete the actions that matter to you. Sign-ups, purchases, demo requests. Create an action for a key conversion to see its visitors and conversion rate here.": "Mục tiêu cho biết có bao nhiêu khách hoàn thành hành động quan trọng (đăng ký, mua hàng, yêu cầu demo). Tạo hành động cho chuyển đổi chính để xem khách truy cập và tỷ lệ chuyển đổi tại đây.",
    "Frustrating Pages": "Trang gây ức chế",
    "Rage Clicks": "Nhấp chuột giận dữ (Rage Clicks)",
    "Dead Clicks": "Nhấp chuột vô hiệu (Dead Clicks)",
    "No frustrating pages found! Keep up the great work!": "Không tìm thấy trang gây ức chế nào! Hãy tiếp tục duy trì nhé!",

    # -------------------------------------------------------------
    # 4. RECURRING LABELS & TIME PHRASES
    # -------------------------------------------------------------
    "grouped by": "nhóm theo",
    "Last refreshed": "Làm mới lần cuối",
    "a few seconds ago": "vài giây trước",
    "an hour ago": "1 giờ trước",
    "a minute ago": "1 phút trước",
    "just now": "vừa xong",
    "very low": "rất thấp",
    "low": "thấp",
    "medium": "trung bình",
    "high": "cao",
    "very high": "rất cao",
    "vs. 0 prior": "so với 0 trước đó",
    "Week 0": "Tuần 0",
    "Week 1": "Tuần 1",
    "Week 2": "Tuần 2",
    "Week 3": "Tuần 3",
    "Week 4": "Tuần 4"
}

# 1. Đồng bộ vào JSON
for k, v in all_new_terms.items():
    vi_data[k] = v
    if k not in en_data:
        en_data[k] = k

with open(vi_path, 'w', encoding='utf-8') as f:
    json.dump(vi_data, f, ensure_ascii=False, indent=2)

with open(vi_js_path, 'w', encoding='utf-8') as f:
    f.write('window.__POSTHOG_I18N_LOCALES__ = window.__POSTHOG_I18N_LOCALES__ || {};\n')
    f.write('window.__POSTHOG_I18N_LOCALES__["vi"] = ' + json.dumps(vi_data, ensure_ascii=False, indent=2) + ';\n')

with open(en_path, 'w', encoding='utf-8') as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

with open(en_js_path, 'w', encoding='utf-8') as f:
    f.write('window.__POSTHOG_I18N_LOCALES__ = window.__POSTHOG_I18N_LOCALES__ || {};\n')
    f.write('window.__POSTHOG_I18N_LOCALES__["en"] = ' + json.dumps(en_data, ensure_ascii=False, indent=2) + ';\n')

print(f"1. Locales updated! Total entries: {len(vi_data)}")

# 2. Cập nhật posthog-i18n.js với bộ quy tắc regex đa năng
with open(i18n_js_path, 'r', encoding='utf-8') as f:
    i18n_code = f.read()

# Chèn hàm regex xử lý động toàn diện cho tiếng Việt
dyn_rules = """
        // Bộ quy tắc dịch động thông minh đa năng cho Tiếng Việt
        if (lang === 'vi') {
            // 1. Chào mừng
            const helloMatch = norm.match(/^Hello\\s+(.+)$/i);
            if (helloMatch) {
                const name = helloMatch[1].trim();
                return 'Xin chào ' + (name.toLowerCase() === 'there' ? 'bạn' : name);
            }
            if (norm.startsWith('What can I help you with?')) {
                return norm.replace('What can I help you with?', 'Tôi có thể giúp gì cho bạn?').replace('/ for commands', '/ để xem lệnh');
            }

            // 2. Thời gian tương đối: "a few seconds ago", "an hour ago", "12 hours ago", "2 days ago"
            if (/^a few seconds ago$/i.test(norm)) return 'vài giây trước';
            if (/^just now$/i.test(norm)) return 'vừa xong';
            if (/^an? minute ago$/i.test(norm)) return '1 phút trước';
            if (/^an? hour ago$/i.test(norm)) return '1 giờ trước';
            if (/^an? day ago$/i.test(norm)) return '1 ngày trước';
            if (/^an? week ago$/i.test(norm)) return '1 tuần trước';
            if (/^an? month ago$/i.test(norm)) return '1 tháng trước';
            if (/^an? year ago$/i.test(norm)) return '1 năm trước';

            const agoMatch = norm.match(/^(\\d+)\\s+(second|minute|hour|day|week|month|year)s?\\s+ago$/i);
            if (agoMatch) {
                const num = agoMatch[1];
                const unit = agoMatch[2].toLowerCase();
                let unitVi = 'ngày';
                if (unit.startsWith('sec')) unitVi = 'giây';
                else if (unit.startsWith('min')) unitVi = 'phút';
                else if (unit.startsWith('hour')) unitVi = 'giờ';
                else if (unit.startsWith('day')) unitVi = 'ngày';
                else if (unit.startsWith('week')) unitVi = 'tuần';
                else if (unit.startsWith('month')) unitVi = 'tháng';
                else if (unit.startsWith('year')) unitVi = 'năm';
                return num + ' ' + unitVi + ' trước';
            }

            // 3. Thời lượng hiển thị: "2m 58s", "10s", "5m"
            const durationMatch = norm.match(/^(\\d+)m\\s*(\\d+)s$/i);
            if (durationMatch) {
                return durationMatch[1] + 'm ' + durationMatch[2] + 's';
            }

            // 4. Làm mới lần cuối: "Last refreshed a few seconds ago", "Last refreshed 5 minutes ago"
            const refreshMatch = norm.match(/^Last refreshed\\s*(.*)$/i);
            if (refreshMatch) {
                const rest = refreshMatch[1].trim();
                const restTrans = lookupDict(rest, 'vi') || rest;
                return 'Làm mới lần cuối ' + (restTrans === rest && rest.includes('ago') ? rest.replace('a few seconds ago', 'vài giây trước').replace('an hour ago', '1 giờ trước') : restTrans);
            }

            // 5. So sánh với kỳ trước: "vs. 0 prior", "vs. 15 prior"
            const priorMatch = norm.match(/^vs\\.\\s*([\\d,]+)\\s+prior$/i);
            if (priorMatch) {
                return 'so với ' + priorMatch[1] + ' trước đó';
            }

            // 6. Nhóm theo: "grouped by"
            if (/^grouped by$/i.test(norm)) return 'nhóm theo';

            // 7. Tuần và Thứ
            const weekMatch = norm.match(/^Week\\s+(\\d+)$/i);
            if (weekMatch) return 'Tuần ' + weekMatch[1];

            const daysMap = { 'sun': 'CN', 'mon': 'T2', 'tue': 'T3', 'wed': 'T4', 'thu': 'T5', 'fri': 'T6', 'sat': 'T7' };
            if (daysMap[norm.toLowerCase()]) return daysMap[norm.toLowerCase()];

            // 8. Dải ngày tháng: "Aug 30 to Sep 5"
            const monthRangeMatch = norm.match(/^([a-zA-Z]{3})\\s+(\\d+)\\s+to\\s+([a-zA-Z]{3})\\s+(\\d+)$/i);
            if (monthRangeMatch) {
                const monthsMap = {
                    'jan': 'Th1', 'feb': 'Th2', 'mar': 'Th3', 'apr': 'Th4',
                    'may': 'Th5', 'jun': 'Th6', 'jul': 'Th7', 'aug': 'Th8',
                    'sep': 'Th9', 'oct': 'Th10', 'nov': 'Th11', 'dec': 'Th12'
                };
                const m1 = monthsMap[monthRangeMatch[1].toLowerCase()] || monthRangeMatch[1];
                const d1 = monthRangeMatch[2];
                const m2 = monthsMap[monthRangeMatch[3].toLowerCase()] || monthRangeMatch[3];
                const d2 = monthRangeMatch[4];
                return d1 + ' ' + m1 + ' đến ' + d2 + ' ' + m2;
            }

            // 9. Chuỗi số lượng bản ghi hoạt động gần đây
            const recentlyMatch = norm.match(/^(\\d+)\\s+recently active(?:\\s*(?:recordings?|Bản ghi phiên))?$/i);
            if (recentlyMatch) {
                return recentlyMatch[1] + ' bản ghi hoạt động gần đây';
            }
            if (/^recently active(?:\\s*(?:recordings?|Bản ghi phiên))?$/i.test(norm)) {
                return 'bản ghi hoạt động gần đây';
            }

            // 10. Chuỗi thời gian tương đối bộ lọc: "Last 3 days", "Last 24 hours"
            const lastTimeMatch = norm.match(/^Last\\s+(\\d+)\\s+(seconds?|minutes?|hours?|days?|weeks?|months?|years?)$/i);
            if (lastTimeMatch) {
                const num = lastTimeMatch[1];
                const unit = lastTimeMatch[2].toLowerCase();
                let unitVi = 'ngày';
                if (unit.startsWith('sec')) unitVi = 'giây';
                else if (unit.startsWith('min')) unitVi = 'phút';
                else if (unit.startsWith('hour')) unitVi = 'giờ';
                else if (unit.startsWith('day')) unitVi = 'ngày';
                else if (unit.startsWith('week')) unitVi = 'tuần';
                else if (unit.startsWith('month')) unitVi = 'tháng';
                else if (unit.startsWith('year')) unitVi = 'năm';
                return num + ' ' + unitVi + ' qua';
            }

            // 11. Chuỗi thời lượng hoạt động bộ lọc: "> 5 active seconds"
            const activeTimeMatch = norm.match(/^(>=?|<=?|>|<)\\s*(\\d+)\\s+active\\s+(seconds?|minutes?|hours?)$/i);
            if (activeTimeMatch) {
                const op = activeTimeMatch[1];
                const num = activeTimeMatch[2];
                const unit = activeTimeMatch[3].toLowerCase();
                const unitVi = unit.startsWith('sec') ? 'giây hoạt động' : (unit.startsWith('min') ? 'phút hoạt động' : 'giờ hoạt động');
                return op + ' ' + num + ' ' + unitVi;
            }

            // 12. Mức độ hoạt động: low, medium, very low, high
            const levelMap = { 'very low': 'rất thấp', 'low': 'thấp', 'medium': 'trung bình', 'high': 'cao', 'very high': 'rất cao' };
            if (levelMap[norm.toLowerCase()]) return levelMap[norm.toLowerCase()];
        }
"""

start_marker = "        // Khớp các chuỗi động đặc thù tiếng Việt\n        if (lang === 'vi') {"
end_marker = "        return null;\n    }\n\n    // Thay thế an toàn đúng vị trí chuỗi con"

if start_marker in i18n_code:
    s_idx = i18n_code.find(start_marker)
    e_idx = i18n_code.find(end_marker)
    if s_idx != -1 and e_idx != -1:
        new_i18n_code = i18n_code[:s_idx] + dyn_rules + "\n        " + i18n_code[e_idx:]
        with open(i18n_js_path, 'w', encoding='utf-8') as f:
            f.write(new_i18n_code)
        print("2. posthog-i18n.js dynamic rules successfully updated!")
    else:
        print("Error: Could not locate markers in posthog-i18n.js")
else:
    print("Error: start_marker not found in posthog-i18n.js")

# 3. Cập nhật cache buster trong head.html
with open(head_html_path, 'r', encoding='utf-8') as f:
    head_code = f.read()

head_code = re.sub(r'v=\d{8}_\d{4}', 'v=20260908_1400', head_code)
with open(head_html_path, 'w', encoding='utf-8') as f:
    f.write(head_code)

print("3. head.html updated with cache buster v=20260908_1400")
