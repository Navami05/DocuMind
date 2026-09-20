
import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.

    Removes:
    - excessive whitespace
    - repeated page headers/footers
    - page numbers
    - presentation metadata
    - common PDF extraction artifacts
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove common presentation footer/header information
    patterns = [
        r"Navami Sajeev",
        r"SPMR\s*6\s*August,\s*2026",
        r"6\s*August,\s*2026",
        r"\b\d+\s*/\s*\d+\b",
    ]

    for pattern in patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    # Remove standalone page numbers
    text = re.sub(
        r"(?m)^\s*\d+\s*$",
        "",
        text
    )

    # Remove repeated whitespace
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


def create_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
):
    """
    Split document text into overlapping chunks.
    """

    if not text:
        return []

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():

            chunks.append(
                chunk.strip()
            )

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def detect_section(text: str) -> str:
    """
    Detect the main section represented by a page.

    Exact section headings are checked first.
    This prevents phrases appearing in the
    table of contents from incorrectly determining
    the section.
    """

    text_lower = text.lower()

    # ========================================
    # Exact / highly specific section headings
    # ========================================

    section_keywords = [

        (
            "Limitations of Existing Systems",
            [
                "limitations of existing systems"
            ]
        ),

        (
            "Advantages and Challenges",
            [
                "advantages and challenges"
            ]
        ),

        (
            "Future Scope",
            [
                "future scope"
            ]
        ),

        (
            "Proposed Deep Learning Algorithm",
            [
                "proposed deep learning algorithm",
                "deep learning algorithm for lpm and cpm"
            ]
        ),

        (
            "Working of SPMR",
            [
                "working of spmr"
            ]
        ),

        (
            "Layers of SPMR System Architecture",
            [
                "layers of spmr system architecture",
                "ambient assisted living",
                "local information processing",
                "cloud management module",
                "cloud analytics management"
            ]
        ),

        (
            "System Architecture",
            [
                "system architecture"
            ]
        ),

        (
            "Proposed SPMR Framework",
            [
                "proposed spmr framework"
            ]
        ),

        (
            "Conclusion",
            [
                "conclusion"
            ]
        ),

        (
            "Introduction",
            [
                "introduction"
            ]
        ),

        (
            "Objectives",
            [
                "objectives"
            ]
        )
    ]

    # ========================================
    # Check headings
    # ========================================

    for section, keywords in section_keywords:

        for keyword in keywords:

            if keyword in text_lower:

                # Avoid incorrectly classifying
                # the table of contents as a real section.
                #
                # If the page contains many section
                # names together, it is most likely
                # the contents page.

                contents_indicators = [
                    "contents",
                    "limitations of existing systems",
                    "objectives",
                    "proposed spmr framework",
                    "system architecture",
                    "working of spmr",
                    "proposed algorithm",
                    "experimental setup",
                    "performance evaluation",
                    "advantages and challenges",
                    "future scope",
                    "conclusion"
                ]

                indicator_count = sum(
                    1
                    for indicator in contents_indicators
                    if indicator in text_lower
                )

                # A page containing many section headings
                # is most likely a contents page.
                if indicator_count >= 5:

                    return "Table of Contents"

                return section

    return "General"

