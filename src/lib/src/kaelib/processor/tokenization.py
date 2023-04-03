import typing
import torch

from tokenizers import Tokenizer, models, pre_tokenizers, trainers

class WordTokenizer:
    def __init__(self, vocab_size=10000, min_frequency=2) -> None:
        self.vocab_size = vocab_size
        self.min_frequency = min_frequency

        self.special_vocab2id = {
            "[PAD]": 0,
            "[UNK]": 1,
        }
        self.special_id2vocab = {v: k for k, v in self.special_vocab2id.items()}
        self.special_token = list(self.special_vocab2id.keys())

        self.tokenizer = Tokenizer(
            models.WordLevel(vocab=self.special_vocab2id, unk_token="[UNK]")
        )
        self.tokenizer.pre_tokenizer = pre_tokenizers.Sequence(
            [pre_tokenizers.WhitespaceSplit()]
        )

        self.trainer = trainers.WordLevelTrainer(
            vocab_size=10000,
            min_frequency=5,
            special_tokens=self.special_token,
        )

    def train(self, corpus: "typing.List[str]"):
        self.tokenizer.train_from_iterator(corpus, trainer=self.trainer)

    def encode(self, text: "typing.List[str]", max_length=256) -> "torch.Tensor":
        self.tokenizer.enable_padding(
            direction="right", pad_id=self.special_vocab2id["[PAD]"], length=max_length
        )
        self.tokenizer.enable_truncation(max_length)

        tokenized = self.tokenizer.encode_batch(text)

        final_tokenized = []

        for encode in tokenized:
            final_tokenized.append(encode.ids)

        final_tokenized = torch.tensor(final_tokenized)

        self.tokenizer.no_padding()
        self.tokenizer.no_truncation()

        return final_tokenized
