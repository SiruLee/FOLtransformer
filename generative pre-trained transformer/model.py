import tiktoken
from interfaces import *


def generate_text_simple(model, idx, max_new_tokens, context_size):  # A
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -context_size:]  # B
        with torch.no_grad():
            logits = model(idx_cond)

        logits = logits[:, -1, :]  # C
        probas = torch.softmax(logits, dim=-1)  # D
        idx_next = torch.argmax(probas, dim=-1, keepdim=True)  # E
        idx = torch.cat((idx, idx_next), dim=1)  # F

    return idx


if __name__ == '__main__':
    tokenizer = tiktoken.encoding_for_model("gpt-2")
    start_context = "Hello, I am"
    encoded = tokenizer.encode(start_context)
    print("encoded:", encoded)
    encoded_tensor = torch.tensor(encoded).unsqueeze(0) #A
    print("encoded_tensor.shape:", encoded_tensor.shape)

    model = GPTModel(GPT_CONFIG_124M)
    model.eval()  # A
    out = generate_text_simple(
        model=model,
        idx=encoded_tensor,
        max_new_tokens=6,
        context_size=GPT_CONFIG_124M["context_length"]
    )
    print("Output:", out)
    print("Output length:", len(out[0]))

    decoded_text = tokenizer.decode(out.squeeze(0).tolist())
    print(decoded_text)