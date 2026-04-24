# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Chatbot nhắc nhở công việc hàng ngày sử dụng NLP (tiếng Việt). Đồ án cuối kỳ môn Xử lý Ngôn ngữ Tự nhiên.

## Architecture

- **Backend** (`backend/`): Python + FastAPI + hệ thống 3 tầng NLP (LSTM + PhoBERT)
- **Frontend**: Flutter (chưa tạo)
- **Database**: Firebase Firestore (fallback in-memory)
- **NLP**: Hệ thống 3 tầng: LSTM (tự train) → PhoBERT (fine-tune) → fallback
- **Training**: Google Colab notebook (`notebooks/train_chatbot.ipynb`)

## NLP 3-Tier System

```
User input
  ├─→ Tầng 1: LSTM (confidence > 85%) → nhanh, model tự train
  ├─→ Tầng 2: PhoBERT (confidence > 60%) → chính xác, pre-trained tiếng Việt
  └─→ Tầng 3: Chọn model có confidence cao hơn
```

## Backend Structure

```
backend/
├── data/
│   ├── chatbot_model.pth       # LSTM model (from Colab)
│   ├── phobert_model.pth       # PhoBERT model (from Colab)
│   ├── phobert_tokenizer/      # PhoBERT tokenizer (from Colab)
│   ├── model_metadata.json     # Vocab, tags, config (from Colab)
│   └── responses.json          # Response templates (from Colab)
├── models/
│   ├── lstm_model.py           # BiLSTM architecture
│   ├── phobert_model.py        # PhoBERT classifier
│   └── chatbot.py              # 3-tier chatbot inference
├── utils/
│   ├── text_preprocessor.py    # Tokenize tiếng Việt (underthesea)
│   └── entity_extractor.py     # Trích xuất tên task, thời gian
└── main.py                     # FastAPI server + task CRUD
```

## Commands

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run API server
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Dataset & Training

- Dataset: `notebooks/task_management_chatbot_dataset.json` (929 train / 110 test, 34 categories)
- Train trên Google Colab: `notebooks/train_chatbot.ipynb`
- Sau khi train, tải 5 files về `backend/data/`

## 34 Intent Categories

greeting, goodbye, thank_you, bot_identity, create_task, delete_task, update_task,
list_tasks, status_update, search_task, assign_task, deadline_management,
priority_management, statistics, reminder, collaboration, general_help,
complete_all_tasks, delete_all_tasks, confirm_complete, confirm_delete,
task_today, task_overdue, task_upcoming, task_by_category, sort_tasks,
add_note, task_detail, reschedule, set_duration, feeling_overwhelmed,
feeling_productive, motivation, out_of_scope

## API Endpoints

- `POST /chat` — gửi message, nhận intent + response + entities + source (LSTM/PhoBERT)
- `POST /tasks` — tạo task
- `GET /tasks/{user_id}` — lấy danh sách task
- `PUT /tasks/{task_id}` — cập nhật task
- `DELETE /tasks/{task_id}` — xóa task
- `PATCH /tasks/{task_id}/complete` — đánh dấu hoàn thành

## Notes

- Firebase credentials (`firebase_credentials.json`) không commit (trong .gitignore)
- Model files `.pth` không commit (trong .gitignore)
- Backend có pending_actions để xử lý confirm xóa/hoàn thành (không gọi model khi chờ xác nhận)
- Nếu không có Firebase, backend dùng in-memory storage
