
import re


def clean_context(context: str):
    """
    Remove metadata and PDF extraction artifacts
    before generating the answer.
    """

    lines = context.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove page metadata
        if line.lower().startswith("page:"):
            continue

        # Remove section metadata
        if line.lower().startswith("section:"):
            continue

        cleaned_lines.append(line)

    text = " ".join(cleaned_lines)

    # Remove common document metadata
    metadata_patterns = [
        r"Department of Computer Science and Engineering",
        r"Model Engineering College, Thrikkakara",
        r"Smart Patient Monitoring and Recommendation "
        r"\(SPMR\) using Cloud Analytics and Deep Learning"
    ]

    for pattern in metadata_patterns:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    # Remove excessive whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# ARCHITECTURE
# ============================================================

def extract_layer_description(
    text: str,
    start_pattern: str,
    end_patterns: list[str]
):
    """
    Extract the text belonging to one architecture layer.
    """

    match = re.search(
        start_pattern,
        text,
        flags=re.IGNORECASE
    )

    if not match:
        return ""

    start = match.end()

    remaining_text = text[start:]

    end_positions = []

    for pattern in end_patterns:

        end_match = re.search(
            pattern,
            remaining_text,
            flags=re.IGNORECASE
        )

        if end_match:
            end_positions.append(
                end_match.start()
            )

    if end_positions:

        end = min(end_positions)

        description = remaining_text[:end]

    else:

        description = remaining_text

    return description.strip()


def extract_architecture(context: str):
    """
    Extract the four SPMR architecture layers.
    """

    text = clean_context(context)

    layer_patterns = [
        (
            "Ambient Assisted Living (AAL)",
            r"Ambient Assisted Living(?: Layer)?",
            [
                r"Local Information Processing",
                r"Cloud Management Module",
                r"Cloud Analytics Management"
            ]
        ),

        (
            "Local Information Processing (LIP)",
            r"Local Information Processing \(?LIP\)?(?: Layer)?",
            [
                r"Cloud Management Module",
                r"Cloud Analytics Management"
            ]
        ),

        (
            "Cloud Management Module (CMM)",
            r"Cloud Management Module \(?CMM\)?(?: Layer)?",
            [
                r"Cloud Analytics Management"
            ]
        ),

        (
            "Cloud Analytics Management (CAM)",
            r"Cloud Analytics Management \(?CAM\)?(?: Layer)?",
            [
                r"\bConclusion\b",
                r"\bProposed SPMR Framework\b",
                r"\bWorking of SPMR\b"
            ]
        )
    ]

    layers = []

    for name, pattern, end_patterns in layer_patterns:

        description = extract_layer_description(
            text,
            pattern,
            end_patterns
        )

        if description:

            description = re.sub(
                r"\s+",
                " ",
                description
            ).strip()

            layers.append(
                {
                    "name": name,
                    "description": description
                }
            )

    return layers


def is_architecture_question(query: str):
    """
    Check whether the question is about architecture.
    """

    query_lower = query.lower()

    keywords = [
        "architecture",
        "architectural",
        "layers",
        "layer",
        "components",
        "component"
    ]

    return any(
        keyword in query_lower
        for keyword in keywords
    )


def generate_architecture_answer(
    query: str,
    context: str
):
    """
    Generate a clean structured answer
    for architecture-related questions.
    """

    layers = extract_architecture(
        context
    )

    if not layers:

        return (
            "I could not find the architecture "
            "details in the uploaded document."
        )

    answer = []

    answer.append(
        "SPMR uses a four-layer architecture "
        "for continuous patient monitoring "
        "and healthcare recommendation."
    )

    answer.append(
        "\nThe four layers are:"
    )

    for index, layer in enumerate(
        layers,
        start=1
    ):

        description = layer["description"]

        answer.append(
            f"\n{index}. {layer['name']}\n"
            f"   {description}"
        )

    answer.append(
        "\nOverall, the architecture collects "
        "patient data, performs local processing, "
        "manages patient information in the cloud, "
        "and applies cloud analytics for health "
        "condition prediction, recommendations, "
        "and alerts."
    )

    return "\n".join(answer).strip()


# ============================================================
# LIMITATIONS
# ============================================================

def extract_limitations(context: str):
    """
    Extract the four limitations from the
    Limitations of Existing Systems section.
    """

    text = clean_context(context)

    match = re.search(
        r"Limitations of Existing Systems",
        text,
        flags=re.IGNORECASE
    )

    if not match:
        return []

    text = text[match.end():]

    stop_match = re.search(
        r"\b(?:Objectives|Proposed SPMR Framework|"
        r"System Architecture|Working of SPMR|"
        r"Conclusion)\b",
        text,
        flags=re.IGNORECASE
    )

    if stop_match:
        text = text[:stop_match.start()]

    limitation_patterns = [
        (
            "Binary Classification",
            r"Binary Classification"
        ),
        (
            "Imbalanced Datasets",
            r"Imbalanced Datasets"
        ),
        (
            "Internet Dependence",
            r"Internet Dependence"
        ),
        (
            "Lack of Contextual Information",
            r"Lack of Contextual Information"
        )
    ]

    limitations = []

    for index, (name, pattern) in enumerate(
        limitation_patterns
    ):

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        start = match.end()

        next_positions = []

        for _, next_pattern in limitation_patterns[
            index + 1:
        ]:

            next_match = re.search(
                next_pattern,
                text[start:],
                flags=re.IGNORECASE
            )

            if next_match:
                next_positions.append(
                    next_match.start()
                )

        if next_positions:

            end = min(next_positions)

            description = text[
                start:start + end
            ]

        else:

            description = text[start:]

        description = re.sub(
            r"\s+",
            " ",
            description
        ).strip()

        if description:

            limitations.append(
                {
                    "name": name,
                    "description": description
                }
            )

    return limitations


def is_limitations_question(query: str):
    """
    Check whether the question is about
    limitations of existing systems.
    """

    query_lower = query.lower()

    return (
        "limitation" in query_lower
        or
        "limitations" in query_lower
    )


def generate_limitations_answer(
    query: str,
    context: str
):
    """
    Generate a structured answer for
    limitations-related questions.
    """

    limitations = extract_limitations(
        context
    )

    if not limitations:

        return (
            "I could not find the limitations "
            "of the existing systems in the "
            "uploaded document."
        )

    answer = []

    answer.append(
        "The limitations of the existing "
        "systems are:"
    )

    for index, limitation in enumerate(
        limitations,
        start=1
    ):

        answer.append(
            f"\n{index}. {limitation['name']}\n"
            f"   {limitation['description']}"
        )

    return "\n".join(answer).strip()


# ============================================================
# WORKING OF SPMR
# ============================================================


def extract_working_steps(context: str):
    """
    Extract the five working steps from
    the Working of SPMR section.

    Only the actual Working of SPMR content
    is used. Page/section metadata and other
    retrieved chunks are ignored.
    """

    # Find the Working of SPMR section
    match = re.search(
        r"Working of SPMR",
        context,
        flags=re.IGNORECASE
    )

    if not match:
        return []

    # Take everything after the heading
    text = context[match.end():]

    # ------------------------------------------------
    # Remove page/section metadata that may appear
    # between retrieved chunks.
    # ------------------------------------------------

    text = re.sub(
        r"Page:\s*\d+\s*Section:\s*",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # ------------------------------------------------
    # Stop when another retrieved section begins.
    # ------------------------------------------------

    stop_patterns = [
        r"\bProposed SPMR Framework\b",
        r"\bConclusion\b",
        r"\bIntroduction\b",
        r"\bFuture Scope\b",
        r"\bAdvantages and Challenges\b",
        r"\bLimitations of Existing Systems\b",
        r"\bObjectives\b",
        r"\bSystem Architecture\b"
    ]

    stop_positions = []

    for pattern in stop_patterns:

        stop_match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if stop_match:

            stop_positions.append(
                stop_match.start()
            )

    if stop_positions:

        text = text[
            :min(stop_positions)
        ]

    # ------------------------------------------------
    # Extract the five documented steps.
    # ------------------------------------------------

    step_patterns = [

        (
            "Data Collection",
            r"1\s+Data Collection"
        ),

        (
            "Local Processing",
            r"2\s+Local Processing"
        ),

        (
            "Data Management",
            r"3\s+Data Management"
        ),

        (
            "Cloud Analysis",
            r"4\s+Cloud Analysis"
        ),

        (
            "Recommendation and Alerts",
            r"5\s+Recommendation and Alerts"
        )
    ]

    steps = []

    for index, (name, pattern) in enumerate(
        step_patterns
    ):

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if not match:
            continue

        start = match.end()

        # Find the next numbered step.
        next_positions = []

        for _, next_pattern in step_patterns[
            index + 1:
        ]:

            next_match = re.search(
                next_pattern,
                text[start:],
                flags=re.IGNORECASE
            )

            if next_match:

                next_positions.append(
                    next_match.start()
                )

        if next_positions:

            end = min(next_positions)

            description = text[
                start:start + end
            ]

        else:

            description = text[start:]

        # Clean whitespace
        description = re.sub(
            r"\s+",
            " ",
            description
        ).strip()

        if description:

            steps.append(
                {
                    "name": name,
                    "description": description
                }
            )

    return steps




def is_working_question(query: str):
    """
    Check whether the question asks about
    the working or operation of SPMR.
    """

    query_lower = query.lower()

    working_phrases = [
        "how does spmr work",
        "how spmr works",
        "how does the spmr work",
        "working of spmr",
        "working of the spmr",
        "explain the working",
        "describe the working",
        "explain how spmr works",
        "describe how spmr works",
        "working process",
        "working process of spmr"
    ]

    if any(
        phrase in query_lower
        for phrase in working_phrases
    ):
        return True

    # Additional keyword-based detection
    # for variations of working questions.
    if (
        "working" in query_lower
        and "spmr" in query_lower
    ):
        return True

    if (
        "how" in query_lower
        and "spmr" in query_lower
        and (
            "operate" in query_lower
            or "function" in query_lower
            or "work" in query_lower
        )
    ):
        return True

    return False


def generate_working_answer(
    query: str,
    context: str
):
    """
    Generate a structured answer describing
    the working of SPMR.
    """

    steps = extract_working_steps(
        context
    )

    if not steps:

        return (
            "I could not find the working process "
            "of SPMR in the uploaded document."
        )

    answer = []

    answer.append(
        "The SPMR system works through a sequence "
        "of five main steps:"
    )

    for index, step in enumerate(
        steps,
        start=1
    ):

        answer.append(
            f"\n{index}. {step['name']}\n"
            f"   {step['description']}"
        )

    answer.append(
        "\nOverall, SPMR collects patient data, "
        "processes it locally, manages the data "
        "in the cloud, performs cloud-based "
        "analysis, and generates personalized "
        "recommendations and emergency alerts."
    )

    return "\n".join(answer).strip()


# ============================================================
# GENERAL QUESTIONS
# ============================================================

def split_into_sentences(text: str):
    """
    Split text into sentences.
    """

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def generate_general_answer(
    query: str,
    context: str
):
    """
    Generate a concise extractive answer for
    general questions.

    The answer is created only from the
    retrieved document context.
    """

    cleaned_context = clean_context(
        context
    )

    if not cleaned_context:

        return (
            "I could not find relevant information "
            "in the uploaded document."
        )

    # ----------------------------------------
    # Remove document metadata
    # ----------------------------------------

    metadata_patterns = [
        r"Department of Computer Science and Engineering",
        r"Model Engineering College, Thrikkakara",
        r"Smart Patient Monitoring and Recommendation "
        r"\(SPMR\) using Cloud Analytics and Deep Learning"
    ]

    for pattern in metadata_patterns:

        cleaned_context = re.sub(
            pattern,
            "",
            cleaned_context,
            flags=re.IGNORECASE
        )

    # ----------------------------------------
    # Remove common section headings
    # ----------------------------------------

    heading_patterns = [
        r"Proposed SPMR Framework",
        r"Introduction",
        r"Conclusion",
        r"Objectives",
        r"System Architecture",
        r"Working of SPMR",
        r"Future Scope",
        r"Advantages and Challenges"
    ]

    for pattern in heading_patterns:

        cleaned_context = re.sub(
            pattern,
            "",
            cleaned_context,
            flags=re.IGNORECASE
        )

    # ----------------------------------------
    # Clean whitespace
    # ----------------------------------------

    cleaned_context = re.sub(
        r"\s+",
        " ",
        cleaned_context
    ).strip()

    # ----------------------------------------
    # Split into sentences
    # ----------------------------------------

    sentences = split_into_sentences(
        cleaned_context
    )

    if not sentences:

        return (
            "I could not find enough information "
            "to answer the question."
        )

    # ----------------------------------------
    # Remove very short fragments
    # ----------------------------------------

    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) >= 30
    ]

    # ----------------------------------------
    # Extract query keywords
    # ----------------------------------------

    query_words = set(
        word.lower()
        for word in re.findall(
            r"\b[a-zA-Z]{3,}\b",
            query
        )
    )

    stop_words = {
        "what",
        "when",
        "where",
        "which",
        "who",
        "whom",
        "whose",
        "why",
        "how",
        "does",
        "do",
        "did",
        "the",
        "and",
        "for",
        "from",
        "with",
        "about",
        "into",
        "that",
        "this",
        "these",
        "those",
        "are",
        "was",
        "were",
        "has",
        "have",
        "been",
        "can",
        "could",
        "would",
        "should",
        "explain",
        "describe",
        "tell",
        "please"
    }

    keywords = query_words - stop_words

    # ----------------------------------------
    # Detect definition questions
    # ----------------------------------------

    is_definition_question = bool(
        re.match(
            r"^\s*what\s+is\s+.+\??\s*$",
            query,
            flags=re.IGNORECASE
        )
    )

    # ----------------------------------------
    # Score sentences
    # ----------------------------------------

    scored = []

    for index, sentence in enumerate(
        sentences
    ):

        sentence_words = set(
            word.lower()
            for word in re.findall(
                r"\b[a-zA-Z]{3,}\b",
                sentence
            )
        )

        overlap = keywords.intersection(
            sentence_words
        )

        score = len(overlap)

        # Prefer explanatory sentences.
        if len(sentence_words) >= 12:

            score += 0.5

        # Special handling for definitions.
        if is_definition_question:

            definition_terms = {
                "framework",
                "system",
                "combines",
                "integrates",
                "provides",
                "enables",
                "designed",
                "developed",
                "refers"
            }

            definition_overlap = (
                definition_terms.intersection(
                    sentence_words
                )
            )

            score += (
                len(definition_overlap) * 1.5
            )

        # Prefer earlier relevant sentences
        # when scores are similar.
        position_bonus = max(
            0,
            3 - index
        ) * 0.1

        score += position_bonus

        if overlap:

            scored.append(
                (
                    score,
                    index,
                    sentence
                )
            )

    # ----------------------------------------
    # Sort by relevance
    # ----------------------------------------

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # ----------------------------------------
    # Select useful sentences
    # ----------------------------------------

    selected = []

    for score, index, sentence in scored:

        if sentence not in selected:

            selected.append(sentence)

        if len(selected) >= 3:

            break

    # ----------------------------------------
    # Fallback
    # ----------------------------------------

    if not selected:

        selected = sentences[:3]

    # ----------------------------------------
    # Return concise answer
    # ----------------------------------------

    return " ".join(
        selected
    ).strip()


# ============================================================
# MAIN ANSWER DISPATCHER
# ============================================================

def generate_answer(
    query: str,
    context: str
):
    """
    Main answer generation function.

    This implementation is completely local
    and does not require an external API.
    """

    if not context or not context.strip():

        return (
            "I could not find relevant information "
            "in the uploaded document."
        )

    # ========================================
    # Architecture questions
    # ========================================

    if is_architecture_question(query):

        return generate_architecture_answer(
            query,
            context
        )

    # ========================================
    # Limitations questions
    # ========================================

    if is_limitations_question(query):

        return generate_limitations_answer(
            query,
            context
        )

    # ========================================
    # Working questions
    # ========================================

    if is_working_question(query):

        return generate_working_answer(
            query,
            context
        )

    # ========================================
    # General questions
    # ========================================

    return generate_general_answer(
        query,
        context
    )

