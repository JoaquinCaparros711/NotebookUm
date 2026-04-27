"""Blueprint for summary retrieval endpoints."""

from flask import Blueprint, Response, jsonify, request

from app.services.summary_service import SummaryService
from app.utils.errors import bad_request, forbidden, not_found

summaries_bp = Blueprint("summaries", __name__, url_prefix="/api/v1/summaries")

_INSTANCE_PREFIX = "/api/v1/summaries/document"


@summaries_bp.route("/document/<int:document_id>", methods=["GET"])
def get_document_summary(document_id: int) -> Response:
    """Retrieve the summary for a specific document.

    Checks ownership when the optional ``X-User-ID`` request header is present.

    Args:
        document_id: Primary key of the document whose summary is requested.

    Returns:
        200 – Summary payload as ``application/json``.
        400 – ``X-User-ID`` header is present but not a valid integer
              (``application/problem+json``, RFC 9457).
        403 – Authenticated user does not own the requested summary
              (``application/problem+json``, RFC 9457).
        404 – No summary exists for the given document
              (``application/problem+json``, RFC 9457).
    """
    instance = f"{_INSTANCE_PREFIX}/{document_id}"
    service = SummaryService()

    summary = service.get_summary_by_document_id(document_id)
    if not summary:
        return not_found(
            detail=f"Summary for document {document_id} not found",
            instance=instance,
        )

    raw_user_id = request.headers.get("X-User-ID")
    if raw_user_id is not None:
        try:
            user_id = int(raw_user_id)
        except ValueError:
            return bad_request(
                detail="X-User-ID header must be a valid integer",
                instance=instance,
            )

        if not service.check_user_ownership(summary, user_id):
            return forbidden(
                detail="Access denied: You are not authorized to view this document summary",
                instance=instance,
            )

    return jsonify(summary.to_dict()), 200
