from flask import Blueprint, jsonify, request
import os
import openai

intelligence_bp = Blueprint("intelligence", __name__)


@intelligence_bp.post("/api/chat")
def chat():
    """Send a message to the Gemma model and return its response"""
    data = request.get_json() or {}
    user_message = data.get("message", "")

    gemma_api_key = os.getenv("GEMMA_API_KEY")
    gemma_api_url = os.getenv("GEMMA_API_URL")

    if not gemma_api_key or not gemma_api_url:
        fallback = user_message.strip() or "No message provided."
        return jsonify({"response": f"Mock response: {fallback}"})

    client = openai.OpenAI(
        api_key=gemma_api_key,
        base_url=gemma_api_url,
    )

    completion = client.chat.completions.create(
        model="gemma3-4b",
        messages=[{"role": "user", "content": user_message}],
    )

    response_text = completion.choices[0].message.content

    return jsonify({"response": response_text})
