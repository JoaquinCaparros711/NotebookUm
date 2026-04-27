"""Blueprint for summary retrieval endpoints."""

import logging

from flask import Blueprint, Response, jsonify, request

from app.services.summary_service import SummaryService
from app.utils.errors import bad_request, forbidden, internal_server_error, not_found

logger = logging.getLogger(__name__)

summaries_bp = Blueprint("summaries", __name__, url_prefix="/api/v1/summaries")

_INSTANCE_PREFIX = "/api/v1/summaries/document"


@summaries_bp.route("/document/<int:document_id>", methods=["GET"])
def get_document_summary(document_id: int) -> Response:
    """Retrieve the summary for a specific document.

    Authorization is applied when the optional ``X-User-ID`` request header
    is present.  Ownership is resolved against the parent document record
    (``HistorialDocumento.usuario_id``) as required by RF-018.

    The response is state-aware: when the summary status is not ``"completed"``
    a ``"message"`` key is included in the JSON body explaining the current
    processing state (spec HU-3, escenario 3).

    All errors — including unexpected service failures — are returned as
    ``application/problem+json`` following RFC 9457 with the endpoint URI
    in the ``"instance"`` field.

    Args:
        document_id: Primary key of the document whose summary is requested.

    Returns:
        200 – Summary payload as ``application/json``.
              Includes ``"message"`` for non-completed states.
        400 – ``X-User-ID`` header is present but not a valid integer
              (``application/problem+json``, RFC 9457).
        403 – Authenticated user does not own the parent document
              (``application/problem+json``, RFC 9457).
        404 – No summary exists for the given document
              (``application/problem+json``, RFC 9457).
        500 – Unexpected service or database failure
              (``application/problem+json``, RFC 9457).
    """
    instance = f"{_INSTANCE_PREFIX}/{document_id}"
    service = SummaryService()

    # ── 1. Retrieve summary record ─────────────────────────────────────────
    try:
        summary = service.get_summary_by_document_id(document_id)
    except Exception:
        logger.exception(
            "Unhandled error retrieving summary for document %s", document_id
        )
        return internal_server_error(
            detail=(
                "An unexpected error occurred while retrieving the summary. "
                "Please try again later."
            ),
            instance=instance,
        )

    if not summary:
        return not_found(
            detail=f"Summary for document {document_id} not found",
            instance=instance,
        )

    # ── 2. Optional authorization ──────────────────────────────────────────
    raw_user_id = request.headers.get("X-User-ID")
    if raw_user_id is not None:
        try:
            user_id = int(raw_user_id)
        except ValueError:
            return bad_request(
                detail="X-User-ID header must be a valid integer",
                instance=instance,
            )

        try:
            authorized = service.check_document_ownership(
                document_id=document_id, user_id=user_id
            )
        except Exception:
            logger.exception(
                "Unhandled error during ownership check for document %s / user %s",
                document_id,
                user_id,
            )
            return internal_server_error(
                detail=(
                    "An unexpected error occurred while verifying access permissions. "
                    "Please try again later."
                ),
                instance=instance,
            )

        if not authorized:
            return forbidden(
                detail=(
                    "Access denied: You are not authorized to view "
                    "this document summary"
                ),
                instance=instance,
            )

    # ── 3. Build state-aware payload ───────────────────────────────────────
    payload = summary.to_dict()

    message = service.get_status_message(summary)
    if message is not None:
        payload["message"] = message

    return jsonify(payload), 200
