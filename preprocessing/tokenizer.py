import io
import re
from typing import TextIO
import tiktoken

class Tokenizer:
    def __init__(self, f: TextIO):
        self.token_to_id = generate_token_id(text_to_tokens(f))
        self.id_to_token = {i: s for s, i in self.token_to_id.items()}

    def encode(self, text):
        preprocessed = re.split(r'([,.?_!"()\']|--|\s)', text)
        preprocessed = [item.strip() for item in preprocessed if item.strip()]
        preprocessed = [item if item in self.token_to_id  # A
                        else "<|unk|>" for item in preprocessed]
        ids = [self.token_to_id[s] for s in preprocessed]
        return ids

    def decode(self, ids):
        text = " ".join([self.id_to_token[id] for id in ids])
        text = re.sub(r'\s+([,.?!"()\'])', r'\1', text)  # E
        return text


def text_to_tokens(f: TextIO) -> list[str]:
    raw_text = f.read()
    preprocessed = re.split(r'([,.?_!"()\']|--|\s)', raw_text)
    preprocessed = [item.strip() for item in preprocessed if item.strip()]
    f.close()
    return preprocessed


def generate_token_id(tokens: list) -> dict:
    all_words = sorted(list(set(tokens)))
    all_words.extend(["<|endoftext|>", "<|unk|>"])
    tokens_to_ids = {token:integer for integer, token in enumerate(all_words)}
    return tokens_to_ids


if __name__ == '__main__':
    # f = open("the_verdict.txt", "r", encoding="utf-8")
    # preprocessing = Tokenizer(f)
    # text1 = "Hello, do you like tea?"
    # text2 = "In the sunlit terraces of the palace."
    # text = " <|endoftext|> ".join((text1, text2))
    # print(text)
    # ids = preprocessing.encode(text)
    # print(ids)
    # print(preprocessing.decode(ids))
    
    tokenizer = tiktoken.encoding_for_model("gpt-4")
    text = "Hello, do you like tea? <|endoftext|> In the sunlit terraces of someunknownPlace."
    integers = tokenizer.encode(text, allowed_special={"<|endoftext|>"})
    print(integers)
    strings = tokenizer.decode(integers)
    print(strings)