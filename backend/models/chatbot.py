import json
import os
import random

from utils.text_preprocessor import text_to_sequence
from utils.entity_extractor import extract_entities

try:
    import torch
except ImportError:
    torch = None

try:
    from models.lstm_model import ChatbotLSTM
except ImportError:
    ChatbotLSTM = None

try:
    from transformers import AutoTokenizer, AutoModel
    from models.phobert_model import PhoBERTClassifier
except ImportError:
    AutoTokenizer = None
    AutoModel = None
    PhoBERTClassifier = None


# Response templates — dùng {task_name} làm placeholder
RESPONSE_TEMPLATES = {
    "greeting": ["Xin chào! Tôi có thể giúp gì cho bạn?", "Chào bạn! Bạn cần hỗ trợ gì về công việc?"],
    "goodbye": ["Tạm biệt! Chúc bạn làm việc hiệu quả!", "Bye bye! Hẹn gặp lại!"],
    "thank_you": ["Không có gì! Tôi luôn sẵn sàng giúp bạn!"],
    "bot_identity": ["Tôi là chatbot quản lý công việc. Tôi giúp bạn thêm, sửa, xóa task, nhắc nhở và theo dõi tiến độ!"],
    "create_task": ["Đã tạo công việc '{task_name}'.", "Bạn muốn thêm công việc gì?"],
    "delete_task": ["Bạn có chắc muốn xóa '{task_name}' không?", "Bạn muốn xóa công việc nào?"],
    "update_task": ["Bạn muốn sửa gì cho '{task_name}'?", "Bạn muốn cập nhật công việc nào?"],
    "status_update": ["Đã đánh dấu '{task_name}' hoàn thành.", "Công việc nào đã hoàn thành?"],
    "list_tasks": ["Đây là danh sách công việc của bạn:"],
    "search_task": ["Để tôi tìm cho bạn."],
    "assign_task": ["Đã gán '{task_name}'.", "Bạn muốn gán task cho ai?"],
    "deadline_management": ["Bạn muốn đặt deadline cho task nào?"],
    "priority_management": ["Bạn muốn thay đổi ưu tiên task nào?"],
    "statistics": ["Đây là thống kê công việc:"],
    "reminder": ["Đã đặt nhắc nhở cho '{task_name}'.", "Bạn muốn nhắc nhở về việc gì?"],
    "collaboration": ["Bạn muốn chia sẻ với ai?"],
    "general_help": ["Tôi có thể giúp: thêm/sửa/xóa task, nhắc nhở, thống kê. Bạn cần gì?"],
    "complete_all_tasks": ["Bạn có chắc muốn đánh dấu hoàn thành TẤT CẢ? (Có/Không)"],
    "delete_all_tasks": ["⚠️ Bạn có chắc muốn XÓA TẤT CẢ? (Có/Không)"],
    "confirm_complete": ["Đã đánh dấu hoàn thành!"],
    "confirm_delete": ["Đã xóa!"],
    "task_today": ["Đây là công việc hôm nay:"],
    "task_overdue": ["Các công việc đã quá hạn:"],
    "task_upcoming": ["Công việc sắp tới:"],
    "task_by_category": ["Để tôi lọc cho bạn."],
    "sort_tasks": ["Để tôi sắp xếp lại."],
    "add_note": ["Đã thêm ghi chú cho '{task_name}'.", "Bạn muốn ghi chú gì?"],
    "task_detail": ["Chi tiết '{task_name}':", "Bạn muốn xem chi tiết task nào?"],
    "reschedule": ["Đã dời '{task_name}'.", "Bạn muốn dời task nào?"],
    "set_duration": ["Đã ghi nhận thời gian."],
    "feeling_overwhelmed": ["Đừng lo! Hãy để tôi giúp bạn sắp xếp lại ưu tiên nhé."],
    "feeling_productive": ["Tuyệt vời! Bạn đang làm rất tốt!"],
    "motivation": ["Mỗi bước nhỏ đều đưa bạn đến gần mục tiêu hơn! Cố lên!"],
    "out_of_scope": ["Xin lỗi, tôi chỉ hỗ trợ về quản lý công việc."],
}


class Chatbot:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") if torch else "cpu"

        # Load metadata
        metadata_path = os.path.join(data_dir, "model_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

        self.word2idx = self.metadata.get("word2idx", {})
        self.tags = self.metadata.get("tags", [])
        self.max_len = self.metadata.get("max_len", 30)
        self.lstm_threshold = self.metadata.get("lstm_threshold", 0.85)
        self.phobert_threshold = self.metadata.get("phobert_threshold", 0.60)

        # Load responses
        responses_path = os.path.join(data_dir, "responses.json")
        if os.path.exists(responses_path):
            with open(responses_path, "r", encoding="utf-8") as f:
                self.responses_dict = json.load(f)
        else:
            self.responses_dict = {}

        # === Load LSTM model ===
        self.lstm_model = None
        lstm_path = os.path.join(data_dir, "chatbot_model.pth")
        if torch and ChatbotLSTM and os.path.exists(lstm_path) and self.metadata:
            self.lstm_model = ChatbotLSTM(
                vocab_size=self.metadata.get("vocab_size", 1),
                embedding_dim=self.metadata.get("embedding_dim", 256),
                hidden_dim=self.metadata.get("hidden_dim", 256),
                output_dim=len(self.tags),
                num_layers=self.metadata.get("num_layers", 2),
                dropout=self.metadata.get("dropout", 0.3),
            ).to(self.device)
            self.lstm_model.load_state_dict(
                torch.load(lstm_path, map_location=self.device, weights_only=True)
            )
            self.lstm_model.eval()
            print("  LSTM model loaded")

        # === Load PhoBERT model ===
        self.phobert_model = None
        self.phobert_tokenizer = None
        phobert_path = os.path.join(data_dir, "phobert_model.pth")
        tokenizer_path = os.path.join(data_dir, "phobert_tokenizer")
        phobert_name = self.metadata.get("phobert_name", "vinai/phobert-base")

        if (torch and AutoTokenizer and PhoBERTClassifier
                and os.path.exists(phobert_path)):
            # Load tokenizer (local hoặc từ hub)
            if os.path.exists(tokenizer_path):
                self.phobert_tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
            else:
                self.phobert_tokenizer = AutoTokenizer.from_pretrained(phobert_name)

            phobert_base = AutoModel.from_pretrained(phobert_name)
            self.phobert_model = PhoBERTClassifier(
                phobert_base, len(self.tags)
            ).to(self.device)
            self.phobert_model.load_state_dict(
                torch.load(phobert_path, map_location=self.device, weights_only=True)
            )
            self.phobert_model.eval()
            print("  PhoBERT model loaded")

    def predict_lstm(self, text: str) -> tuple[str, float]:
        """Tầng 1: LSTM."""
        if self.lstm_model is None or not torch:
            return "unknown", 0.0
        sequence = text_to_sequence(text, self.word2idx, self.max_len)
        input_tensor = torch.LongTensor([sequence]).to(self.device)
        with torch.no_grad():
            output = self.lstm_model(input_tensor)
            probs = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probs, 1)
        return self.tags[predicted.item()], confidence.item()

    def predict_phobert(self, text: str) -> tuple[str, float]:
        """Tầng 2: PhoBERT."""
        if self.phobert_model is None or self.phobert_tokenizer is None or not torch:
            return "unknown", 0.0
        encoding = self.phobert_tokenizer(
            text, max_length=64, padding="max_length",
            truncation=True, return_tensors="pt"
        )
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)
        with torch.no_grad():
            output = self.phobert_model(input_ids, attention_mask)
            probs = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probs, 1)
        return self.tags[predicted.item()], confidence.item()

    def predict_intent(self, text: str) -> tuple[str, float, str]:
        """Hệ thống 3 tầng: LSTM → PhoBERT → fallback."""
        # Tầng 1: LSTM
        lstm_tag, lstm_conf = self.predict_lstm(text)
        if lstm_conf >= self.lstm_threshold:
            return lstm_tag, lstm_conf, "LSTM"

        # Tầng 2: PhoBERT
        phobert_tag, phobert_conf = self.predict_phobert(text)
        if phobert_conf >= self.phobert_threshold:
            return phobert_tag, phobert_conf, "PhoBERT"

        # Tầng 3: Chọn model có confidence cao hơn
        if lstm_conf >= phobert_conf:
            return lstm_tag, lstm_conf, "LSTM(low)"
        return phobert_tag, phobert_conf, "PhoBERT(low)"

    def get_response(self, text: str, confidence_threshold: float = 0.5) -> dict:
        """Lấy response dựa trên intent được dự đoán."""
        tag, confidence, source = self.predict_intent(text)

        if confidence < confidence_threshold:
            return {
                "intent": "unknown",
                "confidence": confidence,
                "response": "Xin lỗi, tôi chưa hiểu ý bạn. Bạn có thể nói rõ hơn không?",
                "entities": {},
                "source": source,
            }

        entities = extract_entities(text, tag)

        # Tạo response từ template
        templates = RESPONSE_TEMPLATES.get(tag, ["Tôi đã hiểu yêu cầu của bạn."])
        task_name = entities.get("task_name")

        if task_name:
            tw = [t for t in templates if "{task_name}" in t]
            response = random.choice(tw).format(task_name=task_name) if tw else random.choice(templates)
        else:
            tw = [t for t in templates if "{task_name}" not in t]
            response = random.choice(tw) if tw else random.choice(templates).replace("'{task_name}'", "công việc")

        return {
            "intent": tag,
            "confidence": confidence,
            "response": response,
            "entities": entities,
            "source": source,
        }
