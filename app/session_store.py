"""
Stateful Session Management
Manages user conversation sessions with summary, recent turns, preferences, and retrieval context.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
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


def _get_empty_state() -> Dict[str, Any]:
    """Returns default empty session state structure."""
    return {
        "summary": "",
        "recent_turns": [],
        "preferences": {},
        "last_retrieval": []
    }


def load_state(user_id: str, session_id: str) -> Dict[str, Any]:
    """
    Load session state for a user.
    
    Args:
        user_id: User identifier
        session_id: Session identifier (e.g., 'default' or UUID)
    
    Returns:
        Session state dict with keys: summary, recent_turns, preferences, last_retrieval
    """
    _, sessions_table, _ = get_ddb_tables()
    
    try:
        response = sessions_table.get_item(
            Key={"user_id": user_id, "session_id": session_id}
        )
        
        if "Item" in response:
            state = response["Item"].get("state_json", {})
            logger.info(json.dumps({
                "action": "load_state",
                "user_id": user_id,
                "session_id": session_id,
                "turns_count": len(state.get("recent_turns", []))
            }))
            return state
        
        # No session exists, return empty state
        logger.info(json.dumps({
            "action": "load_state_new",
            "user_id": user_id,
            "session_id": session_id
        }))
        return _get_empty_state()
        
    except ClientError as e:
        logger.error(json.dumps({
            "action": "load_state_error",
            "user_id": user_id,
            "session_id": session_id,
            "error": str(e)
        }))
        return _get_empty_state()


def save_state(user_id: str, session_id: str, state: Dict[str, Any]) -> bool:
    """
    Save session state to DynamoDB.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        state: State dict with keys: summary, recent_turns, preferences, last_retrieval
    
    Returns:
        True if save was successful
    """
    _, sessions_table, _ = get_ddb_tables()
    
    try:
        # Convert any float values to Decimal for DynamoDB compatibility
        state_converted = _convert_floats_to_decimal(state)
        
        sessions_table.put_item(Item={
            "user_id": user_id,
            "session_id": session_id,
            "state_json": state_converted,
            "last_updated": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(json.dumps({
            "action": "save_state",
            "user_id": user_id,
            "session_id": session_id,
            "turns_count": len(state.get("recent_turns", []))
        }))
        return True
        
    except ClientError as e:
        logger.error(json.dumps({
            "action": "save_state_error",
            "user_id": user_id,
            "session_id": session_id,
            "error": str(e)
        }))
        return False


def append_turn(
    state: Dict[str, Any],
    user_text: str,
    assistant_text: str,
    max_turns: int = 6
) -> Dict[str, Any]:
    """
    Append a conversation turn to recent_turns, maintaining max_turns limit (FIFO).
    
    Args:
        state: Session state dict
        user_text: User's input message
        assistant_text: Assistant's response
        max_turns: Maximum number of turns to keep (default: 6)
    
    Returns:
        Updated state dict
    """
    recent_turns = state.get("recent_turns", [])
    
    # Add new turn
    recent_turns.append({"role": "user", "text": user_text})
    recent_turns.append({"role": "assistant", "text": assistant_text})
    
    # Keep only last max_turns * 2 messages (user + assistant pairs)
    if len(recent_turns) > max_turns * 2:
        recent_turns = recent_turns[-(max_turns * 2):]
    
    state["recent_turns"] = recent_turns
    return state


def update_retrieval_context(
    state: Dict[str, Any],
    retrieval_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Update last_retrieval with current retrieval results.
    
    Args:
        state: Session state dict
        retrieval_results: List of dicts with keys: source, chunk_id, score
    
    Returns:
        Updated state dict
    """
    state["last_retrieval"] = retrieval_results
    return state


def update_preferences(
    state: Dict[str, Any],
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update user preferences in session state.
    
    Args:
        state: Session state dict
        preferences: Dict of user preferences (e.g., age, gender, weight goals, etc.)
    
    Returns:
        Updated state dict
    """
    if "preferences" not in state:
        state["preferences"] = {}
    
    state["preferences"].update(preferences)
    return state


def build_context_prompt(state: Dict[str, Any]) -> str:
    """
    Build a condensed context string from session state for retrieval query enhancement.
    
    Args:
        state: Session state dict
    
    Returns:
        Context string summarizing conversation history and preferences
    """
    parts = []
    
    # Add summary if exists
    if state.get("summary"):
        parts.append(f"Session summary: {state['summary']}")
    
    # Add recent conversation context
    recent_turns = state.get("recent_turns", [])
    if recent_turns:
        last_few = recent_turns[-4:]  # Last 2 exchanges
        conversation = " ".join([f"{turn['role']}: {turn['text']}" for turn in last_few])
        parts.append(f"Recent conversation: {conversation}")
    
    # Add user preferences
    prefs = state.get("preferences", {})
    if prefs:
        pref_str = ", ".join([f"{k}: {v}" for k, v in prefs.items()])
        parts.append(f"User preferences: {pref_str}")
    
    return " | ".join(parts) if parts else ""
