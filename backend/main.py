import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models.chatbot import Chatbot
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


CONFIRM_YES = {"có", "co", "yes", "ừ", "ok", "đồng ý", "chắc chắn", "xác nhận", "có luôn", "ừ đi"}
CONFIRM_NO = {"không", "no", "thôi", "hủy", "cancel", "đừng", "không đâu", "thôi đi"}


def _filter_tasks(tasks: list[dict], status_filter: str | None = None, time_filter: str | None = None) -> list[dict]:
    filtered = tasks
    if status_filter == "completed":
        filtered = [t for t in filtered if t["is_completed"]]
    elif status_filter == "pending":
        filtered = [t for t in filtered if not t["is_completed"]]

    if time_filter:
        normalized_time = time_filter.strip().lower()
        filtered = [
            t for t in filtered
            if (t.get("due_time") or "").strip().lower() == normalized_time
        ]
    return filtered


def _build_followup_response(intent: str, user_id: str, task_name: str, carried_entities: dict | None = None) -> dict:
    carried_entities = carried_entities or {}
    entities = dict(carried_entities)
    entities["task_name"] = task_name

    if intent == "create_task":
        task = db.create_task(task_name, "", entities.get("time"), user_id)
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
            task = db.create_task(task_name, "", result["entities"].get("time"), user_id)
            response_data["response"] = f"Đã tạo công việc '{task_name}'."
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
        tasks = db.get_tasks_by_user(user_id)
        if not tasks:
            response_data["response"] = "Không có công việc nào để xóa."
        else:
            pending_actions[user_id] = {"type": "delete_all"}
            response_data["response"] = f"⚠️ Bạn có chắc muốn XÓA TẤT CẢ {len(tasks)} công việc? (Có/Không)"

    elif intent == "complete_all_tasks":
        tasks = db.get_tasks_by_user(user_id)
        pending_count = sum(1 for t in tasks if not t["is_completed"])
        if pending_count == 0:
            response_data["response"] = "Không có công việc nào cần hoàn thành."
        else:
            pending_actions[user_id] = {"type": "complete_all"}
            response_data["response"] = f"Bạn có chắc muốn đánh dấu hoàn thành TẤT CẢ {pending_count} công việc? (Có/Không)"

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
        count = db.delete_all_tasks(user_id)
        return {"intent": "confirm_delete", "confidence": 1.0,
                "response": f"Đã xóa tất cả {count} công việc."}

    elif action["type"] == "complete_all":
        count = db.complete_all_tasks(user_id)
        return {"intent": "confirm_complete", "confidence": 1.0,
                "response": f"Đã đánh dấu hoàn thành {count} công việc!"}

    return {"intent": "unknown", "confidence": 0.0, "response": "Có lỗi xảy ra."}


# ============ Task REST Endpoints ============
@app.post("/tasks")
async def create_task(task: TaskCreateSchema):
    return db.create_task(task.title, task.description, task.due_time, task.user_id)


@app.get("/tasks/{user_id}")
async def get_tasks(user_id: str):
    return {"tasks": db.get_tasks_by_user(user_id)}


@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task: TaskUpdateSchema):
    existing = db.get_task_by_id(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = {k: v for k, v in task.model_dump().items() if v is not None}
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
