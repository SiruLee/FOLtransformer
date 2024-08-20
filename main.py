from gpt.util.gpt_generate import *
from gpt.util.interfaces import *

CHOOSE_MODEL = "gpt2-medium (355M)"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BASE_CONFIG = {
    "vocab_size": 50257,     # Vocabulary size
    "context_length": 1024,  # Context length
    "drop_rate": 0.0,        # Dropout rate
    "qkv_bias": True         # Query-key-value bias
}

model_configs = {
    "gpt2-small (124M)": {"emb_dim": 768, "n_layers": 12, "n_heads": 12},
    "gpt2-medium (355M)": {"emb_dim": 1024, "n_layers": 24, "n_heads": 16},
    "gpt2-large (774M)": {"emb_dim": 1280, "n_layers": 36, "n_heads": 20},
    "gpt2-xl (1558M)": {"emb_dim": 1600, "n_layers": 48, "n_heads": 25},
}

tokenizer = tiktoken.encoding_for_model("gpt-2")

model_size = CHOOSE_MODEL.split(" ")[-1].lstrip("(").rstrip(")")

BASE_CONFIG.update(model_configs[CHOOSE_MODEL])

gpt = init_gpt(BASE_CONFIG, model_size)

gpt.load_state_dict(torch.load("model/gpt2-medium355M-shp.pth"))

entry = {}

entry["instruction"] = "Translate the following input into the first-order logic statement."
entry['input'] = input("Input Prompt: ")

while entry['input'] != "quit":
    input_text = format_input(entry)
    output = input_gpt(
        model=gpt,
        input_prompt=input_text,
        tokenizer=tokenizer,
        max_new_tokens=50,
        device=device
    )

    response_text = (
        output[len(input_text):].replace("### Response:", "")
        .strip()
    )
    print(response_text)
    print("\n")
    entry['input'] = input("Input Prompt: ")

print("Terminated.")
