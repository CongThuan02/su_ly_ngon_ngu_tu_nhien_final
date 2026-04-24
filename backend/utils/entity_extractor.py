import re


INTENT_ALIASES = {
    "them_cong_viec": "create_task",
    "xoa_cong_viec": "delete_task",
    "sua_cong_viec": "update_task",
    "xem_cong_viec": "list_tasks",
    "hoan_thanh_cong_viec": "complete_task",
    "nhac_nho": "set_reminder",
    "hoi_trang_thai": "task_status",
}


# Các từ khóa trigger theo intent - sau từ khóa này là tên công việc
TASK_TRIGGERS = {
    "create_task": [
        "tạo công việc:",
        "tạo công việc",
        "thêm công việc:",
        "thêm công việc",
        "tạo task:",
        "tạo task",
        "thêm task:",
        "thêm task",
        "add task:",
        "add task",
    ],
    "them_cong_viec": [
        "thêm công việc mới", "thêm công việc", "tạo công việc mới",
        "thêm việc mới cho tôi", "thêm cho tôi công việc",
        "tạo cho tôi một việc", "thêm vào danh sách công việc",
        "tôi muốn thêm công việc", "tôi muốn thêm một việc",
        "tôi muốn tạo task", "tôi cần thêm việc",
        "tôi có việc mới", "cho tôi thêm việc",
        "nhờ thêm công việc", "thêm việc cần làm",
        "thêm lịch làm việc", "ghi lại công việc",
        "ghi nhớ công việc", "lưu công việc",
        "bổ sung công việc", "ghi thêm việc",
        "thêm việc", "thêm task", "tạo task mới",
        "tạo việc mới", "thêm nhiệm vụ", "tạo nhiệm vụ",
        "tạo công việc", "add task",
    ],
    "delete_task": [
        "xóa công việc:",
        "xóa công việc",
        "xóa task:",
        "xóa task",
        "delete task:",
        "delete task",
        "remove task:",
        "remove task",
    ],
    "xoa_cong_viec": [
        "xóa giúp tôi công việc", "xóa công việc giúp tôi",
        "tôi muốn xóa công việc", "tôi muốn bỏ việc này",
        "tôi không cần việc này nữa",
        "xóa bỏ công việc", "hủy bỏ công việc", "loại bỏ công việc",
        "xóa đi công việc", "xóa bớt công việc",
        "xóa khỏi danh sách", "xóa việc cần làm",
        "bỏ task này đi", "bỏ đi việc này",
        "xóa công việc", "xóa việc này", "xóa việc",
        "bỏ công việc", "xóa task", "hủy công việc",
        "xóa nhiệm vụ", "bỏ nhiệm vụ",
        "hủy task", "remove task", "delete task",
    ],
    "update_task": [
        "sửa công việc:",
        "sửa công việc",
        "cập nhật công việc:",
        "cập nhật công việc",
        "update task:",
        "update task",
        "edit task:",
        "edit task",
    ],
    "sua_cong_viec": [
        "sửa lại công việc giúp tôi", "tôi muốn sửa công việc",
        "thay đổi nội dung công việc", "thay đổi thời gian công việc",
        "đổi thông tin công việc", "tôi muốn thay đổi việc",
        "tôi muốn đổi tên việc", "tôi cần sửa việc",
        "chỉnh sửa công việc", "cập nhật công việc",
        "thay đổi công việc", "chỉnh lại công việc",
        "đổi tên công việc", "sửa lại nhiệm vụ",
        "cập nhật nhiệm vụ", "sửa thông tin công việc",
        "sửa giúp tôi công việc", "cập nhật lại task",
        "chỉnh lại nội dung", "đổi lại công việc",
        "sửa công việc", "sửa task", "edit task",
        "update task", "chỉnh sửa task",
    ],
    "complete_task": [
        "hoàn thành công việc:",
        "hoàn thành công việc",
        "đánh dấu hoàn thành:",
        "đánh dấu hoàn thành",
        "complete task:",
        "complete task",
        "mark done:",
        "mark done",
    ],
    "hoan_thanh_cong_viec": [
        "làm xong việc này rồi", "tôi đã làm xong việc",
        "công việc đã hoàn tất", "hoàn thành công việc",
        "đánh dấu hoàn thành", "hoàn tất công việc",
        "hoàn thành task", "hoàn thành nhiệm vụ",
        "đánh dấu xong", "đánh dấu đã làm",
        "tôi đã hoàn thành", "tôi đã xong",
        "tôi làm xong rồi", "tôi hoàn thành rồi",
        "đã hoàn thành", "đã làm xong", "đã xong việc",
        "việc này xong rồi", "việc đã xong", "xong việc rồi",
        "xong rồi", "xong hết rồi", "đã xong tất cả",
        "done", "complete task", "finish task", "mark done",
    ],
    "status_update": [
        "hoàn thành công việc", "hoàn thành task", "hoàn thành việc", "hoàn thành",
        "đánh dấu hoàn thành", "đánh dấu xong", "đánh dấu done",
        "done task", "done", "finish task", "complete task", "mark done",
        "xong task", "xong việc", "xong",
        "tôi đã hoàn thành", "tôi đã xong", "tôi đã làm xong",
        "đã hoàn thành", "đã làm xong", "đã xong",
        "tôi đang làm", "đang làm", "bắt đầu làm", "bắt đầu",
    ],
    "set_reminder": [
        "nhắc tôi:",
        "nhắc tôi",
        "đặt nhắc nhở:",
        "đặt nhắc nhở",
        "set reminder:",
        "set reminder",
    ],
    "nhac_nho": [
        "đặt thông báo nhắc nhở", "tạo thông báo nhắc",
        "đặt báo thức công việc", "đặt hẹn nhắc nhở",
        "tôi muốn được nhắc", "đặt giờ nhắc nhở",
        "nhắc tôi vào lúc", "nhắc tôi vào",
        "nhắc nhở lúc", "nhắc tôi lúc",
        "hẹn giờ nhắc", "hẹn nhắc việc",
        "nhắc nhở tôi", "đặt nhắc nhở", "nhắc tôi",
        "tạo nhắc nhở", "nhắc việc", "đặt lời nhắc",
        "nhắc giúp tôi", "tạo lời nhắc",
        "nhắc tôi làm", "nhớ nhắc tôi",
        "báo nhắc tôi",
        "reminder", "set reminder",
    ],
}

# Các từ nối thừa cần loại bỏ
FILLER_WORDS = ["là:", "là", ":", "về việc", "về", "cho tôi", "giúp tôi", "việc"]
GENERIC_TASK_NAMES = {
    "mới", "công việc mới", "task mới", "việc mới", "một công việc", "một việc",
    "một task", "công việc", "task", "việc",
}


def extract_entities(text: str, intent: str) -> dict:
    """Trích xuất entity (tên công việc, thời gian) từ câu nói."""
    text_lower = text.lower().strip()
    entities = {}
    normalized_intent = INTENT_ALIASES.get(intent, intent)

    # === Trích xuất thời gian ===
    time_patterns = [
        r"((?:ngày\s*)?\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)",
        r"(ngày\s+\d{1,2})(?![/-])",
        r"(?:lúc|vào|vào lúc)\s+(\d{1,2}\s*(?:giờ|h|:)\s*\d{0,2}\s*(?:sáng|chiều|tối|phút)?)",
        r"(\d{1,2}\s*(?:giờ|h|:)\s*\d{0,2}\s*(?:sáng|chiều|tối|phút)?)",
        r"(ngày mai|hôm nay|hôm qua|chiều nay|sáng mai|tối nay|tuần sau|tháng sau)",
    ]

    for pattern in time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            entities["time"] = match.group(1) if match.lastindex else match.group(0)
            text_lower = text_lower[:match.start()] + text_lower[match.end():]
            text_lower = text_lower.strip()
            break

    # === Trích xuất trạng thái lọc (cho list_tasks) ===
    if intent in {"list_tasks", "task_today", "task_upcoming"}:
        completed_keywords = ["đã hoàn thành", "đã xong", "hoàn thành", "đã làm xong", "completed", "done"]
        pending_keywords = ["chưa hoàn thành", "chưa xong", "chưa làm", "chưa bắt đầu", "pending", "chưa done"]
        for kw in pending_keywords:
            if kw in text_lower:
                entities["status"] = "pending"
                break
        else:
            for kw in completed_keywords:
                if kw in text_lower:
                    entities["status"] = "completed"
                    break

    # === Trích xuất tên công việc ===
    triggers = TASK_TRIGGERS.get(normalized_intent, []) + TASK_TRIGGERS.get(intent, [])

    for trigger in triggers:
        idx = text_lower.find(trigger)
        if idx != -1:
            after = text_lower[idx + len(trigger):].strip()
            # Loại bỏ từ nối thừa
            for filler in sorted(FILLER_WORDS, key=len, reverse=True):
                if after.startswith(filler + " "):
                    after = after[len(filler):].strip()
                elif after == filler:
                    after = ""
            after = re.sub(r"^((?:ngày\s*)?\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\s+", "", after).strip()
            after = re.sub(r"^(ngày\s+\d{1,2})(?![/-])\s+", "", after).strip()
            after = re.sub(r"^(hôm nay|ngày mai|hôm qua|chiều nay|sáng mai|tối nay|tuần sau|tháng sau)\s+", "", after).strip()
            after = re.sub(r"\s+(cho|vào|lúc|là)$", "", after).strip()
            if after and after not in GENERIC_TASK_NAMES:
                entities["task_name"] = after
            break

    return entities
