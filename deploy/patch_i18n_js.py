import os

target_path = '/home/opc/posthog-deployment/i18n/posthog-i18n.js'

with open(target_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """            if (norm.startsWith('What can I help you with?')) {
                return norm.replace('What can I help you with?', 'Tôi có thể giúp gì cho bạn?').replace('/ for commands', '/ để xem lệnh');
            }"""

replacement = """            if (norm.startsWith('What can I help you with?')) {
                return norm.replace('What can I help you with?', 'Tôi có thể giúp gì cho bạn?').replace('/ for commands', '/ để xem lệnh');
            }

            // Chuỗi số lượng bản ghi hoạt động gần đây
            const recentlyMatch = norm.match(/^(\\d+)\\s+recently active(?:\\s*(?:recordings?|Bản ghi phiên))?$/i);
            if (recentlyMatch) {
                return recentlyMatch[1] + ' bản ghi hoạt động gần đây';
            }
            if (/^recently active(?:\\s*(?:recordings?|Bản ghi phiên))?$/i.test(norm)) {
                return 'bản ghi hoạt động gần đây';
            }

            // Chuỗi thời gian tương đối: "Last 3 days", "Last 24 hours", "Last 1 month"
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

            // Chuỗi thời lượng hoạt động: "> 5 active seconds", ">= 10 active minutes"
            const activeTimeMatch = norm.match(/^(>=?|<=?|>|<)\\s*(\\d+)\\s+active\\s+(seconds?|minutes?|hours?)$/i);
            if (activeTimeMatch) {
                const op = activeTimeMatch[1];
                const num = activeTimeMatch[2];
                const unit = activeTimeMatch[3].toLowerCase();
                const unitVi = unit.startsWith('sec') ? 'giây hoạt động' : (unit.startsWith('min') ? 'phút hoạt động' : 'giờ hoạt động');
                return op + ' ' + num + ' ' + unitVi;
            }"""

if target in content:
    content = content.replace(target, replacement)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Updated posthog-i18n.js with replay rules')
else:
    print('ERROR: target string not found in posthog-i18n.js')
