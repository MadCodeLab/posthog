/**
 * PostHog Internationalization (i18n) Architecture Engine
 * Hệ thống Đa ngôn ngữ chuẩn chỉ cho PostHog
 *
 * Tính năng chính:
 * 1. Tách biệt hoàn toàn từng tệp ngôn ngữ độc lập: locales/vi.json (Tiếng Việt) & locales/en.json (Tiếng Anh)
 * 2. Khởi tạo mặc định: Tiếng Việt ('vi')
 * 3. Hỗ trợ nạp động cả tệp JSON (qua fetch API) và tệp JS Bundle (window.__POSTHOG_I18N_LOCALES__)
 * 4. Quản lý trạng thái chuyển đổi ngôn ngữ mượt mà (smooth bidirectional switching)
 * 5. Lưu trữ trạng thái lựa chọn người dùng vào localStorage ('posthog_i18n_lang')
 * 6. Tích hợp nút chuyển đổi ngôn ngữ tại 3 vị trí:
 *    - Sidebar Navigation Bar (thanh điều hướng chính, tương thích cả khi thu gọn)
 *    - Trang Cài đặt (Settings Scene)
 *    - Widget chuyển đổi nổi góc màn hình (cho mọi trang kể cả login/preflight)
 * 7. Tuân thủ tuyệt đối chuẩn React DOM, KHÔNG monkey-patch Node.prototype, an toàn với textarea và input
 * 8. Đồng bộ thuộc tính chuẩn document.documentElement.lang
 */

(function () {
    'use strict';

    // =========================================================================
    // 1. CẤU HÌNH & KHỞI TẠO TRẠNG THÁI (STATE MANAGEMENT)
    // =========================================================================
    const STORAGE_KEY = 'posthog_i18n_lang';
    const DEFAULT_LOCALE = 'vi';
    const SUPPORTED_LOCALES = ['vi', 'en'];

    let currentLocale = DEFAULT_LOCALE;
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored && SUPPORTED_LOCALES.includes(stored)) {
            currentLocale = stored;
        } else {
            localStorage.setItem(STORAGE_KEY, DEFAULT_LOCALE);
            currentLocale = DEFAULT_LOCALE;
        }
    } catch (e) {
        currentLocale = DEFAULT_LOCALE;
    }

    // Đồng bộ thuộc tính lang của tài liệu HTML
    if (typeof document !== 'undefined' && document.documentElement) {
        document.documentElement.lang = currentLocale;
    }

    // Kho lưu trữ từ điển độc lập theo mã locale
    const localeCatalogs = {};
    const lowerIndexes = {};

    function registerLocale(code, catalog) {
        if (!code || !catalog || typeof catalog !== 'object') return;
        localeCatalogs[code] = catalog;

        // Xây dựng chỉ mục chữ thường O(1) phục vụ tra cứu case-insensitive
        const lowerMap = new Map();
        for (const [k, v] of Object.entries(catalog)) {
            lowerMap.set(k.toLowerCase(), v);
        }
        lowerIndexes[code] = lowerMap;

        console.log(`[PostHog i18n] Đã nạp thành công từ điển locale: '${code}' (${Object.keys(catalog).length} mục dịch)`);

        // Nếu nạp locale đang sử dụng, lập tức quét và dịch giao diện ngay
        if (code === currentLocale && typeof document !== 'undefined' && document.body) {
            scanAndTranslate(document.body);
        }
    }

    function ensureCatalogs() {
        if (typeof window === 'undefined') return;
        if (window.__POSTHOG_I18N_LOCALES__) {
            for (const [code, dict] of Object.entries(window.__POSTHOG_I18N_LOCALES__)) {
                if (!localeCatalogs[code]) registerLocale(code, dict);
            }
        }
        if (window.__POSTHOG_I18N_VI__ && !localeCatalogs['vi']) {
            registerLocale('vi', window.__POSTHOG_I18N_VI__);
        }
        if (window.__POSTHOG_I18N_EN__ && !localeCatalogs['en']) {
            registerLocale('en', window.__POSTHOG_I18N_EN__);
        }
    }

    // Tải động tệp JSON của locale nếu chưa được tải sẵn
    async function loadLocale(code) {
        if (!SUPPORTED_LOCALES.includes(code)) return null;
        ensureCatalogs();
        if (localeCatalogs[code] && Object.keys(localeCatalogs[code]).length > 0) {
            return localeCatalogs[code];
        }
        try {
            const resp = await fetch(`/static/locales/${code}.json?v=20260908_1530`);
            if (resp.ok) {
                const data = await resp.json();
                registerLocale(code, data);
                return data;
            }
        } catch (err) {
            console.warn(`[PostHog i18n] Không thể nạp locale '${code}' qua mạng:`, err);
        }
        return null;
    }

    // Nạp các catalog đã được tải trước từ window
    ensureCatalogs();

    // =========================================================================
    // 2. HÀM DỊCH THUẬT TIÊU CHUẨN (t FUNCTION)
    // =========================================================================
    function normalizeText(str) {
        if (!str || typeof str !== 'string') return '';
        return str.replace(/\u00a0/g, ' ').replace(/[\r\n\t]+/g, ' ').replace(/\s{2,}/g, ' ').trim();
    }

    function lookupDict(key, lang) {
        if (!key) return null;
        if (!localeCatalogs[lang]) ensureCatalogs();
        const dict = localeCatalogs[lang] || {};
        if (dict[key]) return dict[key];

        const norm = normalizeText(key);
        if (dict[norm]) return dict[norm];

        // Chuẩn hóa biến thể dấu gạch ngang (em dash \u2014, en dash \u2013 sang hyphen hoặc ngược lại)
        const dashNorm = norm.replace(/[\u2010-\u2015\u2212]/g, '-');
        if (dict[dashNorm]) return dict[dashNorm];

        const emDashNorm = norm.replace(/[\u2010-\u2015\u2212]|\s+-\s+/g, ' — ');
        if (dict[emDashNorm]) return dict[emDashNorm];

        const lowerMap = lowerIndexes[lang];
        if (lowerMap) {
            const lowerVal = lowerMap.get(norm.toLowerCase()) ||
                             lowerMap.get(dashNorm.toLowerCase()) ||
                             lowerMap.get(emDashNorm.toLowerCase()) ||
                             lowerMap.get(key.toLowerCase());
            if (lowerVal) {
                return (key === key.toUpperCase() && key.length > 1) ? lowerVal.toUpperCase() : lowerVal;
            }
        }


        // Bộ quy tắc dịch động thông minh đa năng cho Tiếng Việt
        if (lang === 'vi') {
            // 1. Chào mừng
            const helloMatch = norm.match(/^Hello\s+(.+)$/i);
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

            const agoMatch = norm.match(/^(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago$/i);
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
            const durationMatch = norm.match(/^(\d+)m\s*(\d+)s$/i);
            if (durationMatch) {
                return durationMatch[1] + 'm ' + durationMatch[2] + 's';
            }

            // 4. Làm mới lần cuối: "Last refreshed a few seconds ago", "Last refreshed 5 minutes ago"
            const refreshMatch = norm.match(/^Last refreshed\s*(.*)$/i);
            if (refreshMatch) {
                const rest = refreshMatch[1].trim();
                const restTrans = lookupDict(rest, 'vi') || rest;
                return 'Làm mới lần cuối ' + (restTrans === rest && rest.includes('ago') ? rest.replace('a few seconds ago', 'vài giây trước').replace('an hour ago', '1 giờ trước') : restTrans);
            }
            // 4b. Đã tính toán lần cuối: "Computed 2 hours ago", "Computed 2 giờ trước", "Computed a few seconds ago"
            const computedMatch = norm.match(/^Computed\s*(.*)$/i);
            if (computedMatch) {
                const rest = computedMatch[1].trim();
                const restTrans = lookupDict(rest, 'vi') || rest;
                let timeStr = restTrans;
                if (restTrans === rest) {
                    timeStr = rest.replace(/a few seconds ago/i, 'vài giây trước')
                                  .replace(/just now/i, 'vừa xong')
                                  .replace(/an? hour ago/i, '1 giờ trước')
                                  .replace(/(\d+)\s+hours?\s+ago/i, '$1 giờ trước')
                                  .replace(/(\d+)\s+days?\s+ago/i, '$1 ngày trước')
                                  .replace(/(\d+)\s+minutes?\s+ago/i, '$1 phút trước');
                }
                return 'Đã tính toán ' + timeStr;
            }


            // 5. So sánh với kỳ trước: "vs. 0 prior", "vs. 15 prior"
            const priorMatch = norm.match(/^vs\.\s*([\d,]+)\s+prior$/i);
            if (priorMatch) {
                return 'so với ' + priorMatch[1] + ' trước đó';
            }

            // 6. Nhóm theo: "grouped by"
            if (/^grouped by$/i.test(norm)) return 'nhóm theo';

            // 7. Tuần và Thứ
            const weekMatch = norm.match(/^Week\s+(\d+)$/i);
            if (weekMatch) return 'Tuần ' + weekMatch[1];

            const daysMap = { 'sun': 'CN', 'mon': 'T2', 'tue': 'T3', 'wed': 'T4', 'thu': 'T5', 'fri': 'T6', 'sat': 'T7' };
            if (daysMap[norm.toLowerCase()]) return daysMap[norm.toLowerCase()];

            // 8. Dải ngày tháng: "Aug 30 to Sep 5"
            const monthRangeMatch = norm.match(/^([a-zA-Z]{3})\s+(\d+)\s+to\s+([a-zA-Z]{3})\s+(\d+)$/i);
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
            const recentlyMatch = norm.match(/^(\d+)\s+recently active(?:\s*(?:recordings?|Bản ghi phiên))?$/i);
            if (recentlyMatch) {
                return recentlyMatch[1] + ' bản ghi hoạt động gần đây';
            }
            if (/^recently active(?:\s*(?:recordings?|Bản ghi phiên))?$/i.test(norm)) {
                return 'bản ghi hoạt động gần đây';
            }

            // 10. Chuỗi thời gian tương đối bộ lọc: "Last 3 days", "Last 24 hours"
            const lastTimeMatch = norm.match(/^Last\s+(\d+)\s+(seconds?|minutes?|hours?|days?|weeks?|months?|years?)$/i);
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
            const activeTimeMatch = norm.match(/^(>=?|<=?|>|<)\s*(\d+)\s+active\s+(seconds?|minutes?|hours?)$/i);
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

                return null;
    }

    // Thay thế an toàn đúng vị trí chuỗi con, tránh các lỗi biến dạng $ trong String.replace
    function replaceTrimmed(rawText, trimmedTarget, replacement) {
        if (rawText === trimmedTarget) return replacement;
        const idx = rawText.indexOf(trimmedTarget);
        if (idx === -1) return rawText;
        return rawText.slice(0, idx) + replacement + rawText.slice(idx + trimmedTarget.length);
    }

    function translate(text, defaultVal) {
        if (!text || typeof text !== 'string') return text;
        const trimmed = text.trim();
        if (!trimmed) return text;

        // Bỏ qua các chuỗi biến hệ thống PostHog ($current_url...), URL, Email
        if (trimmed.startsWith('$') || trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
            return text;
        }

        // Nếu là tiếng Anh ('en'), trả về chuỗi gốc
        if (currentLocale === 'en') {
            return defaultVal !== undefined ? defaultVal : text;
        }

        // 1. Khớp từ điển trực tiếp O(1)
        const direct = lookupDict(trimmed, 'vi');
        if (direct) {
            return replaceTrimmed(text, trimmed, direct);
        }

        // 2. Xử lý ký tự kết thúc: dấu câu (:, ?, !, ., ..., …) và mũi tên/ký hiệu (→, ←, ↗, ›, », >)
        const trailingMatch = trimmed.match(/^(.+?)(\s*(?:[:?!\u2026\.]|\.{3}|[\u2190-\u2193\u2197\u2198\u203a\u00bb>]))$/);
        if (trailingMatch) {
            const base = trailingMatch[1].trim();
            const suffix = trailingMatch[2];
            const baseTrans = lookupDict(base, 'vi');
            if (baseTrans) {
                return replaceTrimmed(text, trimmed, baseTrans + suffix);
            }
        }

        // 3. Xử lý ký tự bắt đầu: chú thích code (// ) hoặc mũi tên điều hướng (← , → )
        const leadingMatch = trimmed.match(/^((?:\/\/|[\u2190-\u2193\u2197\u2198]\s*)\s*)(.+)$/);
        if (leadingMatch) {
            const prefix = leadingMatch[1];
            const base = leadingMatch[2].trim();
            const baseTrans = lookupDict(base, 'vi');
            if (baseTrans) {
                return replaceTrimmed(text, trimmed, prefix + baseTrans);
            }
        }

        // 4. Xử lý số lượng trong ngoặc đơn: "Events (12)", "Dashboards (3)"
        const parenMatch = trimmed.match(/^(.+?)\s*\(([\d,]+)\)$/);
        if (parenMatch) {
            const base = parenMatch[1].trim();
            const count = parenMatch[2];
            const baseTrans = lookupDict(base, 'vi');
            if (baseTrans) {
                return replaceTrimmed(text, trimmed, `${baseTrans} (${count})`);
            }
        }

        // 5. Xử lý số lượng đứng đầu: "12 Events", "0 results", "5 dashboards"
        const countMatch = trimmed.match(/^([\d,]+)\s+(.+)$/);
        if (countMatch) {
            const count = countMatch[1];
            const base = countMatch[2].trim();
            const baseTrans = lookupDict(base, 'vi');
            if (baseTrans) {
                return replaceTrimmed(text, trimmed, `${count} ${baseTrans}`);
            }
        }

        return defaultVal !== undefined ? defaultVal : text;
    }

    // =========================================================================
    // 3. XỬ LÝ AN TOÀN TRÊN GIAO DIỆN HIỂN THỊ (DOM UI TRANSLATION)
    // =========================================================================
    function shouldSkipElement(el) {
        if (!el || el.nodeType !== Node.ELEMENT_NODE) return false;
        if (el.id === 'posthog-i18n-switcher' ||
            el.id === 'posthog-i18n-settings-card' ||
            el.id === 'posthog-i18n-nav-item') {
            return true;
        }
        const tag = el.tagName ? el.tagName.toUpperCase() : '';
        if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'IFRAME', 'SVG', 'PATH', 'CANVAS'].includes(tag)) {
            return true;
        }
        if (el.isContentEditable) return true;
        if (el.classList) {
            if (el.classList.contains('notranslate') ||
                el.classList.contains('monaco-editor') ||
                el.classList.contains('code-editor') ||
                el.classList.contains('sql-editor')) {
                return true;
            }
        }
        return false;
    }

    function processTextNode(node) {
        if (!node || node.nodeType !== Node.TEXT_NODE) return;
        const parent = node.parentElement;
        // Bảo vệ an toàn tuyệt đối cho ô nhập liệu textarea
        if (!parent || shouldSkipElement(parent) || parent.tagName === 'TEXTAREA') return;

        // Cơ chế đa node chính thống: Nếu thẻ cha chỉ chứa các text node con (React split text)
        // Tra cứu toàn văn bản hợp nhất trực tiếp từ tệp từ điển locales (O(1)), không hardcode if-else
        if (parent.childNodes && parent.childNodes.length > 1) {
            let hasOnlyText = true;
            for (let i = 0; i < parent.childNodes.length; i++) {
                if (parent.childNodes[i].nodeType !== Node.TEXT_NODE) {
                    hasOnlyText = false;
                    break;
                }
            }

            if (hasOnlyText) {
                // Lưu bản gốc nguyên bản của các node con
                if (!parent.__ph_orig_nodes) {
                    parent.__ph_orig_nodes = Array.from(parent.childNodes).map(ch => ch.nodeValue || '');
                }

                if (currentLocale === 'vi') {
                    const fullClean = parent.__ph_orig_nodes.join('').trim();
                    const transWhole = lookupDict(fullClean, 'vi');
                    if (transWhole) {
                        for (let i = 0; i < parent.childNodes.length; i++) {
                            const ch = parent.childNodes[i];
                            const targetVal = (i === 0) ? transWhole : '';
                            if (ch.nodeValue !== targetVal) {
                                ch.nodeValue = targetVal;
                                ch.__posthog_i18n_last = targetVal;
                            }
                        }
                        return;
                    }
                } else {
                    // Phục hồi tiếng Anh nguyên bản
                    if (parent.__ph_orig_nodes) {
                        for (let i = 0; i < parent.childNodes.length; i++) {
                            const ch = parent.childNodes[i];
                            const origVal = parent.__ph_orig_nodes[i];
                            if (origVal !== undefined && ch.nodeValue !== origVal) {
                                ch.nodeValue = origVal;
                                ch.__posthog_i18n_last = origVal;
                            }
                        }
                        return;
                    }
                }
            }
        }

        // Nếu nodeValue hiện tại đã là bản dịch thì không làm lại
        if (node.__posthog_i18n_last !== undefined && node.nodeValue === node.__posthog_i18n_last) {
            return;
        }

        // Lưu hoặc cập nhật bản gốc khi React/JS thay đổi giá trị node
        if (node.__posthog_i18n_orig === undefined || node.nodeValue !== node.__posthog_i18n_last) {
            node.__posthog_i18n_orig = node.nodeValue;
        }

        if (currentLocale === 'vi') {
            const orig = node.__posthog_i18n_orig;
            const translated = translate(orig);
            if (node.nodeValue !== translated) {
                node.__posthog_i18n_last = translated;
                node.nodeValue = translated;
            }
        } else {
            // Phục hồi tiếng Anh nguyên bản 100%
            const orig = node.__posthog_i18n_orig;
            if (node.nodeValue !== orig) {
                node.__posthog_i18n_last = orig;
                node.nodeValue = orig;
            }
        }
    }

    function processAttributes(el) {
        if (!el || el.nodeType !== Node.ELEMENT_NODE || shouldSkipElement(el)) return;
        const attrs = ['placeholder', 'title', 'aria-label'];
        for (const attr of attrs) {
            const val = el.getAttribute(attr);
            if (val) {
                const origKey = '__posthog_i18n_orig_' + attr;
                if (el[origKey] === undefined) {
                    el[origKey] = val;
                }
                if (currentLocale === 'vi') {
                    const translated = translate(el[origKey]);
                    if (val !== translated) {
                        el.setAttribute(attr, translated);
                    }
                } else {
                    if (val !== el[origKey]) {
                        el.setAttribute(attr, el[origKey]);
                    }
                }
            }
        }
    }

    
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

    function scanAndTranslate(root) {
        removeSignupElements();
        if (!root) return;
        if (root.nodeType === Node.ELEMENT_NODE) {
            if (shouldSkipElement(root)) return;
            processAttributes(root);
        }

        if (typeof document.createTreeWalker !== 'function') {
            if (root.nodeType === Node.TEXT_NODE) {
                processTextNode(root);
            }
            if (root.childNodes) {
                for (let i = 0; i < root.childNodes.length; i++) {
                    scanAndTranslate(root.childNodes[i]);
                }
            }
            return;
        }

        const walker = document.createTreeWalker(
            root,
            NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
            {
                acceptNode: function (node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (shouldSkipElement(node)) return NodeFilter.FILTER_REJECT;
                        processAttributes(node);
                        return NodeFilter.FILTER_SKIP;
                    }
                    if (node.nodeType === Node.TEXT_NODE) {
                        const p = node.parentElement;
                        if (!p || shouldSkipElement(p) || p.tagName === 'TEXTAREA') return NodeFilter.FILTER_REJECT;
                        return NodeFilter.FILTER_ACCEPT;
                    }
                    return NodeFilter.FILTER_SKIP;
                }
            }
        );

        let current;
        while ((current = walker.nextNode())) {
            processTextNode(current);
        }
    }

    // =========================================================================
    // 4. OBSERVER TỐI ƯU HIỆU NĂNG CHO REACT (BATCHED VIA rAF)
    // =========================================================================
    let rAFScheduled = false;
    const pendingNodes = new Set();

    const observer = new MutationObserver((mutations) => {
        for (const m of mutations) {
            if (m.type === 'childList') {
                for (const node of m.addedNodes) {
                    if (!node) continue;
                    if (node.id === 'posthog-i18n-switcher' ||
                        node.id === 'posthog-i18n-settings-card' ||
                        node.id === 'posthog-i18n-nav-item') {
                        continue;
                    }
                    pendingNodes.add(node);
                }
            } else if (m.type === 'characterData') {
                const target = m.target;
                if (!target) continue;
                if (target.__posthog_i18n_last !== undefined && target.nodeValue === target.__posthog_i18n_last) {
                    continue;
                }
                target.__posthog_i18n_orig = target.nodeValue;
                pendingNodes.add(target);
            }
        }

        if (!rAFScheduled && pendingNodes.size > 0) {
            rAFScheduled = true;
            requestAnimationFrame(() => {
                rAFScheduled = false;
                const nodes = Array.from(pendingNodes);
                pendingNodes.clear();

                for (const node of nodes) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        scanAndTranslate(node);
                    } else if (node.nodeType === Node.TEXT_NODE) {
                        processTextNode(node);
                    }
                }
                checkAndInjectUI();
            });
        }
    });

    // =========================================================================
    // 5. CHUYỂN ĐỔI NGÔN NGỮ & ĐỒNG BỘ LOCALSTORAGE (LANGUAGE SWITCHING)
    // =========================================================================
    function setLocale(lang) {
        if (!SUPPORTED_LOCALES.includes(lang)) return;
        currentLocale = lang;
        try {
            localStorage.setItem(STORAGE_KEY, lang);
        } catch (e) {
            // ignore
        }

        if (typeof document !== 'undefined' && document.documentElement) {
            document.documentElement.lang = lang;
        }

        console.log(`[PostHog i18n] Đã chuyển đổi ngôn ngữ sang: ${lang === 'vi' ? 'Tiếng Việt 🇻🇳' : 'English 🇬🇧'}`);

        // Đảm bảo từ điển đã sẵn sàng (nếu dùng lazy load)
        if (!localeCatalogs[lang] && lang === 'vi') {
            loadLocale('vi').then(() => {
                applyLocaleUpdate(lang);
            });
            return;
        }

        applyLocaleUpdate(lang);
    }

    function applyLocaleUpdate(lang) {
        // Thông báo sự kiện chuyển đổi ngôn ngữ cho toàn hệ thống
        window.dispatchEvent(new CustomEvent('posthog:locale-changed', { detail: { locale: lang } }));

        // Cập nhật giao diện toàn diện
        if (document.body) {
            scanAndTranslate(document.body);
        }
        updateSwitcherUI();
        updateSettingsCardUI();
        updateNavbarUI();
    }

    function toggleLocale() {
        setLocale(currentLocale === 'vi' ? 'en' : 'vi');
    }

    function checkAndInjectUI() {
        createSwitcherUI();
        injectSettingsOption();
        injectNavbarOption();
    }

    // =========================================================================
    // 6. UI SWITCHER WIDGET (Nút chuyển đổi nổi)
    // =========================================================================
    function createSwitcherUI() {
        if (!document.body || document.getElementById('posthog-i18n-switcher')) return;

        const container = document.createElement('div');
        container.id = 'posthog-i18n-switcher';
        container.setAttribute('translate', 'no');
        container.className = 'notranslate';

        container.innerHTML = `
            <div class="ph-i18n-wrapper">
                <div class="ph-i18n-menu" id="posthog-i18n-menu">
                    <button class="ph-i18n-item" id="ph-opt-vi" type="button">
                        <span>🇻🇳 Tiếng Việt (Mặc định)</span>
                        <span class="ph-check" id="ph-check-vi">✓</span>
                    </button>
                    <button class="ph-i18n-item" id="ph-opt-en" type="button">
                        <span>🇬🇧 English</span>
                        <span class="ph-check" id="ph-check-en" style="display:none;">✓</span>
                    </button>
                </div>
                <button class="ph-i18n-btn" id="posthog-i18n-toggle-btn" type="button" title="Chuyển ngôn ngữ / Switch Language">
                    <span id="ph-switcher-icon">🌐</span>
                    <span id="ph-switcher-label">${currentLocale === 'vi' ? 'Tiếng Việt' : 'English'}</span>
                </button>
            </div>
        `;

        document.body.appendChild(container);

        const btn = document.getElementById('posthog-i18n-toggle-btn');
        const menu = document.getElementById('posthog-i18n-menu');
        const optVi = document.getElementById('ph-opt-vi');
        const optEn = document.getElementById('ph-opt-en');

        if (btn && menu && optVi && optEn) {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                menu.classList.toggle('active');
            });

            document.addEventListener('click', () => {
                menu.classList.remove('active');
            });

            optVi.addEventListener('click', (e) => {
                e.stopPropagation();
                setLocale('vi');
                menu.classList.remove('active');
            });

            optEn.addEventListener('click', (e) => {
                e.stopPropagation();
                setLocale('en');
                menu.classList.remove('active');
            });
        }

        updateSwitcherUI();
    }

    function updateSwitcherUI() {
        const label = document.getElementById('ph-switcher-label');
        const checkVi = document.getElementById('ph-check-vi');
        const checkEn = document.getElementById('ph-check-en');
        const optVi = document.getElementById('ph-opt-vi');
        const optEn = document.getElementById('ph-opt-en');

        if (!label) return;

        if (currentLocale === 'vi') {
            label.textContent = 'Tiếng Việt';
            if (checkVi) checkVi.style.display = 'inline';
            if (checkEn) checkEn.style.display = 'none';
            if (optVi && optVi.classList) optVi.classList.add('selected');
            if (optEn && optEn.classList) optEn.classList.remove('selected');
        } else {
            label.textContent = 'English';
            if (checkVi) checkVi.style.display = 'none';
            if (checkEn) checkEn.style.display = 'inline';
            if (optVi && optVi.classList) optVi.classList.remove('selected');
            if (optEn && optEn.classList) optEn.classList.add('selected');
        }
    }

    // =========================================================================
    // 7. TÍCH HỢP VÀO TRANG CÀI ĐẶT (SETTINGS SCENE)
    // =========================================================================
    function injectSettingsOption() {
        const isSettingsPage = window.location.pathname.includes('/settings') ||
                               window.location.pathname.includes('/project/settings') ||
                               window.location.pathname.includes('/organization/settings');
        if (!isSettingsPage) {
            const old = document.getElementById('posthog-i18n-settings-card');
            if (old && old.parentNode) old.parentNode.removeChild(old);
            return;
        }

        const existingCard = document.getElementById('posthog-i18n-settings-card');
        if (existingCard) {
            updateSettingsCardUI();
            return;
        }

        let target = document.querySelector('#theme')?.closest('.relative');
        let insertMethod = 'after';

        if (!target) {
            target = document.querySelector('.Settings .flex-col.gap-y-8') ||
                     document.querySelector('.Settings .space-y-2') ||
                     document.querySelector('.Settings [class*="min-w-0"]') ||
                     document.querySelector('.Settings');
            insertMethod = 'prepend';
        }

        if (!target) return;

        const card = document.createElement('div');
        card.id = 'posthog-i18n-settings-card';
        card.className = 'relative mb-6 p-4 rounded border';
        card.setAttribute('translate', 'no');

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;">
                <div>
                    <h2 class="text-base font-semibold mb-1" id="ph-st-title" style="margin: 0 0 4px 0;">
                        ${currentLocale === 'vi' ? 'Ngôn ngữ hiển thị' : 'Display Language'}
                    </h2>
                    <p class="text-sm text-secondary" id="ph-st-desc" style="margin: 0; opacity: 0.85;">
                        ${currentLocale === 'vi' ? 'Chọn ngôn ngữ giao diện PostHog (Áp dụng toàn bộ hệ thống)' : 'Choose PostHog UI language (Applied system-wide)'}
                    </p>
                </div>
                <div>
                    <select id="posthog-i18n-settings-select">
                        <option value="vi" ${currentLocale === 'vi' ? 'selected' : ''}>🇻🇳 Tiếng Việt (Mặc định)</option>
                        <option value="en" ${currentLocale === 'en' ? 'selected' : ''}>🇬🇧 English</option>
                    </select>
                </div>
            </div>
        `;

        if (insertMethod === 'after' && target.parentNode) {
            target.parentNode.insertBefore(card, target.nextSibling);
        } else if (target.firstChild) {
            target.insertBefore(card, target.firstChild);
        } else {
            target.appendChild(card);
        }

        const select = document.getElementById('posthog-i18n-settings-select');
        if (select) {
            select.addEventListener('change', (e) => {
                setLocale(e.target.value);
            });
        }
    }

    function updateSettingsCardUI() {
        const title = document.getElementById('ph-st-title');
        const desc = document.getElementById('ph-st-desc');
        const select = document.getElementById('posthog-i18n-settings-select');
        if (!title || !desc || !select) return;

        if (currentLocale === 'vi') {
            title.textContent = 'Ngôn ngữ hiển thị';
            desc.textContent = 'Chọn ngôn ngữ giao diện PostHog (Áp dụng toàn bộ hệ thống)';
            select.value = 'vi';
        } else {
            title.textContent = 'Display Language';
            desc.textContent = 'Choose PostHog UI language (Applied system-wide)';
            select.value = 'en';
        }
    }

    // =========================================================================
    // 8. TÍCH HỢP VÀO THANH ĐIỀU HƯỚNG (SIDEBAR NAVBAR)
    // =========================================================================
    function injectNavbarOption() {
        const settingsLink = document.querySelector('[data-attr="navbar-settings"]');
        if (!settingsLink || document.getElementById('posthog-i18n-nav-item')) return;

        const navItem = document.createElement('button');
        navItem.id = 'posthog-i18n-nav-item';
        navItem.setAttribute('translate', 'no');
        navItem.setAttribute('type', 'button');
        navItem.title = 'Chuyển ngôn ngữ / Switch Language';

        navItem.innerHTML = `
            <span style="font-size: 16px;">🌐</span>
            <span id="ph-nav-lang-label">${currentLocale === 'vi' ? 'Tiếng Việt' : 'English'}</span>
        `;

        navItem.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleLocale();
        });

        if (settingsLink.parentNode) {
            settingsLink.parentNode.insertBefore(navItem, settingsLink);
        }
    }

    function updateNavbarUI() {
        const label = document.getElementById('ph-nav-lang-label');
        if (label) {
            label.textContent = currentLocale === 'vi' ? 'Tiếng Việt' : 'English';
        }
    }

    // =========================================================================
    // 9. KHỞI ĐỘNG HỆ THỐNG i18n
    // =========================================================================
    async function init() {
        ensureCatalogs();
        if (!localeCatalogs[currentLocale]) {
            await loadLocale(currentLocale);
        }
        console.log(`[PostHog i18n] Khởi tạo hệ thống đa ngôn ngữ thành công. Ngôn ngữ hiện tại: ${currentLocale.toUpperCase()}`);

        if (typeof document !== 'undefined' && document.documentElement) {
            document.documentElement.lang = currentLocale;
        }

        scanAndTranslate(document.body);
        checkAndInjectUI();

        if (typeof MutationObserver !== 'undefined' && document.body) {
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                characterData: true
            });
        }

        const handleNavigation = () => {
            setTimeout(() => {
                scanAndTranslate(document.body);
                checkAndInjectUI();
            }, 100);
        };

        window.addEventListener('popstate', handleNavigation);
        if (typeof history !== 'undefined') {
            const originalPushState = history.pushState;
            if (originalPushState) {
                history.pushState = function () {
                    originalPushState.apply(this, arguments);
                    handleNavigation();
                };
            }
            const originalReplaceState = history.replaceState;
            if (originalReplaceState) {
                history.replaceState = function () {
                    originalReplaceState.apply(this, arguments);
                    handleNavigation();
                };
            }
        }
    }

    // =========================================================================
    // 10. EXPOSE GLOBAL i18n API
    // =========================================================================
    window.PostHogI18n = {
        init: init,
        getLocale: () => currentLocale,
        setLocale: setLocale,
        toggleLocale: toggleLocale,
        t: translate,
        registerLocale: registerLocale,
        loadLocale: loadLocale,
        getAvailableLocales: () => [
            { code: 'vi', label: 'Tiếng Việt (Mặc định)', flag: '🇻🇳' },
            { code: 'en', label: 'English', flag: '🇬🇧' }
        ],
        catalogs: localeCatalogs
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
