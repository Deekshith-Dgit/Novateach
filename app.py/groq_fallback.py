import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found in the environment."
    )


groq_client = Groq(
    api_key=GROQ_API_KEY
)


GROQ_MODEL = "openai/gpt-oss-120b"


def generate_with_groq(
    prompt,
    expect_json=False
):
    """
    Generate a response using Groq.

    If expect_json=True, ask Groq to return
    syntactically valid JSON.
    """

    request = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    if expect_json:
        request["response_format"] = {
            "type": "json_object"
        }

    response = groq_client.chat.completions.create(
        **request
    )

    if not response.choices:
        raise ValueError(
            "Groq returned no choices."
        )

    message = response.choices[0].message

    if message is None:
        raise ValueError(
            "Groq returned an empty message."
        )

    content = message.content

    if not content:
        raise ValueError(
            "Groq returned an empty response."
        )

    return content