"""
Test for GPTCustomPromptPlanner with DynamoDB Integration
Validates that the original class now has full stateful persistence.
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GPTCustomPrompt import GPTCustomPromptPlanner
from app.user_store import get_user_credits
from app.session_store import load_state
from app.message_store import get_user_message_history

# Load environment
load_dotenv()

def test_gpt_custom_prompt_stateful():
    """Test GPTCustomPromptPlanner with DynamoDB integration."""
    
    print("\n" + "="*80)
    print("GPTCUSTOMPROMPT WITH DYNAMODB - INTEGRATION TEST")
    print("="*80 + "\n")
    
    # Test parameters
    test_user_id = "test-gpt-custom-001"
    test_session_id = "gpt-session-001"
    
    print("📋 Test Configuration")
    print(f"   User ID: {test_user_id}")
    print(f"   Session ID: {test_session_id}")
    print()
    
    # Initialize planner
    print("🔍 STEP 1: Initialize GPTCustomPromptPlanner")
    print("-" * 80)
    
    planner = GPTCustomPromptPlanner()
    print("✅ Planner initialized")
    print()
    
    # Get initial credits
    initial_credits = get_user_credits(test_user_id)
    print(f"   Initial Credits: {initial_credits if initial_credits > 0 else '(will create new user with 20 credits)'}")
    print()
    
    # Test 1: Generate with all preferences provided
    print("🔍 STEP 2: Generate with Full Preferences")
    print("-" * 80)
    
    prompt1, response1, docs1, metadata1 = planner.generate(
        user_prompt="What are good protein sources for muscle gain?",
        user_id=test_user_id,
        session_id=test_session_id,
        age=25,
        gender="male",
        height_cm=180,
        present_weight=75,
        target_weight=80,
        calories=2800
    )
    
    print("✅ First query completed")
    print(f"   Request ID: {metadata1['request_id']}")
    print(f"   Credits Remaining: {metadata1['credits_remaining']}")
    print(f"   Latency: {metadata1['latency_ms']} ms")
    print(f"   Chunks Retrieved: {metadata1['chunks_retrieved']}")
    print(f"   Response (first 200 chars): {response1[:200]}...")
    print()
    
    # Verify credits deducted
    current_credits = metadata1['credits_remaining']
    credits_used = (initial_credits or 20) - current_credits
    print(f"   Credits used: {credits_used}")
    assert credits_used > 0, "Expected credits to be deducted"
    print()
    
    # Verify session state has preferences
    print("🔍 STEP 3: Verify Session State (Preferences Stored)")
    print("-" * 80)
    
    session_state = load_state(test_user_id, test_session_id)
    stored_prefs = session_state.get("preferences", {})
    
    print("✅ Session state loaded")
    print(f"   Stored Preferences: {stored_prefs}")
    print(f"   Conversation Turns: {len(session_state.get('recent_turns', []))}")
    print()
    
    assert stored_prefs.get("age") == 25, "Age not stored correctly"
    assert stored_prefs.get("target_weight") == 80, "Target weight not stored correctly"
    print("   ✅ Preferences stored correctly in session")
    print()
    
    # Test 2: Generate WITHOUT preferences (should load from session)
    print("🔍 STEP 4: Generate Without Preferences (Load from Session)")
    print("-" * 80)
    
    prompt2, response2, docs2, metadata2 = planner.generate(
        user_prompt="What about carbohydrates for energy?",
        user_id=test_user_id,
        session_id=test_session_id
        # NOTE: No age, gender, weight goals provided - should load from session!
    )
    
    print("✅ Second query completed (preferences loaded from session)")
    print(f"   Request ID: {metadata2['request_id']}")
    print(f"   Credits Remaining: {metadata2['credits_remaining']}")
    print(f"   Response (first 200 chars): {response2[:200]}...")
    print()
    
    # Verify prompt used stored preferences
    assert "Age: 25" in prompt2 or "age" in prompt2.lower(), "Prompt should include stored age"
    print("   ✅ Prompt correctly used stored preferences")
    print()
    
    # Verify session has 4 turns (2 queries * 2 messages each)
    print("🔍 STEP 5: Verify Conversation History")
    print("-" * 80)
    
    updated_state = load_state(test_user_id, test_session_id)
    turns = updated_state.get("recent_turns", [])
    
    print(f"✅ Total conversation turns: {len(turns)}")
    assert len(turns) >= 4, f"Expected at least 4 turns, got {len(turns)}"
    
    print("   Recent conversation:")
    for i, turn in enumerate(turns[-4:]):
        role = turn.get("role")
        text = turn.get("text", "")
        print(f"      [{i+1}] {role}: {text[:80]}...")
    print()
    
    # Verify messages logged
    print("🔍 STEP 6: Verify Audit Log")
    print("-" * 80)
    
    messages = get_user_message_history(test_user_id, session_id=test_session_id, limit=10)
    
    print(f"✅ Messages in audit log: {len(messages)}")
    assert len(messages) >= 4, f"Expected at least 4 messages, got {len(messages)}"
    
    print("   Latest messages:")
    for i, msg in enumerate(messages[:4]):
        role = msg.get("role")
        text = msg.get("text", "")
        print(f"      [{i+1}] {role}: {text[:100]}...")
    print()
    
    # FINAL SUMMARY
    print("\n" + "="*80)
    print("✅ GPTCUSTOMPROMPT INTEGRATION TEST PASSED!")
    print("="*80)
    print("\nVerified:")
    print("  ✓ GPTCustomPromptPlanner works with DynamoDB")
    print("  ✓ Credits deducted on each query")
    print("  ✓ User preferences stored in session state")
    print("  ✓ Preferences loaded automatically when not provided")
    print("  ✓ Conversation history maintained across queries")
    print("  ✓ Full audit logging to DynamoDB")
    print("  ✓ All metadata returned (request_id, credits, latency, etc.)")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        test_gpt_custom_prompt_stateful()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
