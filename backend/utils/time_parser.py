import re
from datetime import datetime, time, timedelta
from typing import Optional
from zoneinfo import ZoneInfo


VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
DEFAULT_TIME = time(9, 0)


def parse_due_time(text: Optional[str]) -> Optional[str]:
    """Parse simple Vietnamese date/time phrases into ISO-8601 local datetime."""
    if not text:
        return None

    raw = text.lower().strip()
    now = datetime.now(VN_TZ)
    due_date = None
    due_time = None

    if any(token in raw for token in ["ngày mai", "mai"]):
        due_date = now.date() + timedelta(days=1)
    elif "hôm nay" in raw or "chiều nay" in raw or "tối nay" in raw or "sáng nay" in raw:
        due_date = now.date()
    elif "tuần sau" in raw:
        due_date = now.date() + timedelta(days=7)

    date_match = re.search(r"(?:ngày\s*)?(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?", raw)
    if date_match:
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year_text = date_match.group(3)
        year = int(year_text) if year_text else now.year
        if year < 100:
            year += 2000
        try:
            due_date = datetime(year, month, day, tzinfo=VN_TZ).date()
        except ValueError:
            pass
    else:
        day_match = re.search(r"ngày\s+(\d{1,2})(?!\s*[/-])", raw)
        if day_match:
            day = int(day_match.group(1))
            month = now.month
            year = now.year
            try:
                candidate = datetime(year, month, day, tzinfo=VN_TZ).date()
                if candidate < now.date():
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
                    candidate = datetime(year, month, day, tzinfo=VN_TZ).date()
                due_date = candidate
            except ValueError:
                pass

    time_match = None
    for match in re.finditer(
        r"(\d{1,2})(?:\s*(?::|h|giờ)\s*(\d{1,2})?)?\s*(sáng|chiều|tối|đêm)?",
        raw,
    ):
        if any(marker in match.group(0) for marker in [":", "h", "giờ", "sáng", "chiều", "tối", "đêm"]):
            time_match = match
            break

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        period = time_match.group(3)

        if period in {"chiều", "tối", "đêm"} and hour < 12:
            hour += 12
        elif period == "sáng" and hour == 12:
            hour = 0

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            due_time = time(hour, minute)

    if due_date is None and due_time is None:
        return None

    due_date = due_date or now.date()
    due_time = due_time or DEFAULT_TIME
    return datetime.combine(due_date, due_time, tzinfo=VN_TZ).isoformat()
