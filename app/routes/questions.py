"""Blueprint routes for preguntas (questions) API."""

from flask import Blueprint, request, jsonify

from app.services.question_service import (
    QuestionService,
    QuestionValidationError,
    QuestionNotFoundError,
    QuestionServiceError,
)
from app.services.validation import create_rfc9457_error
from app.utils.errors import bad_request, not_found, internal_server_error
from app.utils.auth import parse_x_user_id


questions_bp = Blueprint("questions", __name__)


@questions_bp.route("/api/v1/preguntas", methods=["POST"])
def create_question():
    instance = "/api/v1/preguntas"
    data = request.get_json(silent=True)
    try:
        q = QuestionService.create_question(data)
    except QuestionValidationError as exc:
        return create_rfc9457_error(detail=str(exc), instance=instance)
    except QuestionServiceError:
        return internal_server_error(detail="Unable to create question.", instance=instance)

    return jsonify(q.to_dict()), 201


@questions_bp.route("/api/v1/preguntas", methods=["GET"])
def list_questions():
    raw_user_id = request.headers.get("X-User-ID")
    try:
        user_id = parse_x_user_id(raw_user_id)
    except ValueError:
        return bad_request(detail="Invalid X-User-ID header value.", instance="/api/v1/preguntas")

    doc_id_arg = request.args.get("document_id")
    try:
        document_id = int(doc_id_arg) if doc_id_arg is not None else None
    except ValueError:
        return bad_request(detail="Invalid document_id query param.", instance="/api/v1/preguntas")

    # If user_id provided, scope to that user; otherwise list all (but tests use X-User-ID)
    questions = QuestionService.list_questions(user_id=user_id, document_id=document_id)
    return jsonify([q.to_dict() for q in questions]), 200


@questions_bp.route("/api/v1/pregunta/<int:question_id>", methods=["GET"])
def get_question_detail(question_id: int):
    instance = f"/api/v1/pregunta/{question_id}"
    q = QuestionService.get_question(question_id)
    if q is None:
        return not_found(detail=f"Question with ID {question_id} not found", instance=instance)
    return jsonify(q.to_dict()), 200


@questions_bp.route("/api/v1/pregunta/<int:question_id>", methods=["PATCH"])
def patch_question(question_id: int):
    instance = f"/api/v1/pregunta/{question_id}"
    data = request.get_json(silent=True)
    try:
        q = QuestionService.update_question(question_id, data)
    except QuestionNotFoundError as exc:
        return not_found(detail=str(exc), instance=instance)
    except QuestionValidationError as exc:
        return create_rfc9457_error(detail=str(exc), instance=instance)
    except QuestionServiceError:
        return internal_server_error(detail="Unable to update question.", instance=instance)

    return jsonify(q.to_dict()), 200


@questions_bp.route("/api/v1/pregunta/<int:question_id>", methods=["DELETE"])
def delete_question(question_id: int):
    instance = f"/api/v1/pregunta/{question_id}"
    try:
        QuestionService.delete_question(question_id)
    except QuestionNotFoundError as exc:
        return not_found(detail=str(exc), instance=instance)
    except QuestionServiceError:
        return internal_server_error(detail="Unable to delete question.", instance=instance)

    return "", 204
