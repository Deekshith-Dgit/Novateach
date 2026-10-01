import json
import re
from typing import Any

from ai_generator import (
    generate_with_ai as generate_with_provider_ai,
)


def clean_json_response(raw_output: Any) -> str:
    """
    Clean common AI formatting issues before JSON parsing.
    """

    if raw_output is None:
        raise ValueError(
            "AI returned an empty response.",
        )

    if isinstance(raw_output, (dict, list)):
        return json.dumps(
            raw_output,
            ensure_ascii=False,
        )

    raw_output = str(raw_output).strip()

    if not raw_output:
        raise ValueError(
            "AI returned an empty response.",
        )

    raw_output = re.sub(
        r"^```(?:json)?\s*",
        "",
        raw_output,
        flags=re.IGNORECASE,
    )

    raw_output = re.sub(
        r"\s*```$",
        "",
        raw_output,
    )

    raw_output = raw_output.strip()

    first_object = raw_output.find("{")
    last_object = raw_output.rfind("}")

    first_array = raw_output.find("[")
    last_array = raw_output.rfind("]")

    object_is_valid = (
        first_object != -1
        and last_object > first_object
    )

    array_is_valid = (
        first_array != -1
        and last_array > first_array
    )

    if object_is_valid and array_is_valid:
        if first_object < first_array:
            return raw_output[
                first_object:last_object + 1
            ].strip()

        return raw_output[
            first_array:last_array + 1
        ].strip()

    if object_is_valid:
        return raw_output[
            first_object:last_object + 1
        ].strip()

    if array_is_valid:
        return raw_output[
            first_array:last_array + 1
        ].strip()

    return raw_output


def parse_json_response(
    raw_output: Any,
) -> dict[str, Any] | list[Any]:
    """
    Parse an AI response into a JSON object or array.
    """

    if isinstance(raw_output, (dict, list)):
        return raw_output

    cleaned_output = clean_json_response(
        raw_output,
    )

    try:
        return json.loads(cleaned_output)

    except json.JSONDecodeError as error:
        print("\n⚠️ JSON parsing failed.")
        print(f"JSON error: {error}")
        print("\nRaw AI output:")
        print(cleaned_output[:3000])

        raise ValueError(
            "AI returned invalid JSON.",
        ) from error


def build_json_correction_prompt(
    original_prompt: str,
    invalid_output: str,
) -> str:
    """
    Build a repair prompt for malformed JSON.
    """

    return f"""
You are repairing a previous AI response.

ORIGINAL TASK:
{original_prompt}

PREVIOUS RESPONSE:
{invalid_output}

Return the same information as valid JSON.

Rules:
1. Return only JSON.
2. Do not use Markdown.
3. Do not use code fences.
4. Do not add explanations.
5. Do not remove important fields.
6. Preserve the original meaning.
7. Use double quotes for JSON strings.
8. Use valid JSON arrays and objects.
9. Escape special characters correctly.
10. The result must be parseable by json.loads().

Return only the corrected JSON.
""".strip()


def _generate_raw(
    prompt: str,
    temperature: float = 0.2,
) -> str:
    """
    Generate plain text through the shared provider system.

    Primary:
        Token Harbor DeepSeek V4.1 Flash

    Fallback:
        Groq GPT-OSS 120B
    """

    response = generate_with_provider_ai(
        prompt=prompt,
        temperature=temperature,
        expect_json=False,
    )

    if response is None:
        raise ValueError(
            "AI returned no response.",
        )

    if isinstance(response, (dict, list)):
        return json.dumps(
            response,
            ensure_ascii=False,
        )

    response_text = str(response).strip()

    if not response_text:
        raise ValueError(
            "AI returned an empty response.",
        )

    return response_text


def generate_with_ai(
    prompt: str,
    temperature: float = 0.2,
    expect_json: bool = False,
):
    """
    Shared AI entry point for all services.

    When expect_json is False:
        Returns a string.

    When expect_json is True:
        Returns a Python dictionary or list.
    """

    if not isinstance(prompt, str):
        raise TypeError(
            "AI prompt must be a string.",
        )

    if not prompt.strip():
        raise ValueError(
            "AI prompt cannot be empty.",
        )

    if not expect_json:
        return _generate_raw(
            prompt=prompt,
            temperature=temperature,
        )

    first_response = _generate_raw(
        prompt=prompt,
        temperature=temperature,
    )

    try:
        parsed = parse_json_response(
            first_response,
        )

        print(
            "✅ AI returned valid JSON."
        )

        return parsed

    except ValueError as first_error:
        print(
            "\n⚠️ AI returned invalid JSON."
        )
        print(first_error)
        print(
            "\n🔧 Requesting JSON correction..."
        )

        correction_prompt = (
            build_json_correction_prompt(
                original_prompt=prompt,
                invalid_output=first_response,
            )
        )

        corrected_response = _generate_raw(
            prompt=correction_prompt,
            temperature=0.0,
        )

        try:
            parsed = parse_json_response(
                corrected_response,
            )

            print(
                "✅ JSON correction succeeded."
            )

            return parsed

        except ValueError as correction_error:
            raise RuntimeError(
                "AI returned invalid JSON twice.",
            ) from correction_error