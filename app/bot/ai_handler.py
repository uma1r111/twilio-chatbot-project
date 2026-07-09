"""
Phase 4 - AI Chatbot Fallback

Called when no rule-based command matches. Forwards the user's message
to Azure OpenAI and returns the generated reply. Handles errors and
empty responses gracefully so the webhook never crashes or hangs.
"""

from openai import AzureOpenAI, APIError, APIConnectionError, APITimeoutError

from app import config

_client = None


def _get_client() -> AzureOpenAI:
    """
    Lazily creates and caches the Azure OpenAI client so we don't
    reconnect on every message.
    """
    global _client
    if _client is None:
        _client = AzureOpenAI(
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.API_VERSION,
            azure_endpoint=config.ENDPOINT_URL,
        )
    return _client


def get_ai_response(message: str, history: list[dict] | None = None) -> str:
    """
    Sends the user's message to Azure OpenAI and returns the reply text.
    Falls back to a friendly error message if the call fails or the
    response is empty, so the bot always replies with something.

    `history` is an optional list of prior turns for this phone number,
    each formatted as {"incoming_message": ..., "bot_response": ...},
    oldest first. Used to give the model conversation context.
    """
    if not config.AZURE_OPENAI_API_KEY or not config.ENDPOINT_URL:
        print("[AI Handler] Missing Azure OpenAI credentials in .env")
        return "Sorry, the AI assistant isn't configured right now. Type 'Help' for available commands."

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful, concise chatbot replying over "
                "SMS/WhatsApp. Keep replies short (under 3 sentences) "
                "since this is a text messaging channel."
            ),
        }
    ]

    if history:
        for turn in history:
            messages.append({"role": "user", "content": turn["incoming_message"]})
            messages.append({"role": "assistant", "content": turn["bot_response"]})

    messages.append({"role": "user", "content": message})

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=config.DEPLOYMENT_NAME,
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )

        reply = response.choices[0].message.content

        if not reply or not reply.strip():
            print("[AI Handler] Received empty response from model")
            return "Sorry, I couldn't come up with a response. Could you rephrase that?"

        return reply.strip()

    except (APIConnectionError, APITimeoutError) as e:
        print(f"[AI Handler] Connection/timeout error: {e}")
        return "Sorry, I'm having trouble connecting right now. Please try again shortly."

    except APIError as e:
        print(f"[AI Handler] API error: {e}")
        return "Sorry, something went wrong on my end. Please try again."

    except Exception as e:
        print(f"[AI Handler] Unexpected error: {e}")
        return "Sorry, something unexpected happened. Type 'Help' for available commands."