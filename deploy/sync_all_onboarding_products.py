import json
import re

vi_path = '/home/opc/posthog-deployment/i18n/locales/vi.json'
vi_js_path = '/home/opc/posthog-deployment/i18n/locales/vi.js'
en_path = '/home/opc/posthog-deployment/i18n/locales/en.json'
en_js_path = '/home/opc/posthog-deployment/i18n/locales/en.js'
head_html_path = '/home/opc/posthog-deployment/custom_templates/head.html'

with open(vi_path, 'r', encoding='utf-8') as f:
    vi_data = json.load(f)

with open(en_path, 'r', encoding='utf-8') as f:
    en_data = json.load(f)

products_onboarding_terms = {
    # -------------------------------------------------------------
    # ERROR TRACKING
    # -------------------------------------------------------------
    "Track and analyze your error tracking data to understand and fix issues.": "Theo dõi và phân tích dữ liệu lỗi để hiểu và khắc phục sự cố nhanh chóng.",
    "Catch the errors your users actually hit": "Bắt trọn các lỗi mà người dùng của bạn thực sự gặp phải",
    "PostHog captures exceptions from your app and groups them into issues, with stack traces, affected users, and alerts. Triage, assign, and resolve them next to the rest of your product data.": "PostHog thu thập các ngoại lệ từ ứng dụng của bạn và gom nhóm thành sự cố, kèm theo vết ngăn xếp, người dùng bị ảnh hưởng và cảnh báo. Phân loại, chỉ định và giải quyết lỗi ngay bên cạnh dữ liệu sản phẩm của bạn.",
    "Already using posthog-js? One click and errors start flowing:": "Đã sử dụng posthog-js? Chỉ một cú nhấp chuột và lỗi sẽ bắt đầu được ghi nhận:",
    "You're set up. Waiting for the first exception": "Bạn đã cài đặt xong. Đang chờ ngoại lệ đầu tiên",
    "Exception capture is on. When your app throws, the error shows up here on its own, grouped into an issue with its stack trace.": "Tính năng thu thập ngoại lệ đang bật. Khi ứng dụng của bạn gặp lỗi, lỗi sẽ tự động xuất hiện tại đây, được gom nhóm thành sự cố cùng với vết ngăn xếp.",
    "Issues, once exceptions arrive": "Các sự cố, sau khi có ngoại lệ gửi về",
    "Place order": "Đặt hàng",
    "Place order (it throws)": "Đặt hàng (gây lỗi)",
    "Click the button to throw a bug on purpose.": "Bấm vào nút để cố tình tạo ra một lỗi thử nghiệm.",
    "Caught, grouped, and counted below. Click again to undo.": "Đã bắt được, gom nhóm và thống kê bên dưới. Nhấp lại để hoàn tác.",
    "example data": "dữ liệu mẫu",
    "Listening for your first exception…": "Đang lắng nghe ngoại lệ đầu tiên của bạn…",
    "Listening for your first exception...": "Đang lắng nghe ngoại lệ đầu tiên của bạn…",
    "Exceptions · 24 h": "Ngoại lệ · 24 giờ",
    "Exceptions \xB7 24 h": "Ngoại lệ · 24 giờ",
    "captured just now": "vừa ghi nhận xong",
    "in app": "trong ứng dụng",
    "Enable exception autocapture": "Bật tự động thu thập ngoại lệ",
    "Sticker pack × 2": "Gói nhãn dán × 2",
    "Sticker pack": "Gói nhãn dán",
    "Open issues": "Sự cố đang mở",
    "Resolved issues": "Sự cố đã giải quyết",
    "Ignored issues": "Sự cố đã bỏ qua",
    "Merge issues": "Hợp nhất sự cố",
    "Mark as resolved": "Đánh dấu đã giải quyết",
    "Mark as ongoing": "Đánh dấu đang xử lý",
    "Ignore": "Bỏ qua",
    "First seen": "Xuất hiện lần đầu",
    "Last seen": "Xuất hiện lần cuối",
    "Assignee": "Người được giao",
    "Unassigned": "Chưa phân công",
    "Occurrences": "Số lần xuất hiện",
    "Users affected": "Người dùng bị ảnh hưởng",
    "Crash rate": "Tỷ lệ sự cố",
    "Fingerprint": "Dấu vân tay lỗi",
    "Stack trace": "Vết ngăn xếp (Stack trace)",
    "Raw stack trace": "Vết ngăn xếp thô",
    "Symbols": "Ký hiệu (Symbols)",
    "Symbolication": "Giải mã vết lỗi (Symbolication)",
    "Upload source maps": "Tải lên Source maps",

    # -------------------------------------------------------------
    # WEB ANALYTICS / CORE WEB VITALS
    # -------------------------------------------------------------
    "Know how fast your site feels": "Biết trang web của bạn nhanh đến mức nào trong mắt người dùng",
    "Capture Core Web Vitals (LCP, CLS, INP, and FCP) from real visits and see which pages drag them down. Captured events count toward your event quota, and you can turn this off any time in settings.": "Thu thập các chỉ số Core Web Vitals (LCP, CLS, INP và FCP) từ các lượt truy cập thực tế và phát hiện trang nào làm chậm hệ thống. Dữ liệu này được tính vào hạn ngạch sự kiện và bạn có thể tắt bất cứ lúc nào trong phần Cài đặt.",
    "Already sending pageviews with posthog-js? One click and vitals start flowing:": "Đã gửi lượt xem trang với posthog-js? Chỉ một cú nhấp chuột và các chỉ số Web Vitals sẽ bắt đầu được ghi nhận:",
    "Autocapture is on. Waiting for the first vitals": "Tự động thu thập đang bật. Đang chờ các chỉ số Web Vitals đầu tiên",
    "Web vitals arrive with your next page visits. Open your site in another tab and the first samples show up here on their own.": "Các chỉ số Web Vitals sẽ đến cùng các lượt truy cập trang tiếp theo. Hãy mở trang web của bạn trong một tab khác và các mẫu dữ liệu đầu tiên sẽ tự động xuất hiện tại đây.",

    # -------------------------------------------------------------
    # SESSION REPLAY
    # -------------------------------------------------------------
    "Watch how people really use your product": "Quan sát cách mọi người thực sự sử dụng sản phẩm của bạn",
    "Record sessions and replay every click, scroll, and console log. See where users get stuck, reproduce bugs exactly as they happened, and jump from any event or error to the moment it occurred.": "Ghi lại các phiên và phát lại từng thao tác nhấp chuột, cuộn trang và nhật ký console. Xem người dùng bị mắc kẹt ở đâu, tái hiện lỗi chính xác như đã xảy ra và nhảy từ bất kỳ sự kiện hoặc lỗi nào đến đúng thời điểm xảy ra.",
    "Already sending events with posthog-js? One click and recording starts:": "Đã gửi sự kiện với posthog-js? Chỉ một cú nhấp chuột và quá trình ghi phiên sẽ bắt đầu:",
    "Recording is on. Waiting for the first session": "Tính năng ghi phiên đang bật. Đang chờ phiên đầu tiên",
    "New sessions start recording as users visit your site. The first replays usually show up here a few minutes after a visit.": "Các phiên mới sẽ bắt đầu được ghi lại khi người dùng truy cập trang web của bạn. Các bản ghi phát lại đầu tiên thường xuất hiện tại đây vài phút sau lượt truy cập.",

    # -------------------------------------------------------------
    # SURVEYS
    # -------------------------------------------------------------
    "Ask your users, right in the product": "Khảo sát người dùng ngay bên trong sản phẩm",
    "Launch NPS, CSAT, or fully custom surveys with no code. Target them by cohort, feature flag, or URL, and analyze responses next to the rest of your product data.": "Triển khai khảo sát NPS, CSAT hoặc khảo sát tùy chỉnh hoàn toàn mà không cần viết mã. Nhắm mục tiêu theo nhóm người dùng, cờ tính năng hoặc URL, và phân tích phản hồi ngay cạnh dữ liệu sản phẩm của bạn.",

    # -------------------------------------------------------------
    # PRODUCT TOURS
    # -------------------------------------------------------------
    "Show users what to do next, right in your app": "Hướng dẫn người dùng các bước tiếp theo ngay trong ứng dụng",
    "Build multi-step tours that point at real elements in your product, plus announcements and banners for one-off messages. Steps can highlight an element, open a modal, or pin a banner, and feature flags control exactly who sees each tour. No redeploy needed to launch, change, or stop one.": "Xây dựng các tour hướng dẫn nhiều bước trỏ trực tiếp vào các thành phần thực tế trong sản phẩm, cùng các thông báo và banner cho tin nhắn tức thì. Các bước có thể làm nổi bật thành phần, mở cửa sổ bật lên (modal) hoặc ghim banner, và cờ tính năng kiểm soát chính xác ai nhìn thấy tour. Không cần triển khai lại mã khi khởi chạy, thay đổi hoặc dừng lại.",

    # -------------------------------------------------------------
    # REPLAY SCANNERS
    # -------------------------------------------------------------
    "AI watches your recordings so you don't have to": "AI tự động theo dõi bản ghi thay cho bạn",
    "Describe what to look for in plain language. A scanner watches each new session recording for it. Every result is an event you can query, graph, and alert on.": "Mô tả những gì cần tìm bằng ngôn ngữ tự nhiên. Trình quét sẽ tự động theo dõi từng bản ghi phiên mới để tìm kiếm. Mỗi kết quả là một sự kiện bạn có thể truy vấn, vẽ biểu đồ và đặt cảnh báo.",
    "Fastest way in: the setup agent turns on session replay if needed, then reads your codebase and creates scanners for your key flows:": "Cách nhanh nhất: trợ lý cài đặt sẽ bật bản ghi phiên nếu cần, sau đó đọc mã nguồn của bạn và tạo các bộ quét cho các luồng quan trọng:",

    # -------------------------------------------------------------
    # DATA WAREHOUSE SOURCES
    # -------------------------------------------------------------
    "Query your business data next to your product data": "Truy vấn dữ liệu kinh doanh ngay cạnh dữ liệu sản phẩm",
    "Sync tables from Postgres, MySQL, Stripe, Hubspot, and more into PostHog, then join them with your events in SQL. Revenue next to retention, support tickets next to sessions.": "Đồng bộ hóa các bảng từ Postgres, MySQL, Stripe, Hubspot và nhiều nguồn khác vào PostHog, sau đó kết hợp (JOIN) chúng với các sự kiện của bạn bằng SQL. Đặt doanh thu cạnh tỷ lệ giữ chân, phiếu hỗ trợ cạnh các phiên người dùng.",
    "Wizard detects your database and connects it for you:": "Trình hướng dẫn tự động phát hiện cơ sở dữ liệu và kết nối giúp bạn:",

    # -------------------------------------------------------------
    # SUBSCRIPTIONS
    # -------------------------------------------------------------
    "Send the numbers to the people who need them": "Gửi các con số báo cáo đến đúng người cần",
    "A subscription re-runs an insight or a dashboard on a schedule and delivers the result to Slack or email. The people who read it never have to open PostHog, and you can ask for a written report from a prompt instead of a chart.": "Đăng ký định kỳ sẽ tự động chạy lại thông tin chi tiết hoặc bảng điều khiển theo lịch trình và gửi kết quả đến Slack hoặc email. Người nhận không cần phải mở PostHog, và bạn có thể yêu cầu báo cáo dạng văn bản từ câu lệnh thay vì dạng biểu đồ.",

    # -------------------------------------------------------------
    # TRACING / APM
    # -------------------------------------------------------------
    "See where every request spends its time": "Xem mọi yêu cầu mạng tiêu tốn thời gian ở đâu",
    "Send spans from any OpenTelemetry-compatible client over OTLP. No PostHog-specific packages needed. Follow a request across services, find the span that slows it down, and watch latency over time.": "Gửi các đoạn dấu vết (spans) từ bất kỳ client nào tương thích với OpenTelemetry qua giao thức OTLP. Không cần thư viện riêng của PostHog. Theo dõi một yêu cầu qua các dịch vụ vi mô, tìm ra đoạn làm chậm hệ thống và giám sát độ trễ theo thời gian.",

    # -------------------------------------------------------------
    # USER INTERVIEWS
    # -------------------------------------------------------------
    "Run user interviews without booking a single call": "Phỏng vấn người dùng mà không cần đặt một cuộc hẹn nào",
    "Create a research topic with the questions you want answered and the users to ask. An AI voice agent runs each interview, and transcripts and summaries land here as responses come in. You can then search across every response for what users said about any subject.": "Tạo chủ đề nghiên cứu với các câu hỏi bạn muốn được giải đáp và nhóm người dùng cần hỏi. Trợ lý giọng nói AI sẽ thực hiện từng cuộc phỏng vấn, sau đó bản ghi âm và tóm tắt sẽ xuất hiện tại đây khi có câu trả lời. Bạn có thể tìm kiếm xuyên suốt mọi phản hồi để xem người dùng đã nói gì về bất kỳ chủ đề nào.",

    # -------------------------------------------------------------
    # WEB SCRIPTS
    # -------------------------------------------------------------
    "Add scripts to your site without redeploying": "Thêm tập lệnh vào trang web mà không cần triển khai lại mã",
    "Web scripts run custom JavaScript on your site through the PostHog snippet you already have. Start from templates for banners, notifications, and chat-style widgets, or write your own. Enable, update, or disable each script from PostHog, with no code changes.": "Web scripts thực thi JavaScript tùy chỉnh trên trang web của bạn thông qua đoạn mã PostHog có sẵn. Bắt đầu từ các mẫu banner, thông báo và tiện ích trò chuyện, hoặc tự viết mã riêng. Bật, cập nhật hoặc tắt từng tập lệnh trực tiếp từ PostHog mà không cần sửa mã nguồn.",

    # -------------------------------------------------------------
    # WORKFLOWS
    # -------------------------------------------------------------
    "Message users when it matters": "Gửi tin nhắn cho người dùng vào đúng thời điểm quan trọng",
    "Build journeys on a canvas: trigger on any event or cohort, wait, branch on behavior, and send email, SMS, or push. Connect a channel and design your first message along the way.": "Xây dựng hành trình người dùng trên một bảng vẽ trực quan: kích hoạt theo bất kỳ sự kiện hoặc tập người dùng nào, tạm dừng, rẽ nhánh theo hành vi và gửi email, SMS hoặc thông báo đẩy. Kết nối kênh và thiết kế tin nhắn đầu tiên của bạn.",

    # -------------------------------------------------------------
    # CUSTOMER ANALYTICS
    # -------------------------------------------------------------
    "See accounts the way you see users": "Quan sát các tài khoản doanh nghiệp giống như người dùng cá nhân",
    "Customer analytics is built on group analytics: group your users into accounts, then follow each account's activity, health, notes, and feature requests in one place. Start by sending group data from your SDK.": "Phân tích khách hàng được xây dựng trên nền tảng phân tích nhóm: gom nhóm người dùng vào các tài khoản/công ty, sau đó theo dõi hoạt động, sức khỏe tài khoản, ghi chú và yêu cầu tính năng tại một nơi duy nhất. Bắt đầu bằng cách gửi dữ liệu nhóm từ SDK của bạn.",

    # -------------------------------------------------------------
    # FEATURE FLAGS
    # -------------------------------------------------------------
    "Ship code without shipping the feature": "Phát hành mã nguồn mà không bắt buộc phải bật tính năng ngay",
    "Wrap a change in a feature flag, roll it out to 1% of users, and watch what happens: the session replays, events, and exceptions from the people who got it. Turn it off the moment something looks wrong, no redeploy needed. Flags also power experiments, early access programs, kill switches, and remote config.": "Bọc thay đổi trong một cờ tính năng, phân phối thử nghiệm cho 1% người dùng và quan sát điều gì xảy ra: các bản ghi phiên, sự kiện và ngoại lệ từ nhóm người dùng đó. Tắt tính năng ngay lập tức nếu có sự cố mà không cần triển khai lại mã. Cờ tính năng cũng hỗ trợ chạy thử nghiệm A/B, chương trình trải nghiệm sớm, công tắc khẩn cấp và cấu hình từ xa.",

    # -------------------------------------------------------------
    # SUPPORT
    # -------------------------------------------------------------
    "Answer support tickets with full product context": "Xử lý phiếu hỗ trợ với đầy đủ ngữ cảnh sản phẩm",
    "Collect tickets from an in-app chat widget, email, or Slack into one inbox. Every ticket shows the person behind it, with their events, session replays, and past tickets alongside the conversation. Set SLAs, assign owners, and trigger workflows on ticket events.": "Thu thập các phiếu hỗ trợ từ tiện ích chat trong ứng dụng, email hoặc Slack vào một hộp thư đến duy nhất. Mỗi phiếu hiển thị rõ người dùng, kèm theo các sự kiện, bản ghi phiên và các phiếu trước đây bên cạnh cuộc hội thoại. Thiết lập cam kết SLA, phân công người phụ trách và kích hoạt quy trình tự động trên các sự kiện phiếu hỗ trợ.",
    "Support is on. Waiting for your first ticket": "Tính năng hỗ trợ đang bật. Đang chờ phiếu hỗ trợ đầu tiên của bạn",
    "Tickets from your chat widget, email, and any other connected channels will show up here as they arrive. Send a test message through the widget to see one land, or finish connecting a channel in settings.": "Các phiếu hỗ trợ từ tiện ích trò chuyện, email và các kênh kết nối khác sẽ xuất hiện tại đây ngay khi được gửi đến. Hãy gửi tin nhắn thử nghiệm qua tiện ích để kiểm tra hoặc hoàn tất kết nối kênh trong phần Cài đặt.",

    # -------------------------------------------------------------
    # INSIGHTS
    # -------------------------------------------------------------
    "Ask a question about your product and save the answer": "Đặt một câu hỏi về sản phẩm của bạn và lưu lại câu trả lời",
    "An insight is one question about the events you already send: how many people did this, where do they drop off, who comes back. Break the answer down by any property, then save it so you can reopen it later or drop it on a dashboard.": "Một phân tích (insight) là một câu hỏi về các sự kiện bạn đã gửi: có bao nhiêu người thực hiện hành động này, họ rời bỏ ở đâu, ai là người quay lại. Phân tách câu trả lời theo bất kỳ thuộc tính nào, sau đó lưu lại để mở lại sau hoặc đưa vào bảng điều khiển.",

    # -------------------------------------------------------------
    # SKILLS & MCP
    # -------------------------------------------------------------
    "Write a skill once, load it in any agent": "Viết kỹ năng một lần, sử dụng trên mọi tác nhân AI",
    "Skills are versioned instructions your coding agents can discover and use. Publish them here and any MCP-connected agent can load them directly, or install them into Claude Code and Codex with automatic updates. Import and export skills as .zip files to share them across teams.": "Kỹ năng là các chỉ dẫn được quản lý phiên bản mà các tác nhân lập trình AI có thể khám phá và sử dụng. Xuất bản kỹ năng tại đây để bất kỳ tác nhân nào kết nối qua giao thức MCP đều có thể tải trực tiếp, hoặc cài đặt vào Claude Code và Codex với tính năng tự động cập nhật. Nhập và xuất kỹ năng dưới dạng tệp .zip để chia sẻ giữa các nhóm làm việc."
}

# Cập nhật từ điển
for k, v in products_onboarding_terms.items():
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

print(f"Total vocabulary updated: {len(vi_data)} terms!")

# Nâng cache buster lên v=20260908_1415
with open(head_html_path, 'r', encoding='utf-8') as f:
    head_code = f.read()

head_code = re.sub(r'v=\d{8}_\d{4}', 'v=20260908_1415', head_code)
with open(head_html_path, 'w', encoding='utf-8') as f:
    f.write(head_code)

print("head.html cache buster updated to v=20260908_1415")
