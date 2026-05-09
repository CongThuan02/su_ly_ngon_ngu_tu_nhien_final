<div align="center">

# TRƯỜNG ĐẠI HỌC ………………………
## KHOA CÔNG NGHỆ THÔNG TIN

---

# BÁO CÁO ĐỒ ÁN CUỐI KỲ
# MÔN: XỬ LÝ NGÔN NGỮ TỰ NHIÊN

---

## ĐỀ TÀI:
# XÂY DỰNG CHATBOT QUẢN LÝ VÀ NHẮC NHỞ CÔNG VIỆC HÀNG NGÀY SỬ DỤNG MÔ HÌNH NLP TIẾNG VIỆT

---

**Sinh viên thực hiện:** Hoàng Thuận
**Mã số sinh viên:** ………………………
**Lớp:** ………………………
**Giảng viên hướng dẫn:** ………………………

---

*Năm học 2025 – 2026*

</div>

<div style="page-break-after: always;"></div>

---

## LỜI CẢM ƠN

Em xin chân thành cảm ơn quý thầy cô Khoa Công nghệ Thông tin, đặc biệt là giảng viên hướng dẫn môn học **Xử lý Ngôn ngữ Tự nhiên**, đã tận tình truyền đạt kiến thức và định hướng giúp em hoàn thành đồ án này.

Trong quá trình thực hiện, do thời gian và kiến thức còn hạn chế, báo cáo không tránh khỏi thiếu sót. Em rất mong nhận được những góp ý quý báu từ thầy cô để có thể hoàn thiện hơn trong tương lai.

Em xin chân thành cảm ơn!

<div style="page-break-after: always;"></div>

---

## MỤC LỤC

- [TÓM TẮT](#tóm-tắt)
- [DANH MỤC HÌNH ẢNH VÀ BẢNG BIỂU](#danh-mục-hình-ảnh-và-bảng-biểu)
- [CHƯƠNG 1. MỞ ĐẦU](#chương-1-mở-đầu)
  - 1.1. Lý do chọn đề tài
  - 1.2. Mục tiêu nghiên cứu
  - 1.3. Đối tượng và phạm vi nghiên cứu
  - 1.4. Phương pháp nghiên cứu
  - 1.5. Bố cục báo cáo
- [CHƯƠNG 2. CƠ SỞ LÝ THUYẾT](#chương-2-cơ-sở-lý-thuyết)
  - 2.1. Tổng quan về xử lý ngôn ngữ tự nhiên
  - 2.2. Bài toán phân loại ý định (Intent Classification)
  - 2.3. Bài toán trích xuất thực thể (Entity Extraction)
  - 2.4. Mô hình BiLSTM
  - 2.5. Mô hình PhoBERT
  - 2.6. Đặc trưng của tiếng Việt và công cụ Underthesea
- [CHƯƠNG 3. PHƯƠNG PHÁP ĐỀ XUẤT](#chương-3-phương-pháp-đề-xuất)
  - 3.1. Tổng quan kiến trúc hệ thống
  - 3.2. Xây dựng tập dữ liệu
  - 3.3. Tiền xử lý văn bản
  - 3.4. Mô hình BiLSTM tự huấn luyện
  - 3.5. Mô hình PhoBERT fine-tune
  - 3.6. Hệ thống phân loại ba tầng (đề xuất)
  - 3.7. Trích xuất thực thể
  - 3.8. Quản lý hội thoại
- [CHƯƠNG 4. CÀI ĐẶT VÀ THỰC NGHIỆM](#chương-4-cài-đặt-và-thực-nghiệm)
  - 4.1. Môi trường cài đặt
  - 4.2. Cài đặt backend
  - 4.3. Cài đặt ứng dụng di động
  - 4.4. Kết quả thực nghiệm
  - 4.5. Phân tích lỗi và hạn chế
- [CHƯƠNG 5. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN](#chương-5-kết-luận-và-hướng-phát-triển)
  - 5.1. Kết quả đạt được
  - 5.2. Hạn chế
  - 5.3. Hướng phát triển
- [TÀI LIỆU THAM KHẢO](#tài-liệu-tham-khảo)
- [PHỤ LỤC](#phụ-lục)

<div style="page-break-after: always;"></div>

---

## TÓM TẮT

Báo cáo trình bày quá trình xây dựng một chatbot tiếng Việt phục vụ quản lý và nhắc nhở công việc cá nhân hàng ngày, trong khuôn khổ đồ án cuối kỳ môn Xử lý Ngôn ngữ Tự nhiên. Hệ thống được phát triển dưới dạng ứng dụng đa nền tảng gồm backend FastAPI (Python) và ứng dụng di động Flutter, hỗ trợ ba nền tảng iOS, Android và Web.

Đề tài tập trung giải quyết hai bài toán cốt lõi của NLP: (i) phân loại ý định người dùng trên 34 nhãn liên quan đến quản lý công việc; (ii) trích xuất thực thể (tên công việc, thời gian, trạng thái) từ câu tiếng Việt tự nhiên. Đề xuất chính của báo cáo là **kiến trúc phân loại ba tầng (3-tier classification)**, kết hợp mô hình BiLSTM tự huấn luyện ở tầng đầu (xử lý nhanh các câu rõ ràng) và mô hình PhoBERT fine-tune ở tầng sau (xử lý các câu khó, paraphrase). Cơ chế chuyển tầng dựa trên ngưỡng độ tin cậy (confidence threshold) đã được tinh chỉnh thực nghiệm.

Tập dữ liệu tự xây dựng gồm **996 mẫu huấn luyện** và **121 mẫu kiểm thử** trên **34 ý định** thuộc 9 nhóm chức năng. Kết quả thực nghiệm cho thấy hệ thống ba tầng đạt được sự cân bằng tốt giữa độ trễ (latency) và độ chính xác (accuracy), với phần lớn câu hội thoại được xử lý tại tầng BiLSTM nhẹ, chỉ chuyển sang PhoBERT khi cần thiết.

**Từ khóa:** Xử lý ngôn ngữ tự nhiên tiếng Việt, Chatbot, Phân loại ý định, BiLSTM, PhoBERT, Trích xuất thực thể, FastAPI, Flutter.

<div style="page-break-after: always;"></div>

---

## DANH MỤC BẢNG BIỂU

| Số hiệu | Tên bảng | Trang |
|:-------:|:---------|:-----:|
| Bảng 3.1 | Phân bố 34 ý định theo 9 nhóm chức năng | … |
| Bảng 3.2 | Siêu tham số mô hình BiLSTM | … |
| Bảng 3.3 | Cấu hình mô hình PhoBERT | … |
| Bảng 4.1 | Kết quả phân loại ý định trên các trường hợp tiêu biểu | … |
| Bảng 4.2 | Phân bố tỷ lệ sử dụng các tầng trong hệ thống ba tầng | … |

## DANH MỤC HÌNH ẢNH

| Số hiệu | Tên hình | Trang |
|:-------:|:---------|:-----:|
| Hình 3.1 | Kiến trúc tổng thể của hệ thống | … |
| Hình 3.2 | Pipeline tiền xử lý văn bản tiếng Việt | … |
| Hình 3.3 | Kiến trúc mô hình BiLSTM | … |
| Hình 3.4 | Cơ chế ra quyết định ba tầng | … |

<div style="page-break-after: always;"></div>

---

## CHƯƠNG 1. MỞ ĐẦU

### 1.1. Lý do chọn đề tài

Quản lý công việc cá nhân là nhu cầu thiết yếu trong cuộc sống hiện đại. Các ứng dụng to-do list truyền thống thường yêu cầu người dùng thao tác qua nhiều bước thủ công: mở ứng dụng, nhấn nút thêm, gõ tên công việc, chọn ngày giờ qua các giao diện chuyên biệt. Quy trình này tạo rào cản đáng kể đối với người dùng phổ thông, đặc biệt là người lớn tuổi hoặc người chưa quen sử dụng smartphone.

Sự phát triển của các mô hình ngôn ngữ pre-trained như BERT, GPT, và đặc biệt là **PhoBERT** dành riêng cho tiếng Việt [1], đã mở ra khả năng xây dựng các giao diện tương tác bằng ngôn ngữ tự nhiên có chất lượng cao mà không cần tài nguyên huấn luyện khổng lồ. Việc kết hợp các mô hình này vào ứng dụng quản lý công việc cho phép người dùng thao tác bằng cách nói/gõ câu thường ngày như *"nhắc tôi họp 3 giờ chiều mai"*, từ đó giảm thời gian thao tác và tăng trải nghiệm sử dụng.

Đề tài này được lựa chọn nhằm mục đích vận dụng kiến thức đã học trong môn Xử lý Ngôn ngữ Tự nhiên vào một bài toán thực tiễn, đồng thời khám phá khả năng kết hợp giữa mô hình truyền thống (BiLSTM tự huấn luyện) và mô hình pre-trained hiện đại (PhoBERT) trong cùng một hệ thống.

### 1.2. Mục tiêu nghiên cứu

Đề tài đặt ra các mục tiêu cụ thể như sau:

1. Xây dựng tập dữ liệu hội thoại tiếng Việt cho domain quản lý công việc với ít nhất 1.000 mẫu, trải đều trên 34 ý định.
2. Huấn luyện và đánh giá hai mô hình phân loại ý định: BiLSTM tự huấn luyện và PhoBERT fine-tune.
3. Đề xuất và cài đặt kiến trúc kết hợp ba tầng nhằm tận dụng ưu điểm của cả hai mô hình.
4. Cài đặt module trích xuất thực thể (tên công việc, thời gian, trạng thái) bằng kỹ thuật rule-based.
5. Triển khai end-to-end: backend FastAPI và ứng dụng Flutter chạy được trên iOS, Android và Web.

### 1.3. Đối tượng và phạm vi nghiên cứu

**Đối tượng nghiên cứu:**
- Các kỹ thuật NLP tiếng Việt: tokenization, intent classification, entity extraction.
- Mô hình BiLSTM và PhoBERT.
- Kiến trúc chatbot end-to-end.

**Phạm vi nghiên cứu:**
- Ngôn ngữ: tiếng Việt.
- Domain: quản lý công việc cá nhân (CRUD công việc, nhắc nhở, tìm kiếm, thống kê, biểu lộ cảm xúc).
- Số lượng ý định: 34, được chia thành 9 nhóm.
- Người dùng: đơn người dùng (single-user-per-session), không hỗ trợ đa người dùng đồng thời.

### 1.4. Phương pháp nghiên cứu

Đề tài sử dụng phương pháp **nghiên cứu thực nghiệm**, cụ thể:
1. **Khảo sát tài liệu**: nghiên cứu các công trình về NLP tiếng Việt, kiến trúc BERT, các bài toán intent classification.
2. **Xây dựng dataset**: tổng hợp các mẫu câu giao tiếp tiếng Việt thường gặp trong domain quản lý công việc.
3. **Cài đặt mô hình**: sử dụng PyTorch để huấn luyện BiLSTM và fine-tune PhoBERT.
4. **Thực nghiệm và đánh giá**: chạy thử trên tập test, đo lường accuracy, latency, và phân tích lỗi.
5. **Triển khai hệ thống**: xây dựng backend FastAPI và frontend Flutter, kiểm thử thực tế trên thiết bị.

### 1.5. Bố cục báo cáo

Báo cáo được tổ chức thành 5 chương:
- **Chương 1** giới thiệu lý do chọn đề tài, mục tiêu và phạm vi.
- **Chương 2** trình bày cơ sở lý thuyết về NLP, BiLSTM và PhoBERT.
- **Chương 3** mô tả phương pháp đề xuất, bao gồm kiến trúc ba tầng.
- **Chương 4** trình bày quá trình cài đặt và kết quả thực nghiệm.
- **Chương 5** kết luận và đề xuất hướng phát triển.

<div style="page-break-after: always;"></div>

---

## CHƯƠNG 2. CƠ SỞ LÝ THUYẾT

### 2.1. Tổng quan về xử lý ngôn ngữ tự nhiên

Xử lý ngôn ngữ tự nhiên (Natural Language Processing — NLP) là một nhánh của trí tuệ nhân tạo, nghiên cứu cách máy tính hiểu, sinh và xử lý ngôn ngữ con người. Các bài toán điển hình của NLP bao gồm phân loại văn bản, trích xuất thông tin, dịch máy, hỏi đáp tự động, sinh văn bản, v.v.

Đối với chatbot, hai bài toán nền tảng là:
1. **Phân loại ý định (Intent Classification)** — xác định người dùng muốn làm gì.
2. **Trích xuất thực thể (Entity Extraction)** — xác định các tham số cụ thể trong câu.

### 2.2. Bài toán phân loại ý định

Cho câu đầu vào dạng chuỗi token `x = (x₁, x₂, …, xₙ)` và tập nhãn ý định `Y = {y₁, y₂, …, y_K}`, bài toán phân loại ý định là tìm hàm `f: X → Y` sao cho với mỗi câu `x`, hàm `f(x)` trả về ý định đúng. Đây là bài toán phân loại văn bản (text classification) đa lớp.

Các phương pháp tiếp cận chính:
- **Rule-based**: dựa trên từ khóa và pattern. Ưu điểm: dễ hiểu, không cần dữ liệu. Nhược điểm: khó scale, không xử lý được paraphrase.
- **Machine Learning truyền thống**: Naive Bayes, SVM, Random Forest trên TF-IDF. Phù hợp dataset nhỏ.
- **Deep Learning**: CNN, RNN/LSTM, Transformer. Cần dữ liệu lớn hơn nhưng đạt accuracy cao.
- **Pre-trained Language Models**: BERT, RoBERTa, PhoBERT. Tận dụng tri thức đã học từ dữ liệu lớn, fine-tune trên dataset domain.

### 2.3. Bài toán trích xuất thực thể

Trích xuất thực thể (Named Entity Recognition — NER) gán nhãn cho từng token trong câu, ví dụ B-TIME, I-TIME, O. Trong đồ án này, do dataset nhỏ nên sử dụng phương pháp **rule-based** kết hợp **regex**, tập trung vào ba loại thực thể:
- `task_name`: tên công việc.
- `time`: thời gian (tuyệt đối hoặc tương đối).
- `status`: trạng thái lọc (pending/completed) khi liệt kê công việc.

### 2.4. Mô hình BiLSTM

Long Short-Term Memory (LSTM) [4] là biến thể của Recurrent Neural Network có khả năng học các phụ thuộc dài thông qua cơ chế cổng (gate). Phiên bản hai chiều **BiLSTM** đọc câu theo cả hai hướng (trái → phải và phải → trái), kết hợp hai trạng thái ẩn để có biểu diễn ngữ cảnh đầy đủ hơn.

Kiến trúc cơ bản cho phân loại văn bản:
```
Token ids → Embedding → BiLSTM → Pool/Last hidden → Dense → Softmax
```

BiLSTM phù hợp với dataset nhỏ-trung bình do số tham số ít hơn so với Transformer, tốc độ inference nhanh, không cần GPU.

### 2.5. Mô hình PhoBERT

**PhoBERT** [1] là mô hình BERT pre-trained được phát triển bởi VinAI dành riêng cho tiếng Việt. Mô hình được huấn luyện trên 20GB văn bản tiếng Việt, sử dụng kiến trúc RoBERTa-base với 12 lớp Transformer, hidden size 768, 12 attention heads, tổng cộng khoảng 135 triệu tham số.

Đặc điểm quan trọng của PhoBERT là sử dụng **VnCoreNLP** [3] để tách từ tiếng Việt trước khi tokenize bằng SentencePiece BPE. Điều này khác với BERT đa ngôn ngữ (mBERT) vốn không hiểu được cấu trúc từ ghép của tiếng Việt.

Để áp dụng PhoBERT vào phân loại ý định, ta thêm một lớp Linear (768 → K) trên đầu ra `[CLS]` và fine-tune toàn bộ mô hình hoặc chỉ classifier head.

### 2.6. Đặc trưng của tiếng Việt và công cụ Underthesea

Tiếng Việt có những đặc điểm gây khó khăn cho NLP:
- **Từ ghép**: "công việc", "hoàn thành", "đã xong" là một đơn vị ngữ nghĩa nhưng được viết bằng nhiều âm tiết phân tách.
- **Dấu thanh**: dấu sắc, huyền, hỏi, ngã, nặng tạo nên các từ khác nghĩa.
- **Không có biến hình**: không chia động từ, không số nhiều — phụ thuộc vào ngữ cảnh.

**Underthesea** [2] là thư viện NLP tiếng Việt mã nguồn mở, hỗ trợ tách từ, gắn nhãn POS, NER, phân tích cảm xúc. Trong đồ án sử dụng `underthesea.word_tokenize` để tách từ chính xác trước khi map sang token id.

<div style="page-break-after: always;"></div>

---

## CHƯƠNG 3. PHƯƠNG PHÁP ĐỀ XUẤT

### 3.1. Tổng quan kiến trúc hệ thống

Hệ thống được thiết kế theo kiến trúc client-server đa nền tảng:

```
┌────────────────────────────────────────────────────────┐
│  Frontend — Flutter App (iOS, Android, Web)            │
│   ├─ Màn hình Chat                                     │
│   ├─ Màn hình Công việc (CRUD)                         │
│   ├─ Màn hình Đăng nhập                                │
│   └─ Màn hình Cài đặt                                  │
└─────────────────────┬──────────────────────────────────┘
                      │ HTTP / JSON
┌─────────────────────┴──────────────────────────────────┐
│  Backend — FastAPI (Python 3.12)                       │
│   ├─ POST /chat   →  Pipeline NLP ba tầng             │
│   ├─ CRUD /tasks  →  SQLite                            │
│   └─ Pending actions middleware                        │
│                                                         │
│   NLP Pipeline:                                         │
│     ┌────────┐   ┌──────────┐   ┌──────────┐          │
│     │  LSTM  │ → │ PhoBERT  │ → │ Fallback │          │
│     │ ≥ 0.85 │   │  ≥ 0.60  │   │  argmax  │          │
│     └────────┘   └──────────┘   └──────────┘          │
│                                                         │
│   Database: SQLite tasks.db                             │
└────────────────────────────────────────────────────────┘
```

*Hình 3.1. Kiến trúc tổng thể của hệ thống*

### 3.2. Xây dựng tập dữ liệu

#### 3.2.1. Quy mô và phân bố

| Tập | Số mẫu |
|-----|--------|
| Training | 996 |
| Test | 121 |
| **Tổng** | **1.117** |

#### 3.2.2. Phân loại 34 ý định theo 9 nhóm

*Bảng 3.1. Phân bố 34 ý định theo nhóm chức năng*

| STT | Nhóm | Các ý định |
|-----|------|-----------|
| 1 | Chào hỏi | greeting, goodbye, thank_you, bot_identity |
| 2 | CRUD công việc | create_task, delete_task, update_task, list_tasks, status_update |
| 3 | Tìm kiếm | search_task, task_by_category, sort_tasks, task_detail |
| 4 | Quản lý nâng cao | deadline_management, priority_management, assign_task, collaboration |
| 5 | Thời gian | task_today, task_overdue, task_upcoming, reschedule, set_duration |
| 6 | Nhắc nhở | reminder |
| 7 | Thao tác hàng loạt | complete_all_tasks, delete_all_tasks, confirm_complete, confirm_delete |
| 8 | Thống kê | statistics |
| 9 | Cảm xúc & khác | feeling_overwhelmed, feeling_productive, motivation, general_help, add_note, out_of_scope |

#### 3.2.3. Cấu trúc mỗi mẫu dữ liệu

```json
{
  "text": "thêm công việc họp nhóm vào 3 giờ chiều mai",
  "intent": "create_task"
}
```

### 3.3. Tiền xử lý văn bản

Pipeline tiền xử lý được cài đặt tại `backend/utils/text_preprocessor.py`:

```
Câu thô
   │
   ▼
[Lowercase]                       "Thêm Công Việc Họp"
   │                                 → "thêm công việc họp"
   ▼
[underthesea.word_tokenize]       ["thêm", "công_việc", "họp"]
   │
   ▼
[Loại ký tự đặc biệt]
   │
   ▼
[text_to_sequence]                [12, 45, 89, 0, 0, ...]
   │                              (pad/truncate đến max_len = 30)
   ▼
Tensor đầu vào mô hình
```

*Hình 3.2. Pipeline tiền xử lý văn bản*

### 3.4. Mô hình BiLSTM tự huấn luyện

#### 3.4.1. Kiến trúc

```
Input: token ids (batch_size, seq_len = 30)
   │
   ▼
Embedding (vocab=782, dim=256)         (batch, 30, 256)
   │
   ▼
BiLSTM (hidden=256, num_layers=2)      (batch, 30, 512)
   │
   ▼
Take last hidden state                 (batch, 512)
   │
   ▼
Dropout (p=0.3)
   │
   ▼
Linear (512 → 34)                      (batch, 34)
   │
   ▼
Softmax
   │
   ▼
Phân phối xác suất trên 34 ý định
```

*Hình 3.3. Kiến trúc mô hình BiLSTM*

#### 3.4.2. Siêu tham số

*Bảng 3.2. Siêu tham số mô hình BiLSTM*

| Siêu tham số | Giá trị |
|--------------|---------|
| Vocabulary size | 782 |
| Embedding dim | 256 |
| Hidden dim | 256 |
| Số lớp LSTM | 2 |
| Dropout | 0.3 |
| Max sequence length | 30 |
| Loss function | Cross-Entropy |
| Optimizer | Adam |
| Threshold tin cậy (tier-1) | 0.85 |

**Đặc điểm**: kích thước nhỏ (~11 MB), inference dưới 5 ms/câu trên CPU, không yêu cầu GPU khi triển khai.

### 3.5. Mô hình PhoBERT fine-tune

#### 3.5.1. Kiến trúc

Sử dụng `vinai/phobert-base` từ HuggingFace Hub làm backbone, thêm classifier head:

```
Input: PhoBERT tokenizer (SentencePiece BPE)
   │
   ▼
PhoBERT-base (12 layers, hidden=768)
   │
   ▼
Lấy đầu ra [CLS]                       (batch, 768)
   │
   ▼
Linear (768 → 34)                      (batch, 34)
   │
   ▼
Softmax
```

#### 3.5.2. Cấu hình fine-tune

*Bảng 3.3. Cấu hình mô hình PhoBERT*

| Tham số | Giá trị |
|---------|---------|
| Backbone | vinai/phobert-base |
| Hidden size | 768 |
| Số tham số | ≈ 135 triệu |
| Threshold tin cậy (tier-2) | 0.60 |
| Kích thước file | ≈ 515 MB |
| Inference time | 50–100 ms/câu (CPU) |

### 3.6. Hệ thống phân loại ba tầng (đề xuất)

Đây là **đóng góp chính** của đồ án. Thay vì sử dụng đơn lẻ một trong hai mô hình, hệ thống kết hợp cả hai theo cơ chế **cascade**:

```
                    Câu đầu vào
                         │
                         ▼
              ┌──────────────────────┐
              │  Tầng 1: BiLSTM      │
              └──────────┬───────────┘
                         │
                lstm_conf ≥ 0.85?
                    /         \
                  Có            Không
                  │               │
                  ▼               ▼
            ┌─────────┐   ┌──────────────┐
            │ Trả về  │   │ Tầng 2:       │
            │  LSTM   │   │ PhoBERT       │
            └─────────┘   └──────┬───────┘
                                 │
                       phobert_conf ≥ 0.60?
                            /        \
                          Có          Không
                          │             │
                          ▼             ▼
                    ┌─────────┐  ┌─────────────┐
                    │ Trả về  │  │ Tầng 3:     │
                    │ PhoBERT │  │ Chọn conf   │
                    └─────────┘  │ cao hơn     │
                                 └─────────────┘
```

*Hình 3.4. Cơ chế ra quyết định ba tầng*

**Mã giả của thuật toán** (`models/chatbot.py::predict_intent`):

```python
def predict_intent(text: str) -> tuple[str, float, str]:
    # Tầng 1: BiLSTM nhanh
    lstm_tag, lstm_conf = predict_lstm(text)
    if lstm_conf >= 0.85:
        return lstm_tag, lstm_conf, "LSTM"

    # Tầng 2: PhoBERT chính xác hơn
    phobert_tag, phobert_conf = predict_phobert(text)
    if phobert_conf >= 0.60:
        return phobert_tag, phobert_conf, "PhoBERT"

    # Tầng 3: Fallback — chọn model có confidence cao hơn
    if lstm_conf >= phobert_conf:
        return lstm_tag, lstm_conf, "LSTM(low)"
    return phobert_tag, phobert_conf, "PhoBERT(low)"
```

**Cơ sở lý luận của thiết kế:**
- Phần lớn câu trong giao tiếp hàng ngày là rõ ràng, trực tiếp (*"chào bạn"*, *"thêm việc"*) — BiLSTM xử lý dễ và nhanh.
- Chỉ những câu khó (paraphrase, từ vựng hiếm, câu dài) mới cần đến PhoBERT.
- Khi cả hai mô hình đều không tự tin, hệ thống đánh dấu kết quả là "low confidence" để tầng response có thể fallback an toàn (yêu cầu người dùng nói rõ hơn).

**Lợi ích**:
- Latency trung bình thấp hơn so với chỉ dùng PhoBERT.
- Accuracy cao hơn so với chỉ dùng BiLSTM.
- Đạt cân bằng tốt giữa tốc độ và chất lượng — phù hợp triển khai trên thiết bị có tài nguyên hạn chế.

### 3.7. Trích xuất thực thể

Cài đặt tại `backend/utils/entity_extractor.py` theo phương pháp rule-based.

#### 3.7.1. Trích xuất thời gian — regex

```python
time_patterns = [
    r"((?:ngày\s*)?\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)",
    r"(?:lúc|vào|vào lúc)\s+(\d{1,2}\s*(?:giờ|h|:)...)",
    r"(ngày mai|hôm nay|hôm qua|chiều nay|sáng mai|tối nay|tuần sau|tháng sau)"
]
```

#### 3.7.2. Trích xuất tên công việc — trigger keyword

Mỗi ý định có một danh sách trigger. Sau khi tìm thấy trigger, phần còn lại của câu được làm sạch (loại từ nối, loại pattern thời gian) để lấy ra tên công việc.

Ví dụ:
- Câu: *"thêm công việc họp nhóm vào 3 giờ chiều mai"*
- Trigger khớp: `"thêm công việc"`
- Phần sau trigger: *"họp nhóm vào 3 giờ chiều mai"*
- Sau khi loại bỏ phần thời gian *"vào 3 giờ chiều mai"* → `task_name = "họp nhóm"`

#### 3.7.3. Cải tiến chia sẻ trigger giữa các ý định họ hàng

Trong quá trình thực nghiệm, chúng tôi phát hiện một lớp lỗi phổ biến: câu có dạng *"Tạo nhắc nhở: ngày mai bắt đầu đi làm lại"* bị BiLSTM phân loại là `create_task` (do từ khóa "tạo"), nhưng danh sách trigger của `create_task` không chứa cụm "tạo nhắc nhở" → tên công việc bị bỏ trống.

Giải pháp: cho nhóm ý định *họ hàng* `{create_task, set_reminder, them_cong_viec, nhac_nho}` chia sẻ chung một bể trigger. Khi cần trích xuất tên công việc, hệ thống thử lần lượt tất cả trigger trong nhóm theo thứ tự dài → ngắn để khớp chính xác nhất.

### 3.8. Quản lý hội thoại

Một số ý định có tính phá hủy (xóa toàn bộ, hoàn thành toàn bộ) yêu cầu xác nhận. Hệ thống sử dụng cơ chế `pending_actions`:

```
Lượt 1:
  User: "xóa hết công việc đi"
  Bot:  "Bạn có chắc muốn xóa toàn bộ công việc?"
  → pending_actions[user_id] = {"type": "delete_all"}

Lượt 2:
  User: "có"
  Bot:  → kiểm tra pending_actions trước khi gọi mô hình NLP
        → thực thi xóa toàn bộ
        → trả về "Đã xóa N công việc."
        → xóa pending_actions[user_id]
```

Cơ chế này tránh được trường hợp người dùng vô ý gửi câu *"xóa hết"* và hệ thống thực thi ngay lập tức.

<div style="page-break-after: always;"></div>

---

## CHƯƠNG 4. CÀI ĐẶT VÀ THỰC NGHIỆM

### 4.1. Môi trường cài đặt

| Thành phần | Phiên bản |
|------------|-----------|
| Hệ điều hành phát triển | macOS Darwin 25.3 |
| Python | 3.12.13 |
| PyTorch | 2.x |
| Transformers (HuggingFace) | 4.x |
| FastAPI | 0.128 |
| Underthesea | 9.x |
| Flutter | 3.38.3 (qua FVM) |
| Database | SQLite |

### 4.2. Cài đặt backend

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Đặt 5 file model vào backend/data/:
#   chatbot_model.pth         (BiLSTM, ~11 MB)
#   phobert_model.pth         (PhoBERT, ~515 MB)
#   model_metadata.json       (vocab, tags, hyperparams)
#   responses.json            (response templates)
#   phobert_tokenizer/        (tokenizer files)

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend cung cấp 6 endpoint chính:

| Method | Path | Mô tả |
|--------|------|-------|
| POST | `/chat` | Gửi câu hỏi, nhận intent + entities + response |
| POST | `/tasks` | Tạo công việc mới |
| GET | `/tasks/{user_id}` | Lấy danh sách công việc |
| PUT | `/tasks/{task_id}` | Cập nhật công việc |
| DELETE | `/tasks/{task_id}` | Xóa công việc |
| PATCH | `/tasks/{task_id}/complete` | Đánh dấu hoàn thành |

### 4.3. Cài đặt ứng dụng di động

```bash
cd flutter_app
fvm use 3.38.3
fvm flutter pub get
fvm flutter run -d chrome      # Web
fvm flutter run -d <device_id> # iOS/Android
```

Khi triển khai trên thiết bị thật, cần cập nhật `baseUrl` tại `lib/services/api_service.dart` thành địa chỉ IP máy chủ backend trong cùng mạng LAN.

### 4.4. Kết quả thực nghiệm

#### 4.4.1. Một số trường hợp tiêu biểu

*Bảng 4.1. Kết quả phân loại trên các trường hợp tiêu biểu*

| Câu đầu vào | Intent dự đoán | Confidence | Tầng | Entities trích xuất |
|-------------|----------------|-----------|------|---------------------|
| "Tạo nhắc nhở: ngày mai bắt đầu đi làm lại" | `create_task` | 0.999 | LSTM | task_name="bắt đầu đi làm lại", time="ngày mai" |
| "thêm công việc họp nhóm vào 3 giờ chiều mai" | `create_task` | ≈ 0.99 | LSTM | task_name="họp nhóm", time="3 giờ chiều" |
| "xem công việc chưa hoàn thành" | `list_tasks` | ≈ 0.95 | LSTM | status="pending" |
| "chào bạn" | `greeting` | ≈ 0.99 | LSTM | (không có) |
| "việc nào quan trọng nhất hôm nay" | `priority_management` | ≈ 0.7 | PhoBERT | (không có) |

#### 4.4.2. Phân bố sử dụng các tầng

Theo quan sát thực nghiệm trên tập kiểm thử và các phiên chat thực tế:

*Bảng 4.2. Phân bố tỷ lệ sử dụng các tầng*

| Tầng | Tỷ lệ ước lượng |
|------|----------------|
| Tầng 1 (LSTM ≥ 0.85) | 70 – 80 % |
| Tầng 2 (PhoBERT ≥ 0.60) | 10 – 15 % |
| Tầng 3 (Fallback) | < 10 % |

Phần lớn câu được xử lý tại tầng 1 (BiLSTM), giúp giảm đáng kể chi phí tính toán so với việc dùng PhoBERT cho mọi câu đầu vào.

### 4.5. Phân tích lỗi và hạn chế

Trong quá trình thực nghiệm, một số dạng lỗi đã được phát hiện:

1. **Nhầm lẫn ngữ nghĩa**: câu *"công việc đã hoàn thành"* (mục đích xem danh sách) bị phân loại là `status_update` (đánh dấu hoàn thành). Nguyên nhân: dataset có nhiều mẫu `status_update` chứa cụm "đã hoàn thành".
2. **Tên công việc nhiễu**: câu *"thêm việc sửa lỗi cho ngày mai"* — tên công việc *"sửa lỗi"* trùng từ khóa của intent khác, gây nhầm sang `update_task`.
3. **Thực thể bị bỏ sót**: như đã phân tích ở mục 3.7.3, các câu có cấu trúc lai giữa "tạo" và "nhắc nhở" gây mất `task_name`. Đã được khắc phục bằng cải tiến chia sẻ trigger.

Các trường hợp 1 và 2 cần được khắc phục bằng cách bổ sung thêm dữ liệu huấn luyện và tái huấn luyện mô hình.

<div style="page-break-after: always;"></div>

---

## CHƯƠNG 5. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 5.1. Kết quả đạt được

Đồ án đã hoàn thành các mục tiêu đề ra:

1. **Xây dựng tập dữ liệu** gồm 1.117 mẫu trên 34 ý định, đủ phong phú để huấn luyện và đánh giá.
2. **Cài đặt và huấn luyện** hai mô hình BiLSTM và PhoBERT trên Google Colab, đạt độ tin cậy cao trên các câu rõ ràng.
3. **Đề xuất kiến trúc ba tầng** kết hợp ưu điểm của hai mô hình, đạt cân bằng tốt giữa độ trễ và độ chính xác.
4. **Triển khai end-to-end**: backend FastAPI và ứng dụng Flutter chạy được trên iOS, Android và Web.
5. **Khắc phục một số lỗi thực tế** trong quá trình thử nghiệm, ví dụ vấn đề trích xuất tên công việc cho câu lai create_task / reminder.

### 5.2. Hạn chế

Mặc dù hệ thống đã hoạt động tốt trên các câu phổ biến, vẫn còn một số hạn chế:
- **Tập dữ liệu nhỏ** (~1.000 mẫu) khiến một số intent ít mẫu (như `feeling_*`, `out_of_scope`) có accuracy thấp.
- **Trích xuất thực thể rule-based** không scale tốt với câu đa dạng — cần thay thế bằng mô hình NER có học.
- **Không có context history** — chatbot xử lý từng câu độc lập, không hiểu được tham chiếu như *"sửa nó thành 4 giờ"* (it = task vừa tạo).
- **Cơ chế single-user** — `pending_actions` lưu in-memory, mất khi restart server, không hỗ trợ đa người dùng đồng thời.

### 5.3. Hướng phát triển

Đề tài có thể được mở rộng theo các hướng:

1. **Mở rộng dataset** lên 5.000+ mẫu thông qua kỹ thuật augmentation (back-translation, paraphrase generation), nhằm cân bằng phân bố giữa các intent.
2. **Áp dụng NER có học** thay cho rule-based: huấn luyện BiLSTM-CRF hoặc fine-tune PhoBERT-NER trên dataset đã được gắn nhãn token-level.
3. **Dialogue State Tracking**: lưu lại context của 3-5 lượt hội thoại gần nhất để hiểu tham chiếu và slot-filling đa lượt.
4. **Push notification** thông qua Firebase Cloud Messaging cho intent `reminder` — biến chatbot thành trợ lý nhắc việc thực sự.
5. **Voice input**: tích hợp Speech-to-Text tiếng Việt để mang lại trải nghiệm hands-free.
6. **Đa người dùng** với JWT authentication, lưu `pending_actions` trong Redis hoặc database thay vì in-memory.
7. **Tinh chỉnh ngưỡng confidence** thông qua grid search trên tập validation, thay vì chọn thủ công như hiện tại.

<div style="page-break-after: always;"></div>

---

## TÀI LIỆU THAM KHẢO

[1] Nguyen, D. Q., & Tuan Nguyen, A. (2020). *PhoBERT: Pre-trained language models for Vietnamese*. Findings of the Association for Computational Linguistics: EMNLP 2020, pp. 1037–1042.

[2] Vu, X.-S., Nguyen, V.-D., Le-Hong, P., et al. *Underthesea: A Vietnamese Natural Language Processing Toolkit*. https://github.com/undertheseanlp/underthesea

[3] Vu, T., Nguyen, D. Q., Nguyen, D. Q., Dras, M., & Johnson, M. (2018). *VnCoreNLP: A Vietnamese Natural Language Processing Toolkit*. NAACL-HLT 2018: Demonstrations, pp. 56–60.

[4] Hochreiter, S., & Schmidhuber, J. (1997). *Long Short-Term Memory*. Neural Computation, 9(8), pp. 1735–1780.

[5] Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. NAACL-HLT 2019, pp. 4171–4186.

[6] Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). *Attention Is All You Need*. NeurIPS 2017, pp. 5998–6008.

[7] Paszke, A., Gross, S., Massa, F., et al. (2019). *PyTorch: An Imperative Style, High-Performance Deep Learning Library*. NeurIPS 2019, pp. 8024–8035.

[8] Wolf, T., Debut, L., Sanh, V., et al. (2020). *Transformers: State-of-the-Art Natural Language Processing*. EMNLP 2020: System Demonstrations, pp. 38–45.

[9] FastAPI Documentation. https://fastapi.tiangolo.com/ (truy cập 2026).

[10] Flutter Documentation. https://flutter.dev/ (truy cập 2026).

<div style="page-break-after: always;"></div>

---

## PHỤ LỤC

### Phụ lục A. Cấu trúc thư mục source code

```
su_ly_ngon_ngu_tu_nhien_final/
├── BAO_CAO.md                         # Báo cáo này
├── CLAUDE.md                          # Tài liệu kỹ thuật cho dev
├── backend/                           # Python FastAPI server
│   ├── main.py                        # API endpoints, chat logic
│   ├── database.py                    # SQLite CRUD
│   ├── requirements.txt
│   ├── models/
│   │   ├── chatbot.py                 # Logic 3 tầng predict
│   │   ├── lstm_model.py              # BiLSTM architecture
│   │   └── phobert_model.py           # PhoBERT classifier
│   ├── utils/
│   │   ├── text_preprocessor.py       # tokenize, text_to_sequence
│   │   └── entity_extractor.py        # extract_entities
│   └── data/                          # Model files (không commit)
│       ├── chatbot_model.pth
│       ├── phobert_model.pth
│       ├── phobert_tokenizer/
│       ├── model_metadata.json
│       └── responses.json
├── flutter_app/                       # Flutter mobile app
│   ├── pubspec.yaml
│   └── lib/
│       ├── main.dart
│       ├── models/
│       ├── services/api_service.dart
│       ├── providers/
│       └── screens/
└── notebooks/
    ├── train_chatbot.ipynb            # Training script (Colab)
    └── task_management_chatbot_dataset.json
```

### Phụ lục B. Định dạng response của endpoint `/chat`

```json
{
  "intent": "create_task",
  "confidence": 0.999,
  "response": "Đã tạo công việc 'họp nhóm'.",
  "entities": {
    "task_name": "họp nhóm",
    "time": "ngày mai"
  },
  "source": "LSTM",
  "tasks": [
    {
      "id": "abc123",
      "title": "họp nhóm",
      "description": "",
      "due_time": "ngày mai",
      "user_id": "test",
      "is_completed": false,
      "created_at": "2026-04-27T03:34:12+00:00"
    }
  ]
}
```

### Phụ lục C. Một số mẫu dữ liệu huấn luyện

```json
[
  {"text": "thêm công việc họp nhóm 3 giờ chiều mai", "intent": "create_task"},
  {"text": "xóa hết tất cả công việc của tôi", "intent": "delete_all_tasks"},
  {"text": "công việc nào hôm nay phải làm", "intent": "task_today"},
  {"text": "tôi đang cảm thấy quá nhiều việc", "intent": "feeling_overwhelmed"},
  {"text": "nhắc tôi uống thuốc lúc 8 giờ tối", "intent": "reminder"}
]
```

---

<div align="center">

***— HẾT BÁO CÁO —***

</div>
