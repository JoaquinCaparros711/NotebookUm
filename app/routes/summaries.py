"""Routes for summaries API endpoints"""

from flask import Blueprint, jsonify, request

from app.services.summary_service import SummaryService
from app.utils.errors import forbidden, not_found

summaries_bp = Blueprint("summaries", __name__, url_prefix="/api/v1/summaries")


@summaries_bp.route("/document/<int:document_id>", methods=["GET"])
def get_document_summary(document_id: int):
    """
    Get summary for a specific document.

    Args:
        document_id: ID of the document to retrieve summary for

    Returns:
        JSON response with summary data or error
    """
    service = SummaryService()
    summary = service.get_summary_by_document_id(document_id)

    if not summary:
        return not_found(
            detail=f"Summary for document {document_id} not found",
            instance=f"/api/v1/summaries/document/{document_id}",
        )

    requesting_user_id = request.headers.get("X-User-ID")
    if requesting_user_id:
        try:
            user_id = int(requesting_user_id)
            if not service.check_user_ownership(summary, user_id):
                return forbidden(
                    detail="Access denied: You are not authorized to view this document summary",
                    instance=f"/api/v1/summaries/document/{document_id}",
                )
        except ValueError:
            return forbidden(
                detail="Invalid user ID",
                instance=f"/api/v1/summaries/document/{document_id}",
            )

    return jsonify(summary.to_dict()), 200
