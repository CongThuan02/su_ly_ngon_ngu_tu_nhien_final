# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Chatbot quản lý & nhắc nhở công việc hàng ngày sử dụng NLP tiếng Việt. Đồ án cuối kỳ môn Xử lý Ngôn ngữ Tự nhiên.

## Kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────┐
│  Flutter App (flutter_app/)                             │
│  ├── Màn hình Chat (chat với bot)                       │
│  ├── Màn hình Công việc (CRUD tasks)                    │
│  ├── Màn hình Đăng nhập                                 │
│  └── Màn hình Cài đặt                                   │
│        │ HTTP (http://IP:8000)                           │
├────────┼────────────────────────────────────────────────┤
│  FastAPI Backend (backend/)                              │
│  ├── POST /chat → NLP 3 tầng → response                 │
│  ├── CRUD /tasks → SQLite                                │
│  └── pending_actions → xác nhận xóa/hoàn thành          │
│        │                                                 │
│  NLP 3-Tier System:                                      │
│  ├─→ Tầng 1: LSTM tự train (confidence > 85%) → nhanh   │
│  ├─→ Tầng 2: PhoBERT fine-tune (confidence > 60%)       │
│  └─→ Tầng 3: Chọn model confidence cao hơn              │
│        │                                                 │
│  Database: SQLite (backend/data/tasks.db)                │
└─────────────────────────────────────────────────────────┘
```

## Cấu trúc project

```
su_ly_ngon_ngu_tu_nhien_final/
├── CLAUDE.md
├── backend/                          # Python FastAPI server
│   ├── main.py                       # API endpoints + chat logic + pending_actions
│   ├── database.py                   # SQLite CRUD (tasks.db)
│   ├── requirements.txt              # fastapi, torch, transformers, underthesea...
│   ├── models/
│   │   ├── chatbot.py                # Chatbot class: 3-tier predict (LSTM→PhoBERT→fallback)
│   │   ├── lstm_model.py             # BiLSTM architecture (PyTorch)
│   │   └── phobert_model.py          # PhoBERT classifier (FC trên vinai/phobert-base)
│   ├── utils/
│   │   ├── text_preprocessor.py      # tokenize_vi(), text_to_sequence() (underthesea)
│   │   └── entity_extractor.py       # extract_entities(): task_name, time, status
│   └── data/                         # Model files (từ Colab, không commit)
│       ├── chatbot_model.pth         # LSTM model weights
│       ├── phobert_model.pth         # PhoBERT model weights (~515MB)
│       ├── phobert_tokenizer/        # PhoBERT tokenizer files
│       ├── model_metadata.json       # vocab, tags, hyperparams, thresholds
│       ├── responses.json            # response templates theo intent
│       ├── tasks.db                  # SQLite database (auto-created)
│       └── intents.json              # (legacy, không dùng nữa)
│
├── flutter_app/                      # Flutter mobile app
│   ├── pubspec.yaml                  # Dependencies: http, provider, shared_preferences, intl
│   └── lib/
│       ├── main.dart                 # App entry, routing, MultiProvider
│       ├── models/
│       │   ├── chat_message.dart     # ChatMessage (text, isUser, intent, tasks...)
│       │   └── task.dart             # Task model (fromJson)
│       ├── services/
│       │   └── api_service.dart      # HTTP calls tới FastAPI (baseUrl configurable)
│       ├── providers/
│       │   ├── chat_provider.dart    # Chat state: sendMessage(), messages list
│       │   └── task_provider.dart    # Task state: loadTasks(), addTask(), deleteTask()...
│       └── screens/
│           ├── login_screen.dart     # Nhập tên → lưu SharedPreferences → /home
│           ├── home_screen.dart      # BottomNavigationBar (Chat, Công việc, Cài đặt)
│           ├── chat_screen.dart      # Chat UI: bubbles, suggestion chips, task list in bubble
│           ├── task_screen.dart      # 2 tabs (Chưa xong/Đã xong), swipe delete, FAB add
│           └── settings_screen.dart  # User info, about, đăng xuất
│
└── notebooks/                        # Training trên Google Colab
    ├── train_chatbot.ipynb           # Train LSTM + PhoBERT, so sánh, hệ thống 3 tầng
    └── task_management_chatbot_dataset.json  # 967 train / 110 test, 34 categories
```

## Commands

```bash
# === Backend ===
cd backend
source venv/bin/activate              # hoặc tạo: python3 -m venv venv
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# === Flutter ===
cd flutter_app
fvm use 3.38.3                        # dùng fvm quản lý Flutter version
fvm flutter pub get
fvm flutter run -d <device_id>        # xem devices: fvm flutter devices

# === Lưu ý khi test Flutter trên thiết bị thật ===
# Đổi baseUrl trong flutter_app/lib/services/api_service.dart
# từ http://localhost:8000 → http://<IP_máy>:8000
# Backend phải chạy với --host 0.0.0.0
```

## Dataset (34 intent categories)

| Nhóm | Categories |
|------|-----------|
| Chào hỏi | greeting, goodbye, thank_you, bot_identity |
| CRUD task | create_task, delete_task, update_task, list_tasks, status_update |
| Tìm kiếm | search_task, task_by_category, sort_tasks, task_detail |
| Quản lý | deadline_management, priority_management, assign_task, collaboration |
| Thời gian | task_today, task_overdue, task_upcoming, reschedule, set_duration |
| Nhắc nhở | reminder |
| Hàng loạt | complete_all_tasks, delete_all_tasks, confirm_complete, confirm_delete |
| Thống kê | statistics |
| Cảm xúc | feeling_overwhelmed, feeling_productive, motivation |
| Khác | general_help, add_note, out_of_scope |

## API Endpoints

| Method | Path | Mô tả |
|--------|------|-------|
| POST | /chat | Chat: gửi message → intent + response + entities + tasks + source |
| POST | /tasks | Tạo task |
| GET | /tasks/{user_id} | Lấy danh sách task |
| PUT | /tasks/{task_id} | Cập nhật task |
| DELETE | /tasks/{task_id} | Xóa task |
| PATCH | /tasks/{task_id}/complete | Đánh dấu hoàn thành |

### Chat Response format:
```json
{
  "intent": "create_task",
  "confidence": 0.97,
  "response": "Đã tạo công việc 'họp nhóm'.",
  "entities": {"task_name": "họp nhóm", "time": "3 giờ chiều"},
  "source": "LSTM",
  "tasks": [{"id": "abc", "title": "họp nhóm", "is_completed": false}]
}
```

## Luồng xử lý đặc biệt trong backend

### 1. pending_actions (xác nhận xóa/hoàn thành)
Khi user yêu cầu xóa/hoàn thành tất cả → bot hỏi xác nhận → lưu pending_actions[user_id].
Tin nhắn tiếp theo nếu là "có/không" → xử lý trực tiếp, KHÔNG gọi model.

### 2. Entity extraction cho list_tasks
Khi intent là list_tasks, entity_extractor trích xuất `status` từ câu:
- "chưa hoàn thành/chưa xong" → status=pending → lọc task chưa xong
- "đã hoàn thành/đã xong" → status=completed → lọc task đã xong
- Không có → trả tất cả

### 3. Response templates
Backend dùng RESPONSE_TEMPLATES trong chatbot.py với {task_name} placeholder.
Không random từ dataset responses → tránh hiển thị sai tên task.

## Training workflow

1. Sửa dataset: `notebooks/task_management_chatbot_dataset.json`
2. Upload lên Google Colab, chạy `notebooks/train_chatbot.ipynb`
3. Tải 5 files về `backend/data/`:
   - chatbot_model.pth, phobert_model.pth, phobert_tokenizer.zip
   - model_metadata.json, responses.json
4. Giải nén: `unzip phobert_tokenizer.zip -d backend/data/phobert_tokenizer/`
5. Restart backend

## Các vấn đề đã biết (cần train lại model)

- Câu "thêm [tên task] cho [thời gian]" hay bị nhầm sang add_note/status_update khi tên task chứa từ gây nhiễu ("hoàn thành", "sửa lỗi"...)
- Câu "công việc đã hoàn thành" (xem danh sách) hay bị nhầm sang status_update (đánh dấu hoàn thành)
- Đã thêm patterns vào dataset nhưng CHƯA train lại model → cần train lại trên Colab

## Notes

- Database: SQLite tại `backend/data/tasks.db` (auto-created, không commit)
- Model files `.pth` không commit (trong .gitignore)
- Flutter dùng fvm, version 3.38.3
- Backend venv tại `backend/venv/` (Python 3.14)
