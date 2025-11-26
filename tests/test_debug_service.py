import requests
import json
import uuid

DEBUG_URL = "http://localhost:8000/api/debug/analyze"

print("=" * 60)
print("Testing Agent Debugger (Debug Service)")
print("=" * 60)

# 1. Test with a GOOD request
good_request = {
  "request_id": str(uuid.uuid4()),
  "user_id": "test_user",
  "spec": {  # Correct field name
    "agent_purpose": "Agent Gmail",
    "high_level_goal": "Manage emails",
    "inputs": [
      {"name": "gmail_password", "type": "secure_string", "description": "Password"}
    ],
    "outputs": [
      {"name": "summary", "type": "string", "description": "Email summary"}
    ],
    "constraints": ["Auth required"],
    "success_criteria": ["Summary sent"]
  }
}

print("\n[Test 1] Sending GOOD Request...")
try:
    response = requests.post(DEBUG_URL, json=good_request)
    if response.status_code == 200:
        print("✅ Analysis Successful!")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Connection error: {e}")


# 2. Test with a BAD request (valid Pydantic, but bad logic)
bad_request = {
  "request_id": str(uuid.uuid4()),
  "user_id": "test_user",
  "spec": {
    "agent_purpose": "Bad Agent",
    "high_level_goal": "Do bad things",
    "inputs": [
      {"name": "gmail_password", "type": "string", "description": "Insecure password"}  # Insecure!
    ],
    "outputs": [],
    "constraints": [],  # Missing!
    "success_criteria": []  # Missing!
  }
}

print("\n[Test 2] Sending BAD Request...")
try:
    response = requests.post(DEBUG_URL, json=bad_request)
    if response.status_code == 200:
        print("✅ Analysis Successful!")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Connection error: {e}")
