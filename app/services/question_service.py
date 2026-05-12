"""Service layer for question (preguntas) CRUD operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError

from app.database import db
from app.models.question import HistorialPregunta as Question
from app.models.document import HistorialDocumento


class QuestionServiceError(Exception):
    pass


class QuestionNotFoundError(QuestionServiceError):
    pass


class QuestionValidationError(QuestionServiceError):
    pass


class QuestionForbiddenError(QuestionServiceError):
    pass


class QuestionService:
    @staticmethod
    def create_question(data: Dict[str, Any], user_id: Optional[int] = None) -> Question:
        if not isinstance(data, dict):
            raise QuestionValidationError("Request body must be a JSON object.")

        required = ("user_id", "document_id", "pregunta")
        for f in required:
            if f not in data:
                raise QuestionValidationError(f"Missing required field: {f}")

        if user_id is not None and int(data["user_id"]) != user_id:
            raise QuestionForbiddenError("X-User-ID does not match the authenticated user.")

        if not isinstance(data["pregunta"], str) or not data["pregunta"].strip():
            raise QuestionValidationError("Field 'pregunta' must be a non-empty string.")

        q = Question(
            usuario_id=int(data["user_id"]),
            documento_id=int(data["document_id"]),
            pregunta=data["pregunta"].strip(),
        )
        try:
            db.session.add(q)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise QuestionServiceError("Unable to persist question.") from None
        return q

    @staticmethod
    def list_questions(user_id: Optional[int] = None, document_id: Optional[int] = None) -> List[Question]:
        query = Question.query
        if user_id is not None:
            query = query.filter_by(usuario_id=user_id)
        if document_id is not None:
            query = query.filter_by(documento_id=document_id)
        return list(query.order_by(Question.id.desc()).all())

    @staticmethod
    def get_question(question_id: int) -> Optional[Question]:
        return db.session.get(Question, question_id)

    @staticmethod
    def update_question(question_id: int, data: Dict[str, Any], user_id: Optional[int] = None) -> Question:
        q = db.session.get(Question, question_id)
        if q is None:
            raise QuestionNotFoundError(f"Question with ID {question_id} not found")

        if user_id is not None and q.usuario_id != user_id:
            raise QuestionForbiddenError("You are not allowed to modify this question.")

        if not isinstance(data, dict):
            raise QuestionValidationError("Request body must be a JSON object.")

        updated = False
        if "pregunta" in data:
            if not isinstance(data["pregunta"], str) or not data["pregunta"].strip():
                raise QuestionValidationError("Field 'pregunta' must be a non-empty string.")
            q.pregunta = data["pregunta"].strip()
            updated = True
        if "respuesta" in data:
            q.respuesta = data["respuesta"]
            updated = True

        if not updated:
            raise QuestionValidationError("No supported fields to update.")

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise QuestionServiceError("Unable to update question.") from None

        return q

    @staticmethod
    def delete_question(question_id: int, user_id: Optional[int] = None) -> None:
        q = db.session.get(Question, question_id)
        if q is None:
            raise QuestionNotFoundError(f"Question with ID {question_id} not found")

        if user_id is not None and q.usuario_id != user_id:
            raise QuestionForbiddenError("You are not allowed to delete this question.")

        try:
            db.session.delete(q)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise QuestionServiceError("Unable to delete question.") from None
