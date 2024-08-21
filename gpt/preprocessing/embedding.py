import torch.nn
from gpt.preprocessing.dataset import init_dataloader

output_dim = 256
vocab_size = 100276


def init_input_embeddings(file):
    token_embedding_layer = torch.nn.Embedding(vocab_size, output_dim)

    raw_text = file.read()
    max_length = 4
    dataloader = init_dataloader(raw_text, batch_size=8, max_length=max_length, stride=max_length, shuffle=False)
    data_iter = iter(dataloader)
    inputs, targets = next(data_iter)
    # print("Token IDs:\n", inputs)
    # print("\nInputs shape:\n", inputs.shape)

    token_embeddings = token_embedding_layer(inputs)
    # print(token_embeddings.shape)

    context_length = max_length
    pos_embedding_layer = torch.nn.Embedding(context_length, output_dim)
    pos_embeddings = pos_embedding_layer(torch.arange(context_length))
    # print(pos_embeddings.shape)

    input_embeddings = token_embeddings + pos_embeddings
    # print(input_embeddings.shape)
    return input_embeddings


if __name__ == '__main__':
    f = open("the_verdict.txt", "r", encoding="utf-8")
    embedding = init_input_embeddings(f)
    print(embedding)
