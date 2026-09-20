from services.vector_store import collection


print("\n==============================")
print("       CHROMA DATABASE")
print("==============================")


# Get all stored documents
data = collection.get()


documents = data.get("documents", [])
metadatas = data.get("metadatas", [])


print(f"Total stored chunks: {len(documents)}")


for index, (document, metadata) in enumerate(
    zip(documents, metadatas),
    start=1
):

    print(f"\n--- Chunk {index} ---")

    print(
        "Filename:",
        metadata.get("filename")
    )

    print(
        "Page:",
        metadata.get("page")
    )

    print(
        "Section:",
        metadata.get("section")
    )

    print("Text:")

    print(document)