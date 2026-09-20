import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def add_documents(
    ids: list[str],
    texts: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict]
):
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )


def document_exists(filename: str) -> bool:
    results = collection.get(
        where={
            "filename": filename
        },
        limit=1
    )

    return len(results["ids"]) > 0


def delete_document(filename: str):
    collection.delete(
        where={
            "filename": filename
        }
    )


def get_documents():
    results = collection.get(
        include=["metadatas"]
    )

    filenames = set()

    for metadata in results["metadatas"]:
        if metadata and metadata.get("filename"):
            filenames.add(metadata["filename"])

    return sorted(list(filenames))


def search_documents(
    query_embedding: list[float],
    number_of_results: int = 10,
    filename: str | None = None
):
    if filename:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=number_of_results,
            where={
                "filename": filename
            },
            include=["documents", "metadatas", "distances"]
        )
    else:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=number_of_results,
            include=["documents", "metadatas", "distances"]
        )

    return results