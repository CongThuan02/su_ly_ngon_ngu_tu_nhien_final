import torch
import torch.nn as nn


class PhoBERTClassifier(nn.Module):
    def __init__(self, phobert_base, num_classes: int, dropout: float = 0.3):
        super().__init__()
        self.phobert = phobert_base
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(phobert_base.config.hidden_size, num_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        output = self.dropout(cls_output)
        output = self.fc(output)
        return output
