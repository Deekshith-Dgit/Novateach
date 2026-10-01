import json
import re
from collections.abc import Callable
from typing import Any

from openai import OpenAI

from config import (
    GROQ_API_KEY,
    GROQ_BASE_URL,
    GROQ_MODEL,
    TOKEN_HARBOR_API_KEY,
    TOKEN_HARBOR_BASE_URL,
    TOKEN_HARBOR_MODEL,
    require_environment_value,
)


def clean_json_response(raw_output):
    if not raw_output:
        raise ValueError(
            "AI returned an empty response.",
        )

    if not isinstance(raw_output, str):
        raw_output = str(raw_output)

    raw_output = raw_output.strip()

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

    if (
        first_object != -1
        and last_object > first_object
    ):
        return raw_output[
            first_object:last_object + 1
        ].strip()

    first_array = raw_output.find("[")
    last_array = raw_output.rfind("]")

    if (
        first_array != -1
        and last_array > first_array
    ):
        return raw_output[
            first_array:last_array + 1
        ].strip()

    return raw_output


def parse_json_response(raw_output):
    if isinstance(raw_output, (dict, list)):
        return raw_output

    cleaned_output = clean_json_response(
        raw_output,
    )

    try:
        return json.loads(cleaned_output)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"AI returned invalid JSON: {error}",
        ) from error


def _create_client(provider):
    if provider == "token_harbor":
        api_key = require_environment_value(
            TOKEN_HARBOR_API_KEY,
            "TOKEN_HARBOR_API_KEY",
        )

        return OpenAI(
            api_key=api_key,
            base_url=TOKEN_HARBOR_BASE_URL,
        )

    if provider == "groq":
        api_key = require_environment_value(
            GROQ_API_KEY,
            "GROQ_API_KEY",
        )

        return OpenAI(
            api_key=api_key,
            base_url=GROQ_BASE_URL,
        )

    raise ValueError(
        f"Unknown provider: {provider}",
    )


def _get_model(provider):
    if provider == "token_harbor":
        return TOKEN_HARBOR_MODEL

    if provider == "groq":
        return GROQ_MODEL

    raise ValueError(
        f"Unknown provider: {provider}",
    )


def _extract_response_text(response):
    if not response.choices:
        raise ValueError(
            "Provider returned no choices.",
        )

    message = response.choices[0].message

    content = getattr(
        message,
        "content",
        None,
    )

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, dict):
                text = item.get("text")

                if text:
                    text_parts.append(str(text))

            else:
                text = getattr(item, "text", None)

                if text:
                    text_parts.append(str(text))

        content = "".join(text_parts)

    if content and str(content).strip():
        return str(content).strip()

    refusal = getattr(
        message,
        "refusal",
        None,
    )

    if refusal and str(refusal).strip():
        raise ValueError(
            f"Provider refused the request: {refusal}",
        )

    raise ValueError(
        "Provider returned empty content.",
    )


def _generate_from_provider(
    provider,
    prompt,
    temperature,
    expect_json,
    result_validator: Callable[[Any], None] | None = None,
):
    client = _create_client(provider)
    model = _get_model(provider)

    request = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": temperature,
        "max_tokens": 4096,
    }

    if expect_json:
        request["response_format"] = {
            "type": "json_object",
        }

    response = client.chat.completions.create(
        **request,
    )

    text = _extract_response_text(response)

    if expect_json:
        result = parse_json_response(text)
        if result_validator is not None:
            result_validator(result)
        return result

    return text


def generate_with_ai(
    prompt,
    temperature=0.2,
    expect_json=False,
    task_type=None,
    result_validator: Callable[[Any], None] | None = None,
):
    del task_type

    primary_provider = "token_harbor"
    primary_label = (
        "Token Harbor DeepSeek V4.1 Flash"
    )

    try:
        print(
            f"\nTrying {primary_label}..."
        )

        result = _generate_from_provider(
            provider=primary_provider,
            prompt=prompt,
            temperature=temperature,
            expect_json=expect_json,
            result_validator=result_validator,
        )

        print(
            f"{primary_label} response received."
        )

        return result

    except Exception as primary_error:
        print(
            f"\n{primary_label} failed:"
        )
        print(primary_error)
        print(
            "\nSwitching to "
            "Groq GPT-OSS 120B..."
        )

    try:
        result = _generate_from_provider(
            provider="groq",
            prompt=prompt,
            temperature=temperature,
            expect_json=expect_json,
            result_validator=result_validator,
        )

        print(
            "Groq GPT-OSS 120B "
            "fallback response received."
        )

        return result

    except Exception as groq_error:
        print(
            "\nGroq fallback also failed:"
        )
        print(groq_error)

        raise RuntimeError(
            "Token Harbor and Groq both failed.",
        ) from groq_error