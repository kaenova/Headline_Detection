import typing
import torch

from tokenizers import Tokenizer, models, pre_tokenizers, trainers


class WordTokenizer:
    special_vocab2id = {
        "[PAD]": 0,
        "[UNK]": 1,
    }
    special_id2vocab = {v: k for k, v in special_vocab2id.items()}
    special_token = list(special_vocab2id.keys())

    def __init__(self, vocab_size=10000) -> None:
        self.vocab_size = vocab_size

        self.tokenizer = Tokenizer(
            models.WordLevel(vocab=self.special_vocab2id, unk_token="[UNK]")
        )

        self.tokenizer.pre_tokenizer = pre_tokenizers.Sequence(
            [pre_tokenizers.WhitespaceSplit()]
        )  # type: ignore

    def train(self, corpus: "typing.List[str]", min_frequency=2):
        trainer = trainers.WordLevelTrainer(
            vocab_size=self.vocab_size,
            min_frequency=min_frequency,
            special_tokens=self.special_token,
        )  # type: ignore

        self.tokenizer.train_from_iterator(corpus, trainer=trainer)

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

    def save(self, path: "str"):
        self.tokenizer.save(path)

    def __init_from_path__(self, path):
        self.tokenizer.from_file(path)

    @classmethod
    def load(cls, path):
        obj = cls.__new__(cls)
        obj.tokenizer = Tokenizer.from_file(path)
        return obj


if __name__ == "__main__":
    sample_text = [
        "hello who are you?",
        "are you fine with it?",
        "so what are you doing",
    ]

    tokenizer = WordTokenizer(100000)

    tokenizer.train(sample_text, 2)

    print(tokenizer.encode(["hello are you fine?"]))

    tokenizer.save("tokenizer.json")

    new_tokenizer = WordTokenizer.load(".test/tokenizer.json")

    print(new_tokenizer.encode(["hello are you fine?"]))
