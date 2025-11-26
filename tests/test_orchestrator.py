import requests
import json
import uuid

ORCHESTRATOR_URL = "http://localhost:8000/api/orchestrate"

print("=" * 60)
print("Testing Agent 3 (Orchestrator)")
print("=" * 60)

# Mock AgentRequest (as if coming from Agent 2)
agent_request = {
    "request_id": str(uuid.uuid4()),
    "user_id": "test_user",
    "agent_spec": {
        "agent_name": "GmailSummaryAgent",
        "agent_purpose": "Summarize emails from Gmail",
        "high_level_goal": "Connect to Gmail, fetch unread emails, summarize them, and send to Slack.",
        "inputs": ["Gmail credentials", "Slack webhook"],
        "outputs": ["Slack message"],
    }
}

print("\nSending AgentRequest:")
print(json.dumps(agent_request, indent=2))

try:
    response = requests.post(ORCHESTRATOR_URL, json=agent_request)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Orchestration Successful!")
        print("\nResponse:")
        print(json.dumps(data, indent=2))
        
        instance = data["agent_instance"]
        plan = instance["execution_plan"]
        
        print(f"\nAgent Type: {instance['agent_type']}")
        print(f"Plan ID: {plan['plan_id']}")
        print(f"Steps: {len(plan['steps'])}")
        
        for step in plan["steps"]:
            print(f"  - [{step['step_id']}] {step['name']}: {step['description']}")
            
    else:
        print(f"\n❌ Error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"\n❌ Connection error: {e}")
    print("Make sure the API is running: python run_api.py")
