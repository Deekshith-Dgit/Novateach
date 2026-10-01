from typing import Any, Optional


ALLOWED_ERROR_CATEGORIES = {
    "conceptual",
    "procedural",
    "variable_mismatch",
    "formula",
    "prerequisite_gap",
    "application",
}


def _normalize(value: Any) -> str:
    """
    Converts an answer into a normalized string
    for simple comparison.
    """
    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def _normalize_error_type(error_type: Any) -> str:
    """
    Converts an error type into our standard format.
    """
    if error_type is None:
        return ""

    value = str(error_type).strip().lower()

    aliases = {
        "concept": "conceptual",
        "conceptual_error": "conceptual",
        "procedural_error": "procedural",
        "variable": "variable_mismatch",
        "variable mismatch": "variable_mismatch",
        "variable_mismatch_error": "variable_mismatch",
        "formula_error": "formula",
        "prerequisite": "prerequisite_gap",
        "prerequisite_error": "prerequisite_gap",
        "application_error": "application",
    }

    return aliases.get(value, value)


def _extract_possible_error_types(
    possible_error_types: Any,
) -> list[str]:
    """
    Converts possible_error_types into a clean list.
    """

    if possible_error_types is None:
        return []

    if isinstance(possible_error_types, list):
        raw_types = possible_error_types

    elif isinstance(possible_error_types, str):
        raw_types = [
            item.strip()
            for item in possible_error_types.split(",")
            if item.strip()
        ]

    else:
        return []

    result = []

    for item in raw_types:
        normalized = _normalize_error_type(item)

        if normalized in ALLOWED_ERROR_CATEGORIES:
            result.append(normalized)

    return list(dict.fromkeys(result))


def diagnose_error(
    student_answer: Any,
    expected_answer: Any,
    question: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Diagnoses a learner's error using deterministic evidence.

    Returns a dictionary containing:
        category
        pattern_key
        description
        confidence
        method
    """

    student = _normalize(student_answer)
    expected = _normalize(expected_answer)

    question = question or {}

    possible_errors = _extract_possible_error_types(
        question.get("possible_error_types")
    )

    # ---------------------------------------------------------
    # 1. Empty answer
    # ---------------------------------------------------------

    if not student:
        return {
            "category": "procedural",
            "pattern_key": "no_answer",
            "description": "Learner did not provide an answer.",
            "confidence": 0.98,
            "method": "deterministic",
        }

    # ---------------------------------------------------------
    # 2. Exact answer
    # ---------------------------------------------------------

    if student == expected:
        return {
            "category": None,
            "pattern_key": None,
            "description": None,
            "confidence": 1.0,
            "method": "deterministic",
        }

    # ---------------------------------------------------------
    # 3. MCQ / true-false style mismatch
    # ---------------------------------------------------------

    question_type = str(
        question.get("question_type", "")
    ).strip().lower()

    if question_type in {"mcq", "true_false"}:

        if "conceptual" in possible_errors:
            return {
                "category": "conceptual",
                "pattern_key": "incorrect_conceptual_choice",
                "description": (
                    "The learner selected an incorrect conceptual option."
                ),
                "confidence": 0.75,
                "method": "deterministic",
            }

        return {
            "category": (
                possible_errors[0]
                if possible_errors
                else "conceptual"
            ),
            "pattern_key": "incorrect_choice",
            "description": (
                "The learner selected an answer different "
                "from the expected answer."
            ),
            "confidence": 0.65,
            "method": "deterministic",
        }

    # ---------------------------------------------------------
    # 4. Numerical / formula questions
    # ---------------------------------------------------------

    if question_type == "numerical":

        if "variable_mismatch" in possible_errors:
            return {
                "category": "variable_mismatch",
                "pattern_key": "numerical_variable_mismatch",
                "description": (
                    "The numerical answer may indicate "
                    "a mismatch in the variables used."
                ),
                "confidence": 0.60,
                "method": "deterministic",
            }

        if "formula" in possible_errors:
            return {
                "category": "formula",
                "pattern_key": "incorrect_formula_application",
                "description": (
                    "The numerical answer differs from the expected "
                    "result and the question allows formula-related diagnosis."
                ),
                "confidence": 0.60,
                "method": "deterministic",
            }

    # ---------------------------------------------------------
    # 5. Application questions
    # ---------------------------------------------------------

    if question_type in {"application", "reasoning"}:

        if "application" in possible_errors:
            return {
                "category": "application",
                "pattern_key": "application_error",
                "description": (
                    "The learner's answer suggests difficulty "
                    "applying the concept to the given situation."
                ),
                "confidence": 0.60,
                "method": "deterministic",
            }

        if "prerequisite_gap" in possible_errors:
            return {
                "category": "prerequisite_gap",
                "pattern_key": "possible_prerequisite_gap",
                "description": (
                    "The response may indicate a missing prerequisite concept."
                ),
                "confidence": 0.55,
                "method": "deterministic",
            }

    # ---------------------------------------------------------
    # 6. Use question metadata when available
    # ---------------------------------------------------------

    if possible_errors:

        category = possible_errors[0]

        pattern_keys = {
            "conceptual": "conceptual_misconception",
            "procedural": "procedural_error",
            "variable_mismatch": "variable_mismatch",
            "formula": "formula_error",
            "prerequisite_gap": "prerequisite_gap",
            "application": "application_error",
        }

        descriptions = {
            "conceptual": (
                "The response is incorrect and may indicate "
                "a misunderstanding of the underlying concept."
            ),
            "procedural": (
                "The response is incorrect and may indicate "
                "an error in the solution procedure."
            ),
            "variable_mismatch": (
                "The response may indicate confusion between "
                "the variables or quantities involved."
            ),
            "formula": (
                "The response may indicate incorrect "
                "formula selection or application."
            ),
            "prerequisite_gap": (
                "The response may indicate difficulty with "
                "a prerequisite concept."
            ),
            "application": (
                "The response may indicate difficulty "
                "applying the concept to the problem."
            ),
        }

        return {
            "category": category,
            "pattern_key": pattern_keys[category],
            "description": descriptions[category],
            "confidence": 0.50,
            "method": "deterministic",
        }

    # ---------------------------------------------------------
    # 7. Unknown / insufficient evidence
    # ---------------------------------------------------------

    return {
        "category": None,
        "pattern_key": None,
        "description": (
            "The answer is incorrect, but there is insufficient "
            "evidence to determine the specific error type."
        ),
        "confidence": 0.20,
        "method": "deterministic",
    }