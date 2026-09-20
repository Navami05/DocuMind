
from sentence_transformers import CrossEncoder


# Local reranking model.
#
# This model runs on your computer.
# It does NOT require an API key.
# It does NOT consume OpenAI/Gemini credits.
model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def get_section_boost(
    query: str,
    section: str
):
    """
    Give a section-specific relevance boost
    based on the user's question.

    The boost helps the system recognize
    questions that refer to specific sections
    of the document.
    """

    query_lower = query.lower()
    section_lower = section.lower()

    boost = 0.0

    # ========================================
    # Architecture-related questions
    # ========================================

    if any(
        keyword in query_lower
        for keyword in [
            "architecture",
            "architectural",
            "layers",
            "components",
            "component"
        ]
    ):

        if (
            "layers of spmr system architecture"
            in section_lower
        ):
            boost = 3.0

        elif (
            "system architecture"
            in section_lower
        ):
            boost = 1.5

        elif (
            "proposed spmr framework"
            in section_lower
        ):
            boost = 0.5


    # ========================================
    # Limitations-related questions
    # ========================================

    if any(
        keyword in query_lower
        for keyword in [
            "limitation",
            "limitations",
            "limitation of existing systems",
            "limitations of existing systems",
            "existing system limitations"
        ]
    ):

        if (
            "limitations of existing systems"
            in section_lower
        ):
            boost = 4.0


    # ========================================
    # Objectives-related questions
    # ========================================

    if any(
        keyword in query_lower
        for keyword in [
            "objective",
            "objectives",
            "goal",
            "goals",
            "aim",
            "aims"
        ]
    ):

        if "objective" in section_lower:
            boost = 4.0


    # ========================================
    # Proposed framework questions
    # ========================================

    if any(
        keyword in query_lower
        for keyword in [
            "proposed framework",
            "spmr framework",
            "proposed system"
        ]
    ):

        if "proposed spmr framework" in section_lower:
            boost = 4.0


    # ========================================
    # Working-related questions
    # ========================================

    if any(
        keyword in query_lower
        for keyword in [
            "working",
            "how does spmr work",
            "how spmr works",
            "working of spmr"
        ]
    ):

        if "working of spmr" in section_lower:
            boost = 4.0


    # ========================================
    # Advantages and challenges
    # ========================================

    if any(
        keyword in query_lower
        for keyword in [
            "advantage",
            "advantages",
            "benefit",
            "benefits",
            "challenge",
            "challenges"
        ]
    ):

        if (
            "advantages and challenges"
            in section_lower
        ):
            boost = 4.0


    # ========================================
    # Future scope questions
    # ========================================

    if any(
        keyword in query_lower
        for keyword in [
            "future",
            "future scope",
            "future work",
            "improvements",
            "improve"
        ]
    ):

        if "future scope" in section_lower:
            boost = 4.0


    # ========================================
    # Conclusion questions
    # ========================================

    if any(
        keyword in query_lower
        for keyword in [
            "conclusion",
            "summarize",
            "summary",
            "overall"
        ]
    ):

        if "conclusion" in section_lower:
            boost = 4.0


    return boost


def rerank_documents(
    query: str,
    documents: list[str],
    sections: list[str],
    top_k: int = 5
):
    """
    Rerank retrieved documents.

    The CrossEncoder provides the main relevance score.
    A section-specific boost is then added based on
    the question and the document's section.
    """

    if not documents:
        return []

    # Create query-document pairs.
    pairs = [
        [query, document]
        for document in documents
    ]

    # Calculate relevance scores locally.
    scores = model.predict(pairs)

    ranked_documents = []

    for document, section, score in zip(
        documents,
        sections,
        scores
    ):

        section_boost = get_section_boost(
            query,
            section
        )

        final_score = (
            float(score)
            + section_boost
        )

        ranked_documents.append(
            (
                document,
                final_score
            )
        )

    # Highest final score = most relevant.
    ranked_documents.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return ranked_documents[:top_k]

