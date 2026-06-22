import logging
from vault.redis_client import RedisClient
from vault.token_store import TokenStore

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_storage_workflow():
    """
    Day 3 & 6 Task: Store 5 mappings, retrieve them, and verify correctness.
    Updated to support session-scoped token store operations.
    """
    print("--- Starting Vault Storage Workflow Test ---")
    
    redis_client = RedisClient().get_client()
    # For testing purposes, let's clear the DB so we start fresh. 
    # NEVER do this in production!
    redis_client.flushdb() 
    
    store = TokenStore(redis_client)
    session_id = "session_test_123"

    # 1. Store 5 sample mappings
    samples = [
        ("PATIENT", "John Smith"),
        ("PATIENT", "Jane Doe"),
        ("DOCTOR", "Dr. Adams"),
        ("HOSPITAL", "General Hospital"),
        ("PATIENT", "John Smith") # Duplicate to test consistency
    ]

    print(f"\n[Phase 1] Storing Mappings for session '{session_id}'...")
    tokens = []
    for entity_type, name in samples:
        token = store.get_or_create_token(session_id, entity_type, name)
        tokens.append(token)
        print(f"Stored: {name} -> {token}")

    # 2. Retrieve all mappings to verify correctness
    print("\n[Phase 2] Retrieving original names from tokens...")
    for token in set(tokens): # Use set to get unique tokens
        original_name = store.get_name_from_token(session_id, token)
        print(f"Retrieved: {token} -> {original_name}")

    # 3. Verify John Smith received the exact same token both times
    john_token_1 = tokens[0]
    john_token_2 = tokens[4]
    
    print("\n[Phase 3] Verifying Consistency...")
    if john_token_1 == john_token_2:
        print(f"✅ SUCCESS: 'John Smith' consistently received {john_token_1}")
    else:
        print(f"❌ FAILED: Token mismatch for 'John Smith' ({john_token_1} vs {john_token_2})")

if __name__ == "__main__":
    test_storage_workflow()