from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import fitz
import uuid

from services.document_processor import (
    clean_text,
    create_chunks,
    detect_section
)

from services.embedding_service import generate_embeddings

from services.vector_store import (
    add_documents,
    search_documents,
    document_exists,
    get_documents,
    delete_document
)

from services.reranker import rerank_documents

from services.answer_generator import (
    generate_answer,
    is_architecture_question
)


app = FastAPI(title="AI Document RAG API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Document RAG API is running"
    }


@app.get("/documents")
def list_documents():
    return {
        "documents": get_documents()
    }

@app.delete("/documents/{filename}")
def delete_document_endpoint(filename: str):

    delete_document(filename)

    return {
        "filename": filename,
        "message": "Document deleted successfully."
    }

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if document_exists(file.filename):
        return {
            "filename": file.filename,
            "message": "This document has already been uploaded.",
            "duplicate": True
        }

    contents = await file.read()

    document = fitz.open(
        stream=contents,
        filetype="pdf"
    )

    texts = []
    metadatas = []

    for page_number, page in enumerate(document):

        text = page.get_text()

        text = clean_text(text)

        section = detect_section(text)

        chunks = create_chunks(text)

        for chunk in chunks:

            texts.append(chunk)

            metadatas.append({
                "filename": file.filename,
                "page": page_number + 1,
                "section": section
            })

    document.close()

    if not texts:
        return {
            "filename": file.filename,
            "message": "No text could be extracted from this PDF.",
            "duplicate": False
        }

    embeddings = generate_embeddings(texts)

    ids = [
        str(uuid.uuid4())
        for _ in texts
    ]

    add_documents(
        ids=ids,
        texts=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "filename": file.filename,
        "total_chunks": len(texts),
        "message": "PDF processed and stored successfully.",
        "duplicate": False
    }


@app.post("/search")
async def search(
    query: str,
    filename: str | None = None
):

    query_embedding = generate_embeddings(
        [query]
    )[0]

    results = search_documents(
        query_embedding=query_embedding,
        number_of_results=19,
        filename=filename
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    candidates = []

    seen = set()

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        if document in seen:
            continue

        if len(document.strip()) < 50:
            continue

        seen.add(document)

        candidates.append({
            "text": document,
            "filename": metadata.get("filename"),
            "page": metadata.get("page"),
            "section": metadata.get("section"),
            "distance": distance
        })

    candidate_texts = [
        candidate["text"]
        for candidate in candidates
    ]

    candidate_sections = [
        candidate.get(
            "section",
            "General"
        )
        for candidate in candidates
    ]

    reranked = rerank_documents(
        query=query,
        documents=candidate_texts,
        sections=candidate_sections,
        top_k=5
    )

    if is_architecture_question(query):

        filtered_reranked = []

        for document, score in reranked:

            for candidate in candidates:

                if candidate["text"] == document:

                    section = candidate.get(
                        "section",
                        "General"
                    )

                    if (
                        "architecture"
                        in section.lower()
                        or
                        "proposed spmr framework"
                        in section.lower()
                    ):
                        filtered_reranked.append(
                            (document, score)
                        )

                    break

        if filtered_reranked:
            reranked = filtered_reranked

    elif "limitation" in query.lower():

        filtered_reranked = []

        for document, score in reranked:

            for candidate in candidates:

                if candidate["text"] == document:

                    section = candidate.get(
                        "section",
                        "General"
                    )

                    if (
                        "limitations of existing systems"
                        in section.lower()
                    ):
                        filtered_reranked.append(
                            (document, score)
                        )

                    break

        if filtered_reranked:
            reranked = filtered_reranked

    final_results = []

    for document, score in reranked:

        matching_candidate = next(
            (
                candidate
                for candidate in candidates
                if candidate["text"] == document
            ),
            None
        )

        if matching_candidate is None:
            continue

        final_results.append({
            "text": document,
            "filename": matching_candidate["filename"],
            "page": matching_candidate["page"],
            "section": matching_candidate.get(
                "section"
            ),
            "rerank_score": float(score)
        })

    answer_results = final_results[:3]

    context_parts = []

    for result in answer_results:

        context_parts.append(
            f"""
Page: {result['page']}
Section: {result['section']}

{result['text']}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    if context:

        answer = generate_answer(
            query=query,
            context=context
        )

    else:

        answer = (
            "I could not find relevant information "
            "in the selected document."
        )

    return {
        "query": query,
        "filename": filename,
        "answer": answer,
        "results": final_results
    }