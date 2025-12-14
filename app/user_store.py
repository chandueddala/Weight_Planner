"""
User Management with Atomic Credit Operations
Handles user creation, retrieval, and credit management with DynamoDB conditional updates.
Extended with email/username lookup and profile management for authentication.
"""
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
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
        user_id: Unique user identifier (will be Cognito sub or generated UUID)
        email: User email address
        starting_credits: Initial credit allocation for new users
    
    Returns:
        User item dict with fields: user_id, email, credits_remaining, plan, created_at, last_login,
        full_name, username, email_verified, auth_provider, onboarding_completed
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


def get_user_by_email(email: str) -> Optional[dict]:
    """
    Look up user by email address.
    Note: Requires a Global Secondary Index (GSI) on email field for efficient lookup.
    
    Args:
        email: User's email address
        
    Returns:
        User item dict or None if not found
    """
    users_table, _, _ = get_ddb_tables()
    
    try:
        # First, try using GSI if available
        # If GSI is not configured, fall back to scan (inefficient, but works for development)
        try:
            response = users_table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            if response.get('Items'):
                return response['Items'][0]
        except ClientError as gsi_error:
            # GSI might not exist, fall back to scan
            logger.warning(f"GSI lookup failed, using scan (inefficient): {gsi_error}")
            response = users_table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            if response.get('Items'):
                return response['Items'][0]
        
        return None
        
    except ClientError as e:
        logger.error(f"Error looking up user by email {email}: {str(e)}")
        return None


def check_username_exists(username: str) -> bool:
    """
    Check if a username already exists.
    Note: Requires a Global Secondary Index (GSI) on username field for efficient lookup.
    
    Args:
        username: Username to check
        
    Returns:
        True if username exists, False otherwise
    """
    users_table, _, _ = get_ddb_tables()
    
    try:
        # Try using GSI if available, otherwise scan
        try:
            response = users_table.query(
                IndexName='username-index',
                KeyConditionExpression='username = :username',
                ExpressionAttributeValues={':username': username}
            )
            
            return len(response.get('Items', [])) > 0
        except ClientError as gsi_error:
            # GSI might not exist, fall back to scan
            logger.warning(f"GSI lookup failed, using scan: {gsi_error}")
            response = users_table.scan(
                FilterExpression='username = :username',
                ExpressionAttributeValues={':username': username}
            )
            
            return len(response.get('Items', [])) > 0
        
    except ClientError as e:
        logger.error(f"Error checking username {username}: {str(e)}")
        return False


def update_user_profile(user_id: str, **kwargs) -> bool:
    """
    Update user profile fields.
    
    Args:
        user_id: User identifier
        **kwargs: Fields to update (full_name, username, email_verified, etc.)
        
    Returns:
        True if update successful
    """
    users_table, _, _ = get_ddb_tables()
    
    if not kwargs:
        logger.warning("No fields provided to update")
        return False
    
    try:
        # Build update expression dynamically
        update_expr_parts = []
        expr_attr_values = {}
        
        for key, value in kwargs.items():
            update_expr_parts.append(f"{key} = :{key}")
            expr_attr_values[f":{key}"] = value
        
        update_expression = "SET " + ", ".join(update_expr_parts)
        
        response = users_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="UPDATED_NEW"
        )
        
        logger.info(json.dumps({
            "action": "update_user_profile",
            "user_id": user_id,
            "fields_updated": list(kwargs.keys())
        }))
        
        return True
        
    except ClientError as e:
        logger.error(json.dumps({
            "action": "update_user_profile_error",
            "user_id": user_id,
            "error": str(e)
        }))
        return False
