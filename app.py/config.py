import os

from dotenv import load_dotenv


load_dotenv()


TOKEN_HARBOR_API_KEY = os.getenv(
    "TOKEN_HARBOR_API_KEY",
)

TOKEN_HARBOR_BASE_URL = os.getenv(
    "TOKEN_HARBOR_BASE_URL",
    "https://tokenharbor.ai/v1",
)

TOKEN_HARBOR_MODEL = os.getenv(
    "TOKEN_HARBOR_MODEL",
    "deepseek-v4.1-flash:free",
)


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
)

GROQ_BASE_URL = os.getenv(
    "GROQ_BASE_URL",
    "https://api.groq.com/openai/v1",
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)


def require_environment_value(
    value,
    name,
):
    if value is None or not str(value).strip():
        raise RuntimeError(
            f"{name} is not configured.",
        )

    return value