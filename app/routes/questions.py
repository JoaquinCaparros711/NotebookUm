"""Blueprint routes for preguntas (questions) API."""

from flask import Blueprint, request, jsonify

from app.services.question_service import (
    QuestionService,
    QuestionValidationError,
    QuestionNotFoundError,
    QuestionForbiddenError,
    QuestionServiceError,
)
from app.services.validation import create_rfc9457_error
from app.utils.errors import bad_request, forbidden, not_found, internal_server_error
from app.utils.auth import parse_x_user_id


questions_bp = Blueprint("questions", __name__)


@questions_bp.route("/api/v1/preguntas", methods=["POST"])
def create_question():
    instance = "/api/v1/preguntas"
    raw_user_id = request.headers.get("X-User-ID")
    if raw_user_id is None:
        return bad_request(detail="X-User-ID header is required.", instance=instance)

    try:
        user_id = parse_x_user_id(raw_user_id)
    except ValueError:
        return bad_request(detail="Invalid X-User-ID header value.", instance=instance)

    data = request.get_json(silent=True)
    if isinstance(data, dict):
        if "user_id" in data and int(data["user_id"]) != user_id:
            return forbidden(
                detail="X-User-ID does not match the authenticated user.",
                instance=instance,
            )
        data["user_id"] = user_id

    try:
        q = QuestionService.create_question(data, user_id=user_id)
    except QuestionValidationError as exc:
        return create_rfc9457_error(detail=str(exc), instance=instance)
    except QuestionForbiddenError as exc:
        return forbidden(detail=str(exc), instance=instance)
    except QuestionServiceError:
        return internal_server_error(detail="Unable to create question.", instance=instance)

    return jsonify(q.to_dict()), 201


@questions_bp.route("/api/v1/preguntas", methods=["GET"])
def list_questions():
    raw_user_id = request.headers.get("X-User-ID")
    if raw_user_id is None:
        return bad_request(detail="X-User-ID header is required.", instance="/api/v1/preguntas")

    try:
        user_id = parse_x_user_id(raw_user_id)
    except ValueError:
        return bad_request(detail="Invalid X-User-ID header value.", instance="/api/v1/preguntas")

    doc_id_arg = request.args.get("document_id")
    try:
        document_id = int(doc_id_arg) if doc_id_arg is not None else None
    except ValueError:
        return bad_request(detail="Invalid document_id query param.", instance="/api/v1/preguntas")

    questions = QuestionService.list_questions(user_id=user_id, document_id=document_id)
    return jsonify([q.to_dict() for q in questions]), 200


@questions_bp.route("/api/v1/pregunta/<int:question_id>", methods=["GET"])
def get_question_detail(question_id: int):
    instance = f"/api/v1/pregunta/{question_id}"
    raw_user_id = request.headers.get("X-User-ID")
    if raw_user_id is None:
        return bad_request(detail="X-User-ID header is required.", instance=instance)

    try:
        user_id = parse_x_user_id(raw_user_id)
    except ValueError:
        return bad_request(detail="Invalid X-User-ID header value.", instance=instance)

    q = QuestionService.get_question(question_id)
    if q is None:
        return not_found(detail=f"Question with ID {question_id} not found", instance=instance)

    if q.usuario_id != user_id:
        return forbidden(
            detail="You are not authorized to view this question.",
            instance=instance,
        )

    return jsonify(q.to_dict()), 200


@questions_bp.route("/api/v1/pregunta/<int:question_id>", methods=["PATCH"])
def patch_question(question_id: int):
    instance = f"/api/v1/pregunta/{question_id}"
    raw_user_id = request.headers.get("X-User-ID")
    if raw_user_id is None:
        return bad_request(detail="X-User-ID header is required.", instance=instance)

    try:
        user_id = parse_x_user_id(raw_user_id)
    except ValueError:
        return bad_request(detail="Invalid X-User-ID header value.", instance=instance)

    data = request.get_json(silent=True)
    try:
        q = QuestionService.update_question(question_id, data, user_id=user_id)
    except QuestionNotFoundError as exc:
        return not_found(detail=str(exc), instance=instance)
    except QuestionForbiddenError as exc:
        return forbidden(detail=str(exc), instance=instance)
    except QuestionValidationError as exc:
        return create_rfc9457_error(detail=str(exc), instance=instance)
    except QuestionServiceError:
        return internal_server_error(detail="Unable to update question.", instance=instance)

    return jsonify(q.to_dict()), 200


@questions_bp.route("/api/v1/pregunta/<int:question_id>", methods=["DELETE"])
def delete_question(question_id: int):
    instance = f"/api/v1/pregunta/{question_id}"
    raw_user_id = request.headers.get("X-User-ID")
    if raw_user_id is None:
        return bad_request(detail="X-User-ID header is required.", instance=instance)

    try:
        user_id = parse_x_user_id(raw_user_id)
    except ValueError:
        return bad_request(detail="Invalid X-User-ID header value.", instance=instance)

    try:
        QuestionService.delete_question(question_id, user_id=user_id)
    except QuestionNotFoundError as exc:
        return not_found(detail=str(exc), instance=instance)
    except QuestionForbiddenError as exc:
        return forbidden(detail=str(exc), instance=instance)
    except QuestionServiceError:
        return internal_server_error(detail="Unable to delete question.", instance=instance)

    return "", 204
