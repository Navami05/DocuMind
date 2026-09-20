
from services.reranker import rerank_documents


query = "explain the architecture of SPMR"


documents = [
    """
    Contents
    Introduction
    Objectives
    System Architecture
    Working of SPMR
    Conclusion
    """,

    """
    Performance Evaluation - Prediction Accuracy.
    The proposed SPMR achieves higher prediction accuracy
    than existing methods.
    """,

    """
    Layers of SPMR System Architecture

    Ambient Assisted Living Layer collects physiological
    and contextual information using IoT devices and
    smart sensors.

    Local Information Processing (LIP) Layer performs
    initial processing near the patient and detects
    emergency conditions.

    Cloud Management Module (CMM) stores and manages
    current and historical patient information.

    Cloud Analytics Management (CAM) applies deep learning
    models for health prediction and generates
    personalized recommendations and alerts.
    """,

    """
    Working of SPMR

    Sensors collect physiological and contextual data.
    LIP performs local processing.
    CMM manages patient information.
    CAM performs cloud analysis and generates
    recommendations and alerts.
    """
]


results = rerank_documents(
    query=query,
    documents=documents,
    top_k=4
)


print("\n==============================")
print("         RERANKING TEST")
print("==============================")


for rank, (document, score) in enumerate(
    results,
    start=1
):

    print(f"\nRank: {rank}")
    print(f"Score: {score:.4f}")
    print("Text:")
    print(document.strip())

