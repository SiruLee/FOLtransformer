import torch
import tiktoken
from torch.utils.data import Dataset, DataLoader


class GPTDataset(Dataset):
    def __init__(self, txt, tokenizer, max_len, stride):
        self.tokenizer = tokenizer
        self.input_ids = []
        self.target_ids = []

        token_ids = tokenizer.encode(txt)

        for i in range(0, len(token_ids) - max_len, stride):
            input_slice = token_ids[i:i + max_len]
            target_slice = token_ids[i + 1:i + max_len + 1]
            self.input_ids.append(torch.tensor(input_slice))
            self.target_ids.append(torch.tensor(target_slice))

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.target_ids[idx]


def init_dataloader(txt, batch_size=4, max_length=256, stride=128, shuffle=True, drop_last=True):
    tokenizer = tiktoken.encoding_for_model("gpt-4")
    dataset = GPTDataset(txt, tokenizer, max_length, stride)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, drop_last=drop_last)
    return dataloader


if __name__ == '__main__':
    with open("the_verdict.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    dataloader = init_dataloader(raw_text, batch_size=8, max_length=4, stride=4, shuffle=False)
    data_iter = iter(dataloader)
    inputs, targets = next(data_iter)
    print("Inputs:\n", inputs)
    print("\nTargets:\n", targets)

    tokenizer = tiktoken.encoding_for_model("gpt-4")
    print(tokenizer.max_token_value)