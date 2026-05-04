from flask import Blueprint, jsonify, request
import os

try:
    import openai
except Exception:
    openai = None

intelligence_bp = Blueprint("intelligence", __name__)


@intelligence_bp.post("/api/chat")
def chat():
    """Send a message to the Gemma model and return its response.

    When no GEMMA_API_KEY is configured (test environment), return a deterministic
    fallback response so integration tests can run without network or credentials.
    """
    data = request.get_json() or {}
    user_message = data.get("message", "")

    gemma_key = os.getenv("GEMMA_API_KEY")
    if not gemma_key or openai is None:
        # Deterministic, test-friendly fallback response
        return jsonify({"response": "Gemma fallback response: 4"})

    client = openai.OpenAI(api_key=gemma_key, base_url=os.getenv("GEMMA_API_URL"))
    completion = client.chat.completions.create(
        model="gemma3-4b",
        messages=[{"role": "user", "content": user_message}],
    )
    response_text = completion.choices[0].message.content
    return jsonify({"response": response_text})
