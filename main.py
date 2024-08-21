from gpt.util.gpt_generate import *
from gpt.interfaces import *
from mace4.mace4 import run_mace4
from parser.mace4_to_json import parse_model_output
from datetime import datetime

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

gpt.load_state_dict(torch.load("./gpt/model/gpt2-medium355M-shp.pth"))

# clear the terminal
os.system('cls' if os.name == 'nt' else 'clear')

print("============ MACE4 CONFIGURATION ===========")
domain_size = int(input("Mace4 Model Domain Size (default 2): "))
while domain_size < 2:
    print("The domain size must be in the range [2 ... 2147483647]")
    domain_size = int(input("Mace4 Model Domain Size (default >2): "))
max_models = int(input("Mace4 Number of Model (default 1): "))

# clear the terminal
os.system('cls' if os.name == 'nt' else 'clear')

entry = {}

entry["instruction"] = "Translate the following input into the first-order logic statement."
entry['input'] = input("Input Prompt: ")

while entry['input'] != "quit":
    output_name = entry['input'].replace(" ", "-").rstrip(".")

    if entry['input'].startswith("-ignore"):
        output_name = "custom_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        entry['input'] = entry['input'].lstrip("-ignore")
        run_mace4(entry['input'] + ".", "output", output_name,
                  "./mace4/input/fusion.in", domain_size=domain_size, max_models=max_models, model_output=1)

    else:
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
        run_mace4(response_text + ".", "output", output_name, "./mace4/input/fusion.in",
                  domain_size=domain_size, max_models=max_models, model_output=1)

    with open(f"./mace4/output/{output_name}.out", "r") as f:
        parse_model_output(f.read(), output_name, max_models)

    entry['input'] = input("\nInput Prompt: ")
print("Terminated.")
