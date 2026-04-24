import re
import json

try:
    from underthesea import word_tokenize
except ImportError:  # pragma: no cover - fallback for lightweight/dev environments
    word_tokenize = None


def load_intents(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def tokenize_vi(text: str) -> list[str]:
    """Tách từ tiếng Việt sử dụng underthesea."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", "", text)
    if word_tokenize is None:
        tokens = text.split()
    else:
        tokens = word_tokenize(text, format="text").split()
    return tokens


def build_vocab(intents: dict) -> tuple[dict, list]:
    """Xây dựng từ điển từ dataset intents."""
    all_words = set()
    tags = []

    for intent in intents["intents"]:
        tag = intent["tag"]
        if tag not in tags:
            tags.append(tag)
        for pattern in intent["patterns"]:
            tokens = tokenize_vi(pattern)
            all_words.update(tokens)

    all_words = sorted(all_words)
    word2idx = {word: idx + 1 for idx, word in enumerate(all_words)}  # 0 reserved for padding
    return word2idx, tags


def text_to_sequence(text: str, word2idx: dict, max_len: int = 20) -> list[int]:
    """Chuyển text thành sequence số."""
    tokens = tokenize_vi(text)
    sequence = [word2idx.get(token, 0) for token in tokens]

    # Padding hoặc truncate
    if len(sequence) < max_len:
        sequence = sequence + [0] * (max_len - len(sequence))
    else:
        sequence = sequence[:max_len]

    return sequence
