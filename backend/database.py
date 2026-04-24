import sqlite3
import os
import uuid
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "tasks.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Tạo bảng tasks nếu chưa có."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            due_time TEXT,
            user_id TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"SQLite database ready: {DB_PATH}")


def _row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "due_time": row["due_time"],
        "user_id": row["user_id"],
        "is_completed": bool(row["is_completed"]),
        "created_at": row["created_at"],
    }


# === CRUD ===

def create_task(title: str, description: str, due_time: str | None, user_id: str) -> dict:
    task_id = str(uuid.uuid4())[:8]
    created_at = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO tasks (id, title, description, due_time, user_id, is_completed, created_at) VALUES (?, ?, ?, ?, ?, 0, ?)",
        (task_id, title, description, due_time, user_id, created_at),
    )
    conn.commit()
    conn.close()
    return {
        "id": task_id, "title": title, "description": description,
        "due_time": due_time, "user_id": user_id,
        "is_completed": False, "created_at": created_at,
    }


def get_tasks_by_user(user_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_task_by_id(task_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def update_task(task_id: str, **fields) -> bool:
    if not fields:
        return False
    # Chuyển is_completed thành integer cho SQLite
    if "is_completed" in fields:
        fields["is_completed"] = int(fields["is_completed"])
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [task_id]
    conn = get_connection()
    cursor = conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def delete_task(task_id: str) -> bool:
    conn = get_connection()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def complete_task(task_id: str) -> bool:
    return update_task(task_id, is_completed=True)


def complete_all_tasks(user_id: str) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE tasks SET is_completed = 1 WHERE user_id = ? AND is_completed = 0",
        (user_id,),
    )
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count


def delete_all_tasks(user_id: str) -> int:
    conn = get_connection()
    cursor = conn.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count


def find_task_by_name(user_id: str, name: str) -> dict | None:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND LOWER(title) LIKE ?",
        (user_id, f"%{name.lower()}%"),
    ).fetchall()
    conn.close()
    return _row_to_dict(rows[0]) if rows else None
