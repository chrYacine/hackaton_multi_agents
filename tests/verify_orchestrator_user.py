import requests
import json

ORCHESTRATOR_URL = "http://localhost:8000/api/orchestrate"

print("=" * 60)
print("Verifying Orchestrator with User Test Case")
print("=" * 60)

# User provided test case
payload = {
  "request_id": "2b08b15a-b09a-4117-a2e2-1faf312015e2",
  "user_id": "yacine",
  "agent_spec": {  # Note: The user's JSON had "spec", but my model expects "agent_spec". I'll map it.
    "agent_purpose": "Agent de gestion des emails Gmail",
    "high_level_goal": "Se connecter à un compte Gmail, lire les 300 derniers emails, identifier les emails prioritaires et envoyer un résumé de ces emails prioritaires.",
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
      "Accès aux 300 derniers emails Gmail",
      "Identification des emails prioritaires"
    ],
    "success_criteria": [
      "Résumé des emails prioritaires envoyé avec succès"
    ],
    "needs_clarification": False,
    "clarification_question": None
  }
}

print("\nSending Request...")
try:
    response = requests.post(ORCHESTRATOR_URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Orchestration Successful!")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ Error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"\n❌ Connection error: {e}")
