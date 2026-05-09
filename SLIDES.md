---
title: "Chatbot Quản lý & Nhắc nhở Công việc bằng NLP Tiếng Việt"
subtitle: "Đồ án cuối kỳ — Môn Xử lý Ngôn ngữ Tự nhiên"
author: "Hoàng Thuận"
date: "2026"
---

# Mở đầu

## Bài toán

- Quản lý công việc bằng app to-do truyền thống → nhiều thao tác thủ công
- Người dùng phổ thông và người lớn tuổi gặp khó khăn
- **Giải pháp:** giao tiếp bằng câu nói tiếng Việt tự nhiên
  - *"nhắc tôi họp 3 giờ chiều mai"*
  - *"xóa hết công việc đi"*

## Mục tiêu đề tài

1. Xây dựng chatbot tiếng Việt cho **34 ý định** quản lý công việc
2. So sánh **2 mô hình NLP**: BiLSTM tự train + PhoBERT fine-tune
3. Đề xuất **kiến trúc 3 tầng** kết hợp 2 mô hình
4. Triển khai end-to-end: Backend FastAPI + App Flutter (iOS / Android / Web)

## Phạm vi

- **Ngôn ngữ:** tiếng Việt
- **Domain:** quản lý công việc cá nhân (CRUD, nhắc nhở, tìm kiếm, thống kê)
- **Đơn người dùng** mỗi phiên (single-user-per-session)

# Cơ sở lý thuyết

## Hai bài toán nền tảng của Chatbot

**1. Phân loại ý định (Intent Classification)**
- Đầu vào: câu tiếng Việt
- Đầu ra: 1 nhãn trong 34 ý định
- Bài toán phân loại văn bản đa lớp

**2. Trích xuất thực thể (Entity Extraction)**
- `task_name` — tên công việc
- `time` — thời gian
- `status` — trạng thái lọc

## Mô hình BiLSTM

- **Long Short-Term Memory** — RNN có cổng (Hochreiter & Schmidhuber, 1997)
- **Bi-directional**: đọc câu cả hai chiều
- Phù hợp dataset nhỏ–trung bình
- Inference nhanh, không cần GPU

```
Token ids → Embedding → BiLSTM → Dense → Softmax
```

## Mô hình PhoBERT

- BERT pre-trained chuyên cho **tiếng Việt** (VinAI, 2020)
- Train trên 20GB văn bản tiếng Việt
- Kiến trúc RoBERTa-base, 135M tham số
- Dùng VnCoreNLP để tách từ → SentencePiece BPE
- Fine-tune classifier head trên dataset domain

# Phương pháp đề xuất

## Kiến trúc tổng thể

```
┌──────────────────────────────────┐
│  Flutter App (iOS/Android/Web)   │
└────────────┬─────────────────────┘
             │ HTTP / JSON
┌────────────┴─────────────────────┐
│  FastAPI Backend                 │
│   ├─ POST /chat → NLP 3 tầng     │
│   ├─ CRUD /tasks → SQLite        │
│   └─ pending_actions middleware  │
└──────────────────────────────────┘
```

## Dataset tự xây dựng

| Tập | Số mẫu |
|-----|--------|
| Training | **996** |
| Test | **121** |
| Tổng | **1.117** |

- 34 ý định, chia 9 nhóm chức năng
- Mỗi mẫu là cặp `(text, intent)`

## 9 nhóm ý định

| Nhóm | Ví dụ intent |
|------|-------------|
| Chào hỏi | greeting, goodbye, thank_you |
| CRUD task | create_task, delete_task, list_tasks |
| Tìm kiếm | search_task, sort_tasks, task_detail |
| Quản lý | deadline_management, priority_management |
| Thời gian | task_today, task_overdue, task_upcoming |
| Nhắc nhở | reminder |
| Hàng loạt | delete_all_tasks, confirm_delete |
| Thống kê | statistics |
| Cảm xúc | feeling_overwhelmed, motivation |

## Pipeline tiền xử lý

```
Câu thô
   ↓
Lowercase
   ↓
underthesea.word_tokenize  ← tách từ tiếng Việt
   ↓
Loại ký tự đặc biệt
   ↓
text_to_sequence (pad/truncate đến 30 token)
   ↓
Tensor đầu vào mô hình
```

## BiLSTM — siêu tham số

| Tham số | Giá trị |
|---------|---------|
| Vocab size | 782 |
| Embedding dim | 256 |
| Hidden dim | 256 |
| Số lớp LSTM | 2 |
| Dropout | 0.3 |
| Max length | 30 |
| Threshold tin cậy | **0.85** |

Kích thước file: ~11 MB · Inference < 5 ms/câu

## PhoBERT — cấu hình

| Tham số | Giá trị |
|---------|---------|
| Backbone | vinai/phobert-base |
| Hidden size | 768 |
| Số tham số | ~135 triệu |
| Threshold tin cậy | **0.60** |

Kích thước file: ~515 MB · Inference 50–100 ms/câu

## **Đóng góp chính: Kiến trúc 3 tầng**

```
              Câu đầu vào
                  ↓
         ┌────────────────┐
         │ Tầng 1: BiLSTM │
         └────────┬───────┘
                  │
         conf ≥ 0.85 ?
            ╱         ╲
          Có            Không
          ↓               ↓
       Trả về      ┌────────────┐
        LSTM       │ Tầng 2:    │
                   │ PhoBERT    │
                   └─────┬──────┘
                         │
                conf ≥ 0.60 ?
                   ╱        ╲
                 Có           Không
                 ↓              ↓
              Trả về       Tầng 3: chọn
              PhoBERT      conf cao hơn
```

## Logic 3 tầng

```python
def predict_intent(text):
    # Tầng 1: LSTM nhanh
    lstm_tag, lstm_conf = predict_lstm(text)
    if lstm_conf >= 0.85:
        return lstm_tag, "LSTM"

    # Tầng 2: PhoBERT chính xác hơn
    phobert_tag, phobert_conf = predict_phobert(text)
    if phobert_conf >= 0.60:
        return phobert_tag, "PhoBERT"

    # Tầng 3: chọn confidence cao hơn
    return best_of(lstm, phobert), "low"
```

## Vì sao 3 tầng?

- **Đa số câu** trong giao tiếp là rõ ràng → LSTM xử lý là đủ và nhanh
- Câu khó, paraphrase, từ vựng hiếm → PhoBERT
- Cả hai không tự tin → đánh dấu "low" để fallback an toàn
- **Cân bằng tốt** giữa **latency** và **accuracy**

## Trích xuất thực thể (rule-based)

**Thời gian — regex:**
- "ngày 25/4", "lúc 3 giờ chiều", "ngày mai", "tuần sau"

**Tên công việc — trigger keyword:**
```
"thêm công việc họp nhóm vào 3 giờ chiều mai"
        ↓ trigger: "thêm công việc"
"họp nhóm vào 3 giờ chiều mai"
        ↓ loại pattern thời gian
"họp nhóm"  ✓
```

## Cải tiến: chia sẻ trigger

**Vấn đề phát hiện trong thực nghiệm:**

> "Tạo nhắc nhở: ngày mai bắt đầu đi làm lại"

→ LSTM phân loại `create_task` (do từ "tạo")
→ Nhưng trigger list của `create_task` không có "tạo nhắc nhở"
→ task_name **bị bỏ trống**

**Giải pháp:** nhóm intent họ hàng `{create_task, set_reminder, ...}` chia sẻ chung trigger pool, sắp xếp theo độ dài giảm dần để khớp chính xác nhất.

## Quản lý hội thoại — pending_actions

```
User:  "xóa hết công việc đi"
Bot:   "Bạn có chắc muốn xóa toàn bộ?"
       → pending_actions[user_id] = "delete_all"

User:  "có"
Bot:   → kiểm tra pending trước khi gọi NLP
       → thực thi xóa
       → "Đã xóa N công việc."
```

Tránh người dùng vô ý kích hoạt thao tác phá hủy.

# Kết quả thực nghiệm

## Demo case — đã kiểm thử thực tế

| Câu | Intent | Conf | Tầng |
|-----|--------|------|------|
| Tạo nhắc nhở: ngày mai bắt đầu đi làm lại | `create_task` | **0.999** | LSTM |
| thêm công việc họp nhóm 3 giờ chiều mai | `create_task` | ≈0.99 | LSTM |
| xem công việc chưa hoàn thành | `list_tasks` | ≈0.95 | LSTM |
| việc nào quan trọng nhất hôm nay | `priority_mgmt` | ≈0.7 | PhoBERT |

## Phân bố tỷ lệ sử dụng các tầng

| Tầng | Tỷ lệ |
|------|-------|
| Tầng 1 — LSTM (≥ 0.85) | **70 – 80 %** |
| Tầng 2 — PhoBERT (≥ 0.60) | 10 – 15 % |
| Tầng 3 — Fallback | < 10 % |

→ Đa số câu được xử lý nhanh tại tầng 1
→ Chỉ kích hoạt PhoBERT khi cần
→ Giảm chi phí tính toán đáng kể

## Demo ứng dụng Flutter

- Màn hình **Chat**: bubble chat, suggestion chips
- Màn hình **Công việc**: 2 tab Chưa xong / Đã xong
- Màn hình **Đăng nhập** (lưu SharedPreferences)
- Màn hình **Cài đặt**

*[Chèn screenshot tại đây khi thuyết trình]*

# Kết luận

## Kết quả đạt được

- ✓ Dataset 1.117 mẫu, 34 intent
- ✓ Huấn luyện thành công BiLSTM + PhoBERT
- ✓ **Kiến trúc 3 tầng** đạt cân bằng latency/accuracy
- ✓ Triển khai end-to-end iOS/Android/Web
- ✓ Khắc phục lỗi trích xuất tên cho câu lai create/reminder

## Hạn chế

- Dataset còn nhỏ (~1.000 mẫu) → một số intent ít mẫu accuracy thấp
- Entity extraction rule-based → khó scale
- Không có **context history** đa lượt
- Chỉ hỗ trợ **single-user-per-session**

## Hướng phát triển

1. Mở rộng dataset lên 5.000+ qua back-translation
2. Thay rule-based bằng **NER có học** (BiLSTM-CRF, PhoBERT-NER)
3. **Dialogue state tracking** cho tham chiếu đa lượt
4. Push notification thực sự (Firebase) cho `reminder`
5. Voice input (Speech-to-Text tiếng Việt)
6. Đa người dùng + JWT + Redis pending_actions

# Cảm ơn

## Câu hỏi & Thảo luận

**Liên hệ:**
- GitHub: …
- Email: …

***Em xin chân thành cảm ơn quý thầy cô đã lắng nghe!***
