from services.embedding_service import generate_embeddings
from services.vector_store import add_documents, search_documents


texts = [
    "Python is a programming language used for software development.",
    "Machine learning allows computers to learn patterns from data.",
    "The Earth revolves around the Sun."
]


# Generate embeddings for our test sentences
embeddings = generate_embeddings(texts)


# Store the test data
add_documents(
    ids=["test-1", "test-2", "test-3"],
    texts=texts,
    embeddings=embeddings,
    metadatas=[
        {"source": "test", "page": 1},
        {"source": "test", "page": 2},
        {"source": "test", "page": 3}
    ]
)


# Search using a question
query = "What is machine learning?"

query_embedding = generate_embeddings([query])[0]


results = search_documents(query_embedding, 2)


print("\nSearch results:")
print("----------------")

for document in results["documents"][0]:
    print(document)