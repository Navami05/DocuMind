from sentence_transformers import SentenceTransformer


# Load the model once when the application starts
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):
    """
    Convert text into a numerical vector.
    """

    embedding = model.encode(text)

    return embedding.tolist()


def generate_embeddings(texts: list[str]):
    """
    Convert multiple text chunks into numerical vectors.
    """

    embeddings = model.encode(texts)

    return embeddings.tolist()