"""Routes for summaries API endpoints"""

from flask import Blueprint, jsonify, request
from app.database import db
from app.models.summary import Summary
from app.utils.errors import not_found, forbidden

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
    # Query for summary by document_id
    summary = Summary.query.filter_by(document_id=document_id).first()
    
    if not summary:
        return not_found(
            detail=f"Summary for document {document_id} not found",
            instance=f"/api/v1/summaries/document/{document_id}"
        )
    
    # Check authorization: Mock authentication via X-User-ID header
    # In production, this would be replaced with actual authentication
    requesting_user_id = request.headers.get("X-User-ID")
    if requesting_user_id and summary.user_id:
        if int(requesting_user_id) != summary.user_id:
            return forbidden(
                detail="Access denied: You are not authorized to view this document summary",
                instance=f"/api/v1/summaries/document/{document_id}"
            )
    
    return jsonify(summary.to_dict()), 200
