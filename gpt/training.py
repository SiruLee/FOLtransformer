import tiktoken
import torch
from gpt.preprocessing.dataset import init_dataloader
from gpt.interfaces import GPT_CONFIG_124M, GPTModel
from gpt.util.gpt_generate import generate
import matplotlib.pyplot as plt


def plot_losses(epochs_seen, tokens_seen, train_losses, val_losses):
    fig, ax1 = plt.subplots(figsize=(5, 3))
    ax1.plot(epochs_seen, train_losses, label="Training loss")
    ax1.plot(epochs_seen, val_losses, linestyle="-.", label="Validation loss")
    ax1.set_xlabel("Epochs")
    ax1.set_ylabel("Loss")
    ax1.legend(loc="upper right")
    ax2 = ax1.twiny()  # A
    ax2.plot(tokens_seen, train_losses, alpha=0)  # B
    ax2.set_xlabel("Tokens seen")
    fig.tight_layout()
    plt.show()


def text_to_token_ids(text, tokenizer):
    encoded = tokenizer.encode(text, allowed_special={'<|endoftext|>'})
    encoded_tensor = torch.tensor(encoded).unsqueeze(0)  # add batch dimension
    return encoded_tensor


def token_ids_to_text(token_ids, tokenizer):
    flat = token_ids.squeeze(0)  # remove batch dimension
    return tokenizer.decode(flat.tolist())


def calc_loss_batch(input_batch, target_batch, model, device):
    input_batch, target_batch = input_batch.to(device), target_batch.to(device)
    logits = model(input_batch)
    loss = torch.nn.functional.cross_entropy(
        logits.flatten(0, 1), target_batch.flatten()
    )
    return loss


def calc_loss_loader(data_loader, model, device, num_batches=None):
    total_loss = 0.
    if num_batches is None:
        num_batches = len(data_loader) #A
    else:
        num_batches = min(num_batches, len(data_loader)) #B
    for i, (input_batch, target_batch) in enumerate(data_loader):
        if i < num_batches:
            loss = calc_loss_batch(input_batch, target_batch, model, device)
            total_loss += loss.item() #C
        else:
            break
    return total_loss / num_batches #D


def evaluate_model(model, train_loader, val_loader, device, eval_iter):
    model.eval() #A
    with torch.no_grad(): #B
        train_loss = calc_loss_loader(train_loader, model, device, num_batches=eval_iter)
        val_loss = calc_loss_loader(val_loader, model, device, num_batches=eval_iter)
    model.train()
    return train_loss, val_loss


def train_model_simple(model, train_loader, val_loader, optimizer, device, num_epochs,
                       eval_freq, eval_iter, start_context):
    train_losses, val_losses, track_tokens_seen = [], [], []  # A
    tokens_seen, global_step = 0, -1

    for epoch in range(num_epochs):  # B
        model.train()
        for input_batch, target_batch in train_loader:
            optimizer.zero_grad()  # C
            loss = calc_loss_batch(input_batch, target_batch, model, device)
            loss.backward()  # D
            optimizer.step()  # E
            tokens_seen += input_batch.numel()
            global_step += 1

            if global_step % eval_freq == 0:  # F
                train_loss, val_loss = evaluate_model(
                    model, train_loader, val_loader, device, eval_iter)
                train_losses.append(train_loss)
                val_losses.append(val_loss)
                track_tokens_seen.append(tokens_seen)
                print(f"Ep {epoch + 1} (Step {global_step:06d}): "
                      f"Train loss {train_loss:.3f}, Val loss {val_loss:.3f}")
    return train_losses, val_losses, track_tokens_seen


if __name__ == '__main__':

    """
    Calculation of Training Loss and Validation Loss example
    """
    file_path = "preprocessing/the_verdict.txt"
    with open(file_path, "r", encoding="utf-8") as file:
        text_data = file.read()

    train_ratio = 0.90
    split_idx = int(train_ratio * len(text_data))
    train_data = text_data[:split_idx]
    val_data = text_data[split_idx:]

    train_loader = init_dataloader(
        train_data,
        batch_size=2,
        max_length=GPT_CONFIG_124M["context_length"],
        stride=GPT_CONFIG_124M["context_length"],
        drop_last=True,
        shuffle=True
    )
    val_loader = init_dataloader(
        val_data,
        batch_size=2,
        max_length=GPT_CONFIG_124M["context_length"],
        stride=GPT_CONFIG_124M["context_length"],
        drop_last=False,
        shuffle=False
    )

    model = GPTModel(GPT_CONFIG_124M)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # A
    model.to(device)
    train_loss = calc_loss_loader(train_loader, model, device)  # B
    val_loss = calc_loss_loader(val_loader, model, device)
    print("Training loss:", train_loss)
    print("Validation loss:", val_loss)


    """
    Test train_model_simple
    """
    torch.manual_seed(123)
    model = GPTModel(GPT_CONFIG_124M)
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0004, weight_decay=0.1)  # A
    num_epochs = 10
    train_losses, val_losses, tokens_seen = train_model_simple(
        model, train_loader, val_loader, optimizer, device,
        num_epochs=num_epochs, eval_freq=5, eval_iter=None,
        start_context="Every effort moves you"
    )

    epochs_tensor = torch.linspace(0, num_epochs, len(train_losses))
    plot_losses(epochs_tensor, tokens_seen, train_losses, val_losses)

    model.to("cpu")
    model.eval()

    tokenizer = tiktoken.get_encoding("gpt2")
    token_ids = generate(
        model=model,
        idx=text_to_token_ids("Every effort moves you", tokenizer),
        max_new_tokens=15,
        context_size=GPT_CONFIG_124M["context_length"],
        top_k=25,
        temperature=1.4
    )
    print("Output text:\n", token_ids_to_text(token_ids, tokenizer))


