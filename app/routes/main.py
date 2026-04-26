from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from ..database import db

main_bp = Blueprint("main", __name__)


import socket

@main_bp.get("/")
def index():
    hostname = socket.gethostname()
    return jsonify({
        "message": "NotebookUm API is running 🚀",
        "instance": hostname
    })


@main_bp.get("/health")
def health():
    """Health check endpoint for Docker HEALTHCHECK and Traefik discovery."""
    status = {"status": "ok", "services": {}}

    # Check database connectivity
    try:
        db.session.execute(text("SELECT 1"))
        status["services"]["database"] = "ok"
    except Exception as e:
        status["services"]["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check Redis connectivity
    try:
        import redis as redis_lib
        broker_url = current_app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
        r = redis_lib.from_url(broker_url)
        r.ping()
        status["services"]["redis"] = "ok"
    except Exception as e:
        status["services"]["redis"] = f"error: {str(e)}"
        status["status"] = "degraded"

    http_status = 200  # Flask is alive - always 200 for process health
    return jsonify(status), http_status

