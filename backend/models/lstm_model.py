import torch
import torch.nn as nn


class ChatbotLSTM(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int, hidden_dim: int, output_dim: int,
                 num_layers: int = 2, dropout: float = 0.3):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)  # *2 vì bidirectional

    def forward(self, x):
        # x: (batch_size, seq_len)
        embedded = self.embedding(x)  # (batch_size, seq_len, embedding_dim)
        lstm_out, (hidden, _) = self.lstm(embedded)

        # Lấy hidden state từ 2 hướng của layer cuối
        hidden_fwd = hidden[-2]  # (batch_size, hidden_dim)
        hidden_bwd = hidden[-1]  # (batch_size, hidden_dim)
        hidden_cat = torch.cat((hidden_fwd, hidden_bwd), dim=1)  # (batch_size, hidden_dim*2)

        output = self.dropout(hidden_cat)
        output = self.fc(output)  # (batch_size, output_dim)
        return output
