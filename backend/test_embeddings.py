from services.embedding_service import generate_embedding


text = "This is a test document about artificial intelligence."

embedding = generate_embedding(text)

print("Embedding generated successfully!")
print("Vector length:", len(embedding))
print("First 5 values:", embedding[:5])