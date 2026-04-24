import json
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np

from models.lstm_model import ChatbotLSTM
from utils.text_preprocessor import load_intents, build_vocab, text_to_sequence

# ============ Config ============
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "intents.json")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "data")
MAX_LEN = 20
EMBEDDING_DIM = 128
HIDDEN_DIM = 128
NUM_LAYERS = 2
DROPOUT = 0.3
BATCH_SIZE = 16
EPOCHS = 200
LEARNING_RATE = 0.001


# ============ Dataset ============
class IntentDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.LongTensor(X)
        self.y = torch.LongTensor(y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# ============ Training ============
def train():
    print("Loading dataset...")
    intents = load_intents(DATA_PATH)
    word2idx, tags = build_vocab(intents)
    vocab_size = len(word2idx) + 1  # +1 for padding

    print(f"Vocab size: {vocab_size}")
    print(f"Tags: {tags}")
    print(f"Số lượng intent: {len(tags)}")

    # Chuẩn bị dữ liệu training
    X_train = []
    y_train = []

    for intent in intents["intents"]:
        tag = intent["tag"]
        tag_idx = tags.index(tag)
        for pattern in intent["patterns"]:
            seq = text_to_sequence(pattern, word2idx, MAX_LEN)
            X_train.append(seq)
            y_train.append(tag_idx)

    X_train = np.array(X_train)
    y_train = np.array(y_train)
    print(f"Training samples: {len(X_train)}")

    # DataLoader
    dataset = IntentDataset(X_train, y_train)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    model = ChatbotLSTM(
        vocab_size=vocab_size,
        embedding_dim=EMBEDDING_DIM,
        hidden_dim=HIDDEN_DIM,
        output_dim=len(tags),
        num_layers=NUM_LAYERS,
        dropout=DROPOUT,
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Training loop
    print("\nBắt đầu training...")
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        correct = 0
        total = 0

        for batch_X, batch_y in dataloader:
            batch_X = batch_X.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            _, predicted = torch.max(output, 1)
            correct += (predicted == batch_y).sum().item()
            total += batch_y.size(0)

        if (epoch + 1) % 20 == 0:
            accuracy = correct / total * 100
            avg_loss = total_loss / len(dataloader)
            print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.1f}%")

    # Lưu model và metadata
    model_path = os.path.join(MODEL_DIR, "chatbot_model.pth")
    metadata_path = os.path.join(MODEL_DIR, "model_metadata.json")

    torch.save(model.state_dict(), model_path)
    print(f"\nModel saved: {model_path}")

    metadata = {
        "word2idx": word2idx,
        "tags": tags,
        "vocab_size": vocab_size,
        "embedding_dim": EMBEDDING_DIM,
        "hidden_dim": HIDDEN_DIM,
        "num_layers": NUM_LAYERS,
        "dropout": DROPOUT,
        "max_len": MAX_LEN,
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Metadata saved: {metadata_path}")
    print("\nTraining hoàn tất!")


if __name__ == "__main__":
    train()
