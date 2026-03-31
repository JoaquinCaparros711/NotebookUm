from flask import Blueprint, jsonify, request
import os
import openai

intelligence_bp = Blueprint("intelligence", __name__)


@intelligence_bp.post("/api/chat")
def chat():
    """Send a message to the Gemma model and return its response"""
    data = request.get_json()
    user_message = data.get("message", "")
    
    # Configure OpenAI client with custom settings
    client = openai.OpenAI(
        api_key=os.getenv("GEMMA_API_KEY"),
        base_url=os.getenv("GEMMA_API_URL")
    )
    
    # Call the API
    completion = client.chat.completions.create(
        model="gemma3-4b",
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    response_text = completion.choices[0].message.content
    
    return jsonify({"response": response_text})
