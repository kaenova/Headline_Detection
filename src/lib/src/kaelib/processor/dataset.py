import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizerBase
from tokenizers import Tokenizer


class HuggingfaceHeadlineDataset(Dataset):
    def __init__(
        self,
        csv_path: "str",
        tokenizer: "PreTrainedTokenizerBase",
        **tokenizer_call_kwarg
    ):
        """
        Create dataset and get the dataset from 'tweet' and 'labels' columns
        """
        df = pd.read_csv(csv_path)
        self.length = len(df)
        tokenized = tokenizer(df["tweet"].to_list(), **tokenizer_call_kwarg)
        
        self.input_ids = tokenized["input_ids"]
        self.attention_mask = tokenized["attention_mask"]
        self.labels = torch.tensor(df['labels'].to_list(), dtype=torch.int64)

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx], # type: ignore
            "attention_mask": self.attention_mask[idx], # type: ignore
        }, self.labels[idx]
        
class TokenizerHeadlineDataset(Dataset):
    def __init__(
        self,
        csv_path: "str",
        tokenizer: "Tokenizer",
        **tokenizer_call_kwarg
    ):
        """
        Create dataset and get the dataset from 'tweet' and 'labels' columns
        """
        df = pd.read_csv(csv_path)
        self.length = len(df)
        tokenized = tokenizer.encode(df["tweet"].to_list())
        
        self.input_ids = tokenized["input_ids"]
        self.attention_mask = tokenized["attention_mask"]
        self.labels = torch.tensor(df['labels'].to_list(), dtype=torch.int64)

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
        }, self.labels[idx]
