import requests
import json

ORCHESTRATOR_URL = "http://localhost:8000/api/orchestrate"

print("=" * 60)
print("Testing Orchestrator API")
print("=" * 60)

# Correct payload structure based on user's specification
payload = {
  "request_id": "2b08b15a-b09a-4117-a2e2-1faf312015e2",
  "user_id": "yacine",
  "agent_spec": {
    "agent_purpose": "Agent de gestion des emails Gmail",
    "high_level_goal": "Se connecter à un compte Gmail, lire les 300 derniers emails, identifier les emails prioritaires et envoyer un résumé.",
    "inputs": [
      {
        "name": "gmail_email",
        "type": "string",
        "description": "Adresse email Gmail à se connecter"
      },
      {
        "name": "gmail_password",
        "type": "secure_string",
        "description": "Mot de passe Gmail"
      }
    ],
    "outputs": [
      {
        "name": "resume_emails_prioritaires",
        "type": "string",
        "description": "Résumé des emails prioritaires"
      }
    ],
    "constraints": [
      "Authentification Gmail réussie",
      "Accès aux 300 derniers emails",
      "Identification des emails prioritaires"
    ],
    "success_criteria": [
      "Résumé envoyé avec succès"
    ],
    "needs_clarification": False,
    "clarification_question": None
  }
}

print("\nSending Request to Orchestrator...")
print(json.dumps(payload, indent=2, ensure_ascii=False))

try:
    response = requests.post(ORCHESTRATOR_URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Orchestration Successful!")
        print("\nResponse:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        instance = data["agent_instance"]
        plan = instance["execution_plan"]
        
        print(f"\n📊 Summary:")
        print(f"Agent Type: {instance['agent_type']}")
        print(f"Plan ID: {plan['plan_id']}")
        print(f"Number of Steps: {len(plan['steps'])}")
        
        print(f"\n📋 Execution Steps:")
        for step in plan["steps"]:
            print(f"  [{step['step_id']}] {step['name']}")
            print(f"      → {step['description']}")
            
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"\n❌ Connection error: {e}")
    print("Make sure the API is running: python run_api.py")
