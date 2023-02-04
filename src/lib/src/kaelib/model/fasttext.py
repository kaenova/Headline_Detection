# https://arxiv.org/pdf/1607.01759.pdf

import torch 
import torch.nn as nn
from torchnlp.word_to_vector import FastText


class FastTextClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        
        # Model
        self.fasttext = FastText("id")
        self.feed_forward = nn.Sequential(
            nn.Linear(300, 10),
            nn.ReLU(),
            nn.Linear(10, 2),
        )

    def forward(self, x: "list[str]") -> torch.Tensor:
        
        # Prepare str
        x_tensor = []
        for sentence in x:
            sentence_seq = sentence.split(" ")
            # Average from word embedding to text embedding
            word_embedding = self.fasttext[sentence_seq].mean(dim=0)
            x_tensor.append(word_embedding)

        x_feed = torch.stack(x_tensor)
        y = self.feed_forward(x_feed)
        return y
