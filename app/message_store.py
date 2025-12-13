"""
Idempotent Message Logging for Audit Trail
Logs all user and assistant messages to DynamoDB with full metadata.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from decimal import Decimal
from botocore.exceptions import ClientError
from .aws_session import get_ddb_tables

logger = logging.getLogger(__name__)


def _convert_floats_to_decimal(obj):
    """
    Recursively convert float values to Decimal for DynamoDB compatibility.
    DynamoDB does not support floats, only Decimal types.
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: _convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_floats_to_decimal(item) for item in obj]
    return obj


def log_message(
    user_id: str,
    session_id: str,
    role: str,
    text: str,
    request_id: str,
    retrieval_meta: Optional[List[Dict[str, Any]]] = None,
    model: Optional[str] = None,
    latency_ms: Optional[int] = None,
    tokens: Optional[int] = None
) -> bool:
    """
    Log a message to UserMessages table with full audit metadata.
    Idempotent: uses deterministic timestamp key to prevent duplicate logging on retries.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        role: Message role ('user' or 'assistant')
        text: Message content
        request_id: Unique request identifier for this turn
        retrieval_meta: Optional list of retrieval results with source, chunk_id, score
        model: Optional model name used for generation
        latency_ms: Optional response latency in milliseconds
        tokens: Optional token count for this message
    
    Returns:
        True if message was logged successfully
    """
    _, _, messages_table = get_ddb_tables()
    
    # Create deterministic timestamp key: ISO timestamp + request_id + role
    # This ensures idempotency - same request_id and role won't create duplicates
    timestamp = datetime.now(timezone.utc).isoformat()
    sort_key = f"{timestamp}#{request_id}#{role}"
    
    try:
        message_item = {
            "user_id": user_id,
            "ts": sort_key,
            "session_id": session_id,
            "role": role,
            "text": text,
            "request_id": request_id,
            "timestamp": timestamp
        }
        
        # Add optional fields if provided (convert floats to Decimal)
        if retrieval_meta is not None:
            message_item["retrieval_meta"] = _convert_floats_to_decimal(retrieval_meta)
        if model is not None:
            message_item["model"] = model
        if latency_ms is not None:
            message_item["latency_ms"] = latency_ms
        if tokens is not None:
            message_item["tokens"] = tokens
        
        messages_table.put_item(Item=message_item)
        
        logger.info(json.dumps({
            "action": "log_message",
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "request_id": request_id,
            "text_length": len(text)
        }))
        
        return True
        
    except ClientError as e:
        logger.error(json.dumps({
            "action": "log_message_error",
            "user_id": user_id,
            "role": role,
            "request_id": request_id,
            "error": str(e)
        }))
        return False


def get_user_message_history(
    user_id: str,
    session_id: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Retrieve message history for a user, optionally filtered by session.
    
    Args:
        user_id: User identifier
        session_id: Optional session filter
        limit: Maximum number of messages to retrieve
    
    Returns:
        List of message items sorted by timestamp (newest first)
    """
    _, _, messages_table = get_ddb_tables()
    
    try:
        query_params = {
            "KeyConditionExpression": "user_id = :uid",
            "ExpressionAttributeValues": {":uid": user_id},
            "Limit": limit,
            "ScanIndexForward": False  # Descending order (newest first)
        }
        
        # Add session filter if provided
        if session_id:
            query_params["FilterExpression"] = "session_id = :sid"
            query_params["ExpressionAttributeValues"][":sid"] = session_id
        
        response = messages_table.query(**query_params)
        return response.get("Items", [])
        
    except ClientError as e:
        logger.error(json.dumps({
            "action": "get_message_history_error",
            "user_id": user_id,
            "error": str(e)
        }))
        return []
