import os
import re
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models.chatbot import Chatbot
from utils.time_parser import VN_TZ
from utils.time_parser import parse_due_time
import database as db

# ============ Globals ============
chatbot: Chatbot | None = None
pending_actions: dict[str, dict] = {}
waiting_for: dict[str, dict] = {}


# ============ Lifespan ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot

    # Init SQLite
    db.init_db()

    # Load chatbot model
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    chatbot = Chatbot(data_dir)
    print("Chatbot model loaded!")

    yield


# ============ App ============
app = FastAPI(title="Task Reminder Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Schemas ============
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"


class ChatResponse(BaseModel):
    intent: str
    confidence: float
    response: str
    entities: dict = Field(default_factory=dict)
    source: str = ""
    tasks: list[dict] = Field(default_factory=list)


class TaskCreateSchema(BaseModel):
    title: str
    description: str = ""
    due_time: str | None = None
    user_id: str = "default"


class TaskUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    due_time: str | None = None
    is_completed: bool | None = None


def _schema_dump_set_fields(schema: BaseModel) -> dict:
    """Return only submitted fields on both Pydantic v1 and v2."""
    if hasattr(schema, "model_dump"):
        return schema.model_dump(exclude_unset=True)
    return schema.dict(exclude_unset=True)


def _normalize_due_time(due_time: str | None) -> str | None:
    if due_time is None:
        return None

    try:
        datetime.fromisoformat(due_time)
        return due_time
    except ValueError:
        return parse_due_time(due_time) or due_time


CONFIRM_YES = {"có", "co", "yes", "ừ", "ok", "đồng ý", "chắc chắn", "xác nhận", "có luôn", "ừ đi"}
CONFIRM_NO = {"không", "no", "thôi", "hủy", "cancel", "đừng", "không đâu", "thôi đi"}
def _filter_tasks(tasks: list[dict], status_filter: str | None = None, time_filter: str | None = None) -> list[dict]:
    filtered = tasks
    if status_filter == "completed":
        filtered = [t for t in filtered if t["is_completed"]]
    elif status_filter == "pending":
        filtered = [t for t in filtered if not t["is_completed"]]

    if time_filter:
        target_date = _date_from_due_time(time_filter)
        if target_date:
            filtered = [
                t for t in filtered
                if _date_from_due_time(t.get("due_time")) == target_date
            ]
        else:
            normalized_time = time_filter.strip().lower()
            filtered = [
                t for t in filtered
                if (t.get("due_time") or "").strip().lower() == normalized_time
            ]
    return filtered


def _date_from_due_time(value: str | None):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value).astimezone(VN_TZ).date()
    except ValueError:
        parsed_value = parse_due_time(value)
        if not parsed_value:
            return None
        try:
            return datetime.fromisoformat(parsed_value).astimezone(VN_TZ).date()
        except ValueError:
            return None


def _format_due_time(value: str | None) -> str:
    if not value:
        return "chưa có ngày giờ cụ thể"
    try:
        due = datetime.fromisoformat(value).astimezone(VN_TZ)
        return due.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return value


def _extract_lookup_task_name(message: str, entities: dict) -> str | None:
    task_name = entities.get("task_name")
    if task_name:
        return task_name

    text = message.lower().strip()
    patterns = [
        r"bao giờ\s+(.+?)\s+cần thanh toán",
        r"khi nào\s+(.+?)\s+cần thanh toán",
        r"(.+?)\s+cần thanh toán\s+(?:bao giờ|khi nào|lúc nào|ngày nào)",
        r"hạn\s+(.+?)\s+(?:là|vào|ngày|bao giờ|khi nào)",
        r"deadline\s+(.+?)\s+(?:là|vào|ngày|bao giờ|khi nào)",
        r"(.+?)\s+đến hạn\s+(?:bao giờ|khi nào|ngày nào)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            candidate = re.sub(r"\s+", " ", match.group(1)).strip()
            if candidate:
                return candidate

    replacements = [
        "bao giờ", "khi nào", "lúc nào", "ngày nào", "hạn", "deadline",
        "đến hạn", "cần", "phải", "sẽ", "làm", "xong", "hoàn thành",
        "thanh toán lúc nào", "thanh toán khi nào", "cần thanh toán",
        "cho tôi biết", "xem", "chi tiết", "công việc", "task", "việc",
        "là", "vậy", "nhỉ", "?", "ạ", "giúp tôi",
    ]
    for token in replacements:
        text = text.replace(token, " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _handle_task_lookup(intent: str, message: str, user_id: str, entities: dict) -> dict | None:
    task_name = _extract_lookup_task_name(message, entities)
    if not task_name:
        return None

    task = db.find_task_by_name(user_id, task_name)
    if not task and not task_name.startswith("thanh toán "):
        task = db.find_task_by_name(user_id, f"thanh toán {task_name}")
    if not task and task_name.startswith("thanh toán "):
        task = db.find_task_by_name(user_id, task_name.replace("thanh toán ", "", 1))

    if not task:
        return {
            "intent": intent,
            "confidence": 1.0,
            "response": f"Không tìm thấy công việc liên quan đến '{task_name}'.",
            "entities": {"task_name": task_name},
            "source": "task_lookup",
            "tasks": [],
        }

    due_label = _format_due_time(task.get("due_time"))
    status = "đã hoàn thành" if task["is_completed"] else "chưa hoàn thành"
    return {
        "intent": intent,
        "confidence": 1.0,
        "response": f"Công việc '{task['title']}' cần làm vào {due_label}. Trạng thái: {status}.",
        "entities": {"task_name": task["title"]},
        "source": "task_lookup",
        "tasks": [task],
    }


def _build_followup_response(intent: str, user_id: str, task_name: str, carried_entities: dict | None = None) -> dict:
    carried_entities = carried_entities or {}
    entities = dict(carried_entities)
    entities["task_name"] = task_name

    if intent == "create_task":
        due_time = parse_due_time(entities.get("time"))
        task = db.create_task(task_name, "", due_time, user_id)
        return {
            "intent": intent,
            "confidence": 1.0,
            "response": f"Đã tạo công việc '{task_name}'.",
            "entities": entities,
            "source": "follow_up",
            "tasks": [task],
        }

    if intent == "status_update":
        task = db.find_task_by_name(user_id, task_name)
        if task:
            db.complete_task(task["id"])
            return {
                "intent": intent,
                "confidence": 1.0,
                "response": f"Đã đánh dấu '{task['title']}' hoàn thành!",
                "entities": entities,
                "source": "follow_up",
                "tasks": [db.get_task_by_id(task["id"])],
            }
        return {
            "intent": intent,
            "confidence": 1.0,
            "response": f"Không tìm thấy công việc '{task_name}'.",
            "entities": entities,
            "source": "follow_up",
        }

    if intent == "delete_task":
        task = db.find_task_by_name(user_id, task_name)
        if task:
            pending_actions[user_id] = {"type": "delete", "task_id": task["id"], "task_name": task["title"]}
            return {
                "intent": intent,
                "confidence": 1.0,
                "response": f"Bạn có chắc muốn xóa '{task['title']}' không? (Có/Không)",
                "entities": entities,
                "source": "follow_up",
            }
        return {
            "intent": intent,
            "confidence": 1.0,
            "response": f"Không tìm thấy công việc '{task_name}'.",
            "entities": entities,
            "source": "follow_up",
        }

    if intent == "update_task":
        return {
            "intent": intent,
            "confidence": 1.0,
            "response": f"Bạn muốn sửa gì cho '{task_name}'?",
            "entities": entities,
            "source": "follow_up",
        }

    return {
        "intent": intent,
        "confidence": 1.0,
        "response": "Đã ghi nhận.",
        "entities": entities,
        "source": "follow_up",
    }


# ============ Chat Endpoint ============
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Chatbot chưa sẵn sàng")

    user_id = request.user_id
    message_lower = request.message.lower().strip()

    # === Xử lý xác nhận nếu đang chờ ===
    if user_id in pending_actions:
        action = pending_actions[user_id]
        if message_lower in CONFIRM_YES:
            del pending_actions[user_id]
            return ChatResponse(**_handle_confirm_yes(action, user_id))
        elif message_lower in CONFIRM_NO:
            del pending_actions[user_id]
            return ChatResponse(intent="confirm_cancel", confidence=1.0,
                                response="Đã hủy. Không thay đổi gì.")
        del pending_actions[user_id]

    # === Xử lý chờ người dùng nhập tên task ===
    if user_id in waiting_for:
        followup = waiting_for.pop(user_id)
        return ChatResponse(**_build_followup_response(
            followup["intent"],
            user_id,
            request.message.strip(),
            followup.get("entities"),
        ))

    result = chatbot.get_response(request.message)
    intent = result["intent"]

    response_data = {
        "intent": intent,
        "confidence": result["confidence"],
        "response": result["response"],
        "entities": result.get("entities", {}),
        "source": result.get("source", ""),
    }

    # === Xử lý từng intent ===
    if intent == "create_task":
        task_name = result["entities"].get("task_name")
        if task_name:
            due_time = parse_due_time(request.message) or parse_due_time(result["entities"].get("time"))
            task = db.create_task(task_name, "", due_time, user_id)
            response_data["response"] = f"Đã tạo công việc '{task_name}'."
            if due_time:
                response_data["entities"]["due_time"] = due_time
            response_data["tasks"] = [task]
        else:
            waiting_for[user_id] = {"intent": intent, "entities": result.get("entities", {})}
            if result["entities"].get("time"):
                response_data["response"] = f"Bạn muốn tạo công việc gì cho {result['entities']['time']}?"
            else:
                response_data["response"] = "Bạn muốn thêm công việc gì?"

    elif intent == "list_tasks":
        all_tasks = db.get_tasks_by_user(user_id)
        status_filter = result["entities"].get("status")
        time_filter = result["entities"].get("time")
        tasks = _filter_tasks(all_tasks, status_filter, time_filter)
        if status_filter == "completed":
            label = "đã hoàn thành"
        elif status_filter == "pending":
            label = "chưa hoàn thành"
        else:
            label = ""
        response_data["tasks"] = tasks
        if not tasks:
            if time_filter:
                response_data["response"] = f"Không có công việc nào cho {time_filter}."
            elif status_filter:
                response_data["response"] = f"Không có công việc nào {label}."
            else:
                response_data["response"] = "Bạn chưa có công việc nào."
        else:
            if time_filter:
                response_data["response"] = f"Danh sách công việc {time_filter}:"
            elif status_filter:
                response_data["response"] = f"Có {len(tasks)} công việc {label}:"
            else:
                response_data["response"] = "Đây là danh sách công việc của bạn:"

    elif intent == "task_upcoming":
        all_tasks = db.get_tasks_by_user(user_id)
        time_filter = result["entities"].get("time")
        tasks = _filter_tasks(all_tasks, result["entities"].get("status"), time_filter)
        response_data["tasks"] = tasks
        if not tasks:
            if time_filter:
                response_data["response"] = f"Không có công việc nào cho {time_filter}."
            else:
                response_data["response"] = "Không có công việc sắp tới."
        else:
            if time_filter:
                response_data["response"] = f"Danh sách công việc {time_filter}:"
            else:
                response_data["response"] = f"Có {len(tasks)} công việc sắp tới:"

    elif intent in {"search_task", "task_detail", "deadline_management"}:
        lookup = _handle_task_lookup(intent, request.message, user_id, result.get("entities", {}))
        if lookup:
            return ChatResponse(**lookup)

    elif intent == "status_update":
        task_name = result["entities"].get("task_name")
        if task_name:
            task = db.find_task_by_name(user_id, task_name)
            if task:
                db.complete_task(task["id"])
                response_data["response"] = f"Đã đánh dấu '{task['title']}' hoàn thành!"
            else:
                response_data["response"] = f"Không tìm thấy công việc '{task_name}'."
        else:
            waiting_for[user_id] = {"intent": intent, "entities": result.get("entities", {})}
            response_data["response"] = "Công việc nào đã hoàn thành?"

    elif intent == "delete_task":
        task_name = result["entities"].get("task_name")
        if task_name:
            task = db.find_task_by_name(user_id, task_name)
            if task:
                pending_actions[user_id] = {"type": "delete", "task_id": task["id"], "task_name": task["title"]}
                response_data["response"] = f"Bạn có chắc muốn xóa '{task['title']}' không? (Có/Không)"
            else:
                response_data["response"] = f"Không tìm thấy công việc '{task_name}'."
        else:
            waiting_for[user_id] = {"intent": intent, "entities": result.get("entities", {})}
            response_data["response"] = "Bạn muốn xóa công việc nào?"

    elif intent == "update_task":
        task_name = result["entities"].get("task_name")
        if task_name:
            response_data["response"] = f"Bạn muốn sửa gì cho '{task_name}'?"
        else:
            waiting_for[user_id] = {"intent": intent, "entities": result.get("entities", {})}
            response_data["response"] = "Bạn muốn cập nhật công việc nào?"

    elif intent == "delete_all_tasks":
        time_filter = result["entities"].get("time")
        all_tasks = db.get_tasks_by_user(user_id)
        tasks = _filter_tasks(all_tasks, time_filter=time_filter) if time_filter else all_tasks
        if not tasks:
            if time_filter:
                response_data["response"] = f"Không có công việc nào cho {time_filter} để xóa."
            else:
                response_data["response"] = "Không có công việc nào để xóa."
        else:
            pending_actions[user_id] = {
                "type": "delete_all",
                "task_ids": [task["id"] for task in tasks],
                "time_filter": time_filter,
            }
            if time_filter:
                response_data["response"] = f"⚠️ Bạn có chắc muốn xóa {len(tasks)} công việc cho {time_filter}? (Có/Không)"
            else:
                response_data["response"] = f"⚠️ Bạn có chắc muốn XÓA TẤT CẢ {len(tasks)} công việc? (Có/Không)"
            response_data["tasks"] = tasks

    elif intent == "complete_all_tasks":
        time_filter = result["entities"].get("time")
        all_tasks = db.get_tasks_by_user(user_id)
        tasks = _filter_tasks(all_tasks, "pending", time_filter)
        pending_count = sum(1 for t in tasks if not t["is_completed"])
        if pending_count == 0:
            if time_filter:
                response_data["response"] = f"Không có công việc nào cho {time_filter} cần hoàn thành."
            else:
                response_data["response"] = "Không có công việc nào cần hoàn thành."
        else:
            pending_actions[user_id] = {
                "type": "complete_all",
                "task_ids": [task["id"] for task in tasks if not task["is_completed"]],
                "time_filter": time_filter,
            }
            if time_filter:
                response_data["response"] = f"Bạn có chắc muốn đánh dấu hoàn thành {pending_count} công việc cho {time_filter}? (Có/Không)"
            else:
                response_data["response"] = f"Bạn có chắc muốn đánh dấu hoàn thành TẤT CẢ {pending_count} công việc? (Có/Không)"
            response_data["tasks"] = tasks

    elif intent == "statistics":
        tasks = db.get_tasks_by_user(user_id)
        total = len(tasks)
        done = sum(1 for t in tasks if t["is_completed"])
        pct = done / total * 100 if total > 0 else 0
        response_data["response"] = f"Thống kê: {total} tổng | {done} hoàn thành ({pct:.0f}%) | {total - done} chưa xong"

    elif intent == "task_today":
        tasks = db.get_tasks_by_user(user_id)
        pending = _filter_tasks(tasks, "pending", result["entities"].get("time") or "hôm nay")
        response_data["tasks"] = pending
        if not pending:
            response_data["response"] = "Hôm nay bạn chưa có việc gì hoặc đã hoàn thành tất cả!"
        else:
            response_data["response"] = f"Bạn có {len(pending)} công việc chưa xong:"

    return ChatResponse(**response_data)



def _handle_confirm_yes(action: dict, user_id: str) -> dict:
    if action["type"] == "delete":
        db.delete_task(action["task_id"])
        return {"intent": "confirm_delete", "confidence": 1.0,
                "response": f"Đã xóa '{action['task_name']}'."}

    elif action["type"] == "delete_all":
        task_ids = action.get("task_ids")
        if task_ids is not None:
            count = sum(1 for task_id in task_ids if db.delete_task(task_id))
            time_filter = action.get("time_filter")
            if time_filter:
                return {"intent": "confirm_delete", "confidence": 1.0,
                        "response": f"Đã xóa {count} công việc cho {time_filter}."}
        else:
            count = db.delete_all_tasks(user_id)
        return {"intent": "confirm_delete", "confidence": 1.0,
                "response": f"Đã xóa tất cả {count} công việc."}

    elif action["type"] == "complete_all":
        task_ids = action.get("task_ids")
        if task_ids is not None:
            count = sum(1 for task_id in task_ids if db.complete_task(task_id))
            time_filter = action.get("time_filter")
            if time_filter:
                return {"intent": "confirm_complete", "confidence": 1.0,
                        "response": f"Đã đánh dấu hoàn thành {count} công việc cho {time_filter}!"}
        else:
            count = db.complete_all_tasks(user_id)
        return {"intent": "confirm_complete", "confidence": 1.0,
                "response": f"Đã đánh dấu hoàn thành {count} công việc!"}

    return {"intent": "unknown", "confidence": 0.0, "response": "Có lỗi xảy ra."}


# ============ Task REST Endpoints ============
@app.post("/tasks")
async def create_task(task: TaskCreateSchema):
    due_time = _normalize_due_time(task.due_time)
    return db.create_task(task.title, task.description, due_time, task.user_id)


@app.get("/tasks/{user_id}")
async def get_tasks(user_id: str):
    return {"tasks": db.get_tasks_by_user(user_id)}


@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task: TaskUpdateSchema):
    existing = db.get_task_by_id(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = _schema_dump_set_fields(task)
    if "due_time" in update_data:
        update_data["due_time"] = _normalize_due_time(update_data["due_time"])
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    db.update_task(task_id, **update_data)
    return {"message": "Task updated", "id": task_id}


@app.delete("/tasks/{task_id}")
async def delete_task_endpoint(task_id: str):
    if not db.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted", "id": task_id}


@app.patch("/tasks/{task_id}/complete")
async def complete_task_endpoint(task_id: str):
    if not db.complete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task marked as completed", "id": task_id}
