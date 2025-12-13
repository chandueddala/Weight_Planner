"""
User Management with Atomic Credit Operations
Handles user creation, retrieval, and credit management with DynamoDB conditional updates.
"""
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from botocore.exceptions import ClientError
from .aws_session import get_ddb_tables

logger = logging.getLogger(__name__)


def _decimal_to_number(obj):
    """Convert DynamoDB Decimal objects to int or float for JSON serialization."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


def get_or_create_user(user_id: str, email: str = None, starting_credits: int = 20) -> dict:
    """
    Get existing user or create new user with starting credits.
    
    Args:
        user_id: Unique user identifier (will be Cognito sub in production)
        email: User email address
        starting_credits: Initial credit allocation for new users
    
    Returns:
        User item dict with fields: user_id, email, credits_remaining, plan, created_at, last_login
    """
    users_table, _, _ = get_ddb_tables()
    
    try:
        # Try to get existing user
        response = users_table.get_item(Key={"user_id": user_id})
        
        if "Item" in response:
            user = response["Item"]
            logger.info(json.dumps({
                "action": "get_user",
                "user_id": user_id,
                "credits": _decimal_to_number(user.get("credits_remaining", 0))
            }))
            return user
        
        # User doesn't exist, create new
        now_iso = datetime.now(timezone.utc).isoformat()
        new_user = {
            "user_id": user_id,
            "email": email or f"{user_id}@example.com",
            "credits_remaining": starting_credits,
            "plan": "free",
            "created_at": now_iso,
            "last_login": now_iso
        }
        
        users_table.put_item(Item=new_user)
        logger.info(json.dumps({
            "action": "create_user",
            "user_id": user_id,
            "credits": starting_credits
        }))
        
        return new_user
        
    except ClientError as e:
        logger.error(json.dumps({
            "action": "get_or_create_user_error",
            "user_id": user_id,
            "error": str(e)
        }))
        raise


def charge_credits(user_id: str, cost: int = 1, request_id: str = None) -> bool:
    """
    Atomically deduct credits from user account with conditional update.
    Ensures credits cannot go negative and prevents double-charging on retries.
    
    Args:
        user_id: User to charge
        cost: Number of credits to deduct
        request_id: Optional request ID for idempotency tracking
    
    Returns:
        True if credits were successfully charged
    
    Raises:
        ValueError: If user has insufficient credits
        ClientError: On DynamoDB errors
    """
    users_table, _, _ = get_ddb_tables()
    
    try:
        # Atomic update with condition: credits_remaining must be >= cost
        response = users_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="SET credits_remaining = credits_remaining - :cost, last_login = :now",
            ConditionExpression="credits_remaining >= :cost",
            ExpressionAttributeValues={
                ":cost": cost,
                ":now": datetime.now(timezone.utc).isoformat()
            },
            ReturnValues="UPDATED_NEW"
        )
        
        new_credits = response["Attributes"]["credits_remaining"]
        logger.info(json.dumps({
            "action": "charge_credits_success",
            "user_id": user_id,
            "cost": cost,
            "remaining_credits": _decimal_to_number(new_credits),
            "request_id": request_id
        }))
        
        return True
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        
        if error_code == "ConditionalCheckFailedException":
            # User has insufficient credits
            logger.warning(json.dumps({
                "action": "charge_credits_failed",
                "user_id": user_id,
                "cost": cost,
                "reason": "insufficient_credits",
                "request_id": request_id
            }))
            raise ValueError(f"Insufficient credits for user {user_id}")
        
        logger.error(json.dumps({
            "action": "charge_credits_error",
            "user_id": user_id,
            "error": str(e),
            "request_id": request_id
        }))
        raise


def get_user_credits(user_id: str) -> int:
    """
    Get current credit balance for user.
    
    Args:
        user_id: User identifier
    
    Returns:
        Current credit balance
    """
    users_table, _, _ = get_ddb_tables()
    
    try:
        response = users_table.get_item(Key={"user_id": user_id})
        if "Item" not in response:
            return 0
        return _decimal_to_number(response["Item"].get("credits_remaining", 0))
    except ClientError as e:
        logger.error(json.dumps({
            "action": "get_credits_error",
            "user_id": user_id,
            "error": str(e)
        }))
        return 0
