import json
import os

vi_path = '/home/opc/posthog-deployment/i18n/locales/vi.json'
vi_js_path = '/home/opc/posthog-deployment/i18n/locales/vi.js'
en_path = '/home/opc/posthog-deployment/i18n/locales/en.json'
en_js_path = '/home/opc/posthog-deployment/i18n/locales/en.js'

with open(vi_path, 'r', encoding='utf-8') as f:
    vi_data = json.load(f)

with open(en_path, 'r', encoding='utf-8') as f:
    en_data = json.load(f)

replay_terms = {
    # Header & Banner
    "Replay vision is here. Scanners watch your recordings for you and surface what matters.": "Replay Vision đã sẵn sàng. Trình quét tự động theo dõi bản ghi của bạn và làm nổi bật những gì quan trọng nhất.",
    "Replay vision is here": "Replay Vision đã sẵn sàng",
    "Try Replay vision": "Trải nghiệm Replay Vision",
    "Try Replay Vision": "Trải nghiệm Replay Vision",
    "Replay vision": "Replay Vision",
    "Replay Vision": "Replay Vision",
    "recently active": "hoạt động gần đây",
    "recently active recording": "bản ghi hoạt động gần đây",
    "recently active recordings": "bản ghi hoạt động gần đây",
    "1 recently active": "1 hoạt động gần đây",
    "1 recently active recording": "1 bản ghi hoạt động gần đây",
    "1 recently active recordings": "1 bản ghi hoạt động gần đây",
    "1 recently active Bản ghi phiên": "1 bản ghi phiên hoạt động gần đây",
    "recently active Bản ghi phiên": "bản ghi phiên hoạt động gần đây",

    # Left pane / recording list
    "Viewed and unviewed recordings": "Bản ghi đã xem và chưa xem",
    "Unviewed recordings": "Bản ghi chưa xem",
    "Viewed recordings": "Bản ghi đã xem",
    "Relative": "Tương đối",
    "Absolute": "Tuyệt đối",
    "Latest": "Mới nhất",
    "Oldest": "Cũ nhất",
    "Duration: High to Low": "Thời lượng: Cao đến thấp",
    "Duration: Low to High": "Thời lượng: Thấp đến cao",
    "Activity: High to Low": "Mức độ hoạt động: Cao đến thấp",
    "Activity: Low to High": "Mức độ hoạt động: Thấp đến cao",
    "Search over the last 30 days": "Tìm kiếm trong 30 ngày qua",
    "Recordings might be outside the retention period": "Bản ghi có thể nằm ngoài thời gian lưu trữ",
    "An ad blocker might be preventing recordings": "Trình chặn quảng cáo có thể đang chặn ghi phiên",
    "No recordings yet": "Chưa có bản ghi nào",
    "No recordings in this collection": "Không có bản ghi nào trong bộ sưu tập này",
    "No recording selected": "Chưa chọn bản ghi nào",
    "Please select a recording from the list on the left": "Vui lòng chọn một bản ghi từ danh sách bên trái",
    "Loading recordings...": "Đang tải danh sách bản ghi...",
    "Error while trying to load recordings.": "Lỗi khi tải danh sách bản ghi.",
    "Learn more about recordings": "Tìm hiểu thêm về bản ghi phiên",

    # Right pane / filter pane
    "Saved filters": "Bộ lọc đã lưu",
    "Saved filter": "Bộ lọc đã lưu",
    "Save as new filter": "Lưu thành bộ lọc mới",
    "Save filter": "Lưu bộ lọc",
    "Save changes": "Lưu thay đổi",
    "Match": "Khớp",
    "Match all filters": "Khớp tất cả bộ lọc",
    "Match any filter": "Khớp bất kỳ bộ lọc nào",
    "Filter out internal and test users": "Lọc bỏ người dùng nội bộ và thử nghiệm",
    "Search suggested filters, URLs, email addresses, recent, pinned...": "Tìm kiếm bộ lọc gợi ý, URL, địa chỉ email, gần đây, đã ghim...",
    "Applied filters:": "Bộ lọc đã áp dụng:",
    "Applied filters": "Bộ lọc đã áp dụng",

    # Time & duration filters
    "> 5 active seconds": "> 5 giây hoạt động",
    "> 10 active seconds": "> 10 giây hoạt động",
    "> 30 active seconds": "> 30 giây hoạt động",
    "> 1 active minutes": "> 1 phút hoạt động",
    "> 5 active minutes": "> 5 phút hoạt động",
    "> 10 active minutes": "> 10 phút hoạt động",
    "active seconds": "giây hoạt động",
    "active minutes": "phút hoạt động",
    "active hours": "giờ hoạt động",
    "Last 24 hours": "24 giờ qua",
    "Last 3 days": "3 ngày qua",
    "Last 7 days": "7 ngày qua",
    "Last 14 days": "14 ngày qua",
    "Last 30 days": "30 ngày qua",
    "Last 90 days": "90 ngày qua",
    "Last 180 days": "180 ngày qua",
    "Last 365 days": "365 ngày qua",
    "Today": "Hôm nay",
    "Yesterday": "Hôm qua",
    "This week": "Tuần này",
    "Previous week": "Tuần trước",
    "This month": "Tháng này",
    "Previous month": "Tháng trước",
    "This year": "Năm nay",
    "Previous year": "Năm trước",
    "All time": "Toàn thời gian",
    "Custom range": "Khoảng tùy chỉnh",
    "Showing": "Đang hiển thị",
    "results": "kết quả",
    "results.": "kết quả.",

    # Collections & templates
    "New collection": "Bộ sưu tập mới",
    "Playback from PostHog JSON file": "Phát lại từ tệp JSON PostHog",
    "Kiosk mode": "Chế độ Kiosk",
    "Filter templates": "Mẫu bộ lọc",
    "View & create collections": "Xem & tạo bộ sưu tập",
    "Select event": "Chọn sự kiện",
    "Select person property": "Chọn thuộc tính người dùng",
    "Apply filters": "Áp dụng bộ lọc",
    "Please set a value for at least one variable": "Vui lòng đặt giá trị cho ít nhất một biến",
    "This collection is automatically populated.": "Bộ sưu tập này được tự động cập nhật.",
    "Cannot use these events to filter for session recordings:": "Không thể dùng các sự kiện này để lọc bản ghi phiên:",
    "Events have to have a": "Sự kiện cần phải có",
    "to be used to filter recordings. This is added automatically by": "để dùng làm bộ lọc bản ghi. Giá trị này được tự động thêm bởi",
    "the Web SDK": "Web SDK",
    "and the Mobile SDKs (Android, iOS, React Native and Flutter)": "và các Mobile SDK (Android, iOS, React Native và Flutter)",
    "Use our templates to find a focus area, then watch the filtered replays to see where users struggle, what could be made more clear, and other ways to improve.": "Sử dụng các mẫu có sẵn để tìm khu vực trọng tâm, sau đó xem các bản ghi đã lọc để hiểu người dùng gặp khó khăn ở đâu và cách cải thiện.",
    "To get the most out of session replay, you just need to know where to start.": "Để khai thác tối đa bản ghi phiên, bạn chỉ cần biết nơi bắt đầu."
}

for k, v in replay_terms.items():
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

print(f"SUCCESS: Synced {len(replay_terms)} new replay terms to vi.json, vi.js, en.json, en.js. Total terms: {len(vi_data)}")
