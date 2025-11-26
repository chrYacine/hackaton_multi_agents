"""
Diagnostic Complet - Test de Tous les Agents
Vérifie l'état de chaque agent et identifie ce qui manque.
"""

import requests
import json
from datetime import datetime
import uuid


BASE_URL = "http://localhost:8000"


def print_header(title: str, emoji: str = "🔍"):
    """Print a formatted header."""
    print(f"\n{'='*80}")
    print(f"{emoji} {title}")
    print(f"{'='*80}\n")


def print_status(agent: str, status: str, details: str = ""):
    """Print agent status."""
    emoji = "✅" if status == "OK" else "❌" if status == "FAIL" else "⚠️"
    print(f"{emoji} {agent}: {status}")
    if details:
        print(f"   → {details}")




def test_agent_1_chat():
    """Test Agent 1 - Chat Service."""
    print_header("AGENT 1 - CHAT SERVICE", "💬")
    
    try:
        # Test chat endpoint directly (no health check available)
        print("   ℹ️  Testing /api/chat endpoint...")
        
        chat_data = {
            "user_id": "test_user",
            "message": "Bonjour, je veux tester le système"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=chat_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print_status("Chat Service", "OK", "Response received")
            print(f"   Response: {result.get('message', '')[:50]}...")
            return True
        else:
            print_status("Chat Service", "FAIL", f"Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status("Chat Service", "FAIL", "Cannot connect - is server running?")
        return False
    except Exception as e:
        print_status("Chat Service", "FAIL", str(e))
        return False


def test_agent_2_interpretation():
    """Test Agent 2 - Interpretation Service."""
    print_header("AGENT 2 - INTERPRETATION SERVICE", "🧠")
    
    try:
        # Test interpretation endpoint (Expects Form data)
        interpret_data = {
            "user_id": "test_user",
            "text": "Résume mes emails non lus et envoie sur Slack",
            "conversation_id": str(uuid.uuid4())
        }
        
        response = requests.post(
            f"{BASE_URL}/api/interpret",
            data=interpret_data,  # Use data for Form/Multipart
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            agent_spec = result.get("spec") # AgentRequest has 'spec', not 'agent_spec' directly? Let's check model.
            # Wait, AgentRequest has 'spec'. But previous test code used 'agent_spec'.
            # Let's check what service returns.
            # service.process_request returns AgentRequest.
            # AgentRequest has 'spec'.
            
            if not agent_spec and "agent_spec" in result:
                agent_spec = result["agent_spec"] # Fallback if model changed
            
            if agent_spec:
                print_status("Interpretation", "OK", f"AgentSpec generated")
                print(f"   Agent Type: {agent_spec.get('agent_type', 'N/A')}")
                # agent_purpose is in AgentSpec
                print(f"   Purpose: {agent_spec.get('agent_purpose', 'N/A')}")
                
                # Check required fields
                missing = []
                # AgentSpec has agent_purpose, high_level_goal, inputs, outputs
                if not agent_spec.get("agent_purpose"):
                    missing.append("agent_purpose")
                
                if missing:
                    print_status("AgentSpec Validation", "WARNING", f"Missing fields: {missing}")
                else:
                    print_status("AgentSpec Validation", "OK", "All required fields present")
                
                return agent_spec
            else:
                print_status("Interpretation", "FAIL", "No spec in response")
                print(f"   Response keys: {result.keys()}")
                return None
        else:
            print_status("Interpretation", "FAIL", f"Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return None
            
    except Exception as e:
        print_status("Interpretation Service", "FAIL", str(e))
        return None


def test_agent_3_orchestrator(agent_spec):
    """Test Agent 3 - Orchestrator Service."""
    print_header("AGENT 3 - ORCHESTRATOR SERVICE", "🎯")
    
    if not agent_spec:
        print_status("Orchestrator", "SKIP", "No AgentSpec from previous step")
        return None
    
    try:
        orchestrate_data = {
            "request_id": str(uuid.uuid4()),
            "user_id": "test_user",  # Added user_id
            "agent_spec": agent_spec
        }
        
        response = requests.post(
            f"{BASE_URL}/api/orchestrate",
            json=orchestrate_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            agent_instance = result.get("agent_instance")
            execution_plan = result.get("execution_plan")
            
            if agent_instance and execution_plan:
                print_status("Orchestration", "OK", "Plan generated")
                print(f"   Agent ID: {agent_instance.get('agent_id', 'N/A')}")
                print(f"   Plan ID: {execution_plan.get('plan_id', 'N/A')}")
                print(f"   Steps: {len(execution_plan.get('steps', []))}")
                
                # Show steps
                for step in execution_plan.get('steps', []):
                    print(f"      {step.get('step_id')}. {step.get('name')} ({step.get('tool')})")
                
                return result  # Return full result including approval and correlation_id
            else:
                print_status("Orchestration", "FAIL", f"Status: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return None
            
    except Exception as e:
        print_status("Orchestrator Service", "FAIL", str(e))
        return None


def test_agent_debugger(agent_spec):
    """Test Agent Debugger - Debug Service."""
    print_header("AGENT DEBUGGER - DEBUG SERVICE", "🐛")
    
    if not agent_spec:
        print_status("Debug Service", "SKIP", "No AgentSpec from previous step")
        return None
    
    try:
        # Construct AgentRequest for Debug Service
        debug_data = {
            "request_id": str(uuid.uuid4()),
            "user_id": "test_user",
            "spec": agent_spec,
            "status": "created"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/debug/analyze",  # Corrected endpoint
            json=debug_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status")
            errors = result.get("errors", [])
            warnings = result.get("warnings", [])
            
            print_status("Debug Validation", "OK", f"Status: {status}")
            print(f"   Errors: {len(errors)}")
            print(f"   Warnings: {len(warnings)}")
            
            if errors:
                print("\n   ❌ Errors found:")
                for err in errors[:3]:  # Show first 3
                    print(f"      - {err.get('message', 'N/A')}")
            
            if warnings:
                print("\n   ⚠️  Warnings found:")
                for warn in warnings[:3]:  # Show first 3
                    print(f"      - {warn.get('message', 'N/A')}")
            
            return result
        else:
            print_status("Debug Service", "FAIL", f"Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_status("Debug Service", "FAIL", str(e))
        return None


def test_agent_4_executor(orchestration_result):
    """Test Agent 4 - Execution Service."""
    print_header("AGENT 4 - EXECUTION SERVICE", "⚙️")
    
    if not orchestration_result:
        print_status("Execution Service", "SKIP", "No orchestration result from previous step")
        return None
    
    try:
        # First check health
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print_status("Execution Health", "OK", f"Status: {health.get('status')}")
        
        # List available tools
        response = requests.get(f"{BASE_URL}/api/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()
            print_status("Tools Registry", "OK", f"{tools.get('count')} tools available")
            print(f"   Tools: {', '.join(tools.get('tools', []))}")
        
        # Test dry-run execution
        # Approve the plan first
        plan_id = orchestration_result["execution_plan"]["plan_id"]
        print(f"\n   ✍️  Approving plan {plan_id}...")
        
        approve_response = requests.post(
            f"{BASE_URL}/api/orchestrate/{plan_id}/approve",
            json={"approved_by": "diagnostic_test"}
        )
        
        if approve_response.status_code != 200:
            print_status("Plan Approval", "FAIL", f"Status: {approve_response.status_code}")
            return None
            
        approved_result = approve_response.json()
        print_status("Plan Approval", "OK", "Plan approved by diagnostic_test")

        # Test dry-run execution
        execution_data = {
            "correlation_id": approved_result["correlation_id"],
            "request_id": str(uuid.uuid4()),
            "agent_instance": approved_result["agent_instance"],
            "execution_plan": approved_result["execution_plan"],
            "approval": approved_result["approval"],
            "dry_run": True
        }
        
        print("\n   🔍 Testing DRY RUN execution...")
        response = requests.post(
            f"{BASE_URL}/api/execute",
            json=execution_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status")
            steps = result.get("steps", [])
            
            print_status("Dry Run Execution", "OK", f"Status: {status}")
            print(f"   Steps executed: {len(steps)}")
            
            for step in steps:
                step_status = "✅" if step.get('status') == 'success' else "❌"
                print(f"      {step_status} Step {step.get('step_id')}: {step.get('tool')}")
            
            # Test actual execution
            print("\n   ⚙️  Testing ACTUAL execution (with mocks)...")
            execution_data["dry_run"] = False
            execution_data["request_id"] = str(uuid.uuid4())
            
            response = requests.post(
                f"{BASE_URL}/api/execute",
                json=execution_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status")
                
                print_status("Actual Execution", "OK", f"Status: {status}")
                
                # Check if context has expected data
                context = result.get("context", {})
                if "summary_text" in context:
                    print_status("Context Flow", "OK", "Summary generated and available")
                
                return result
            else:
                print_status("Actual Execution", "FAIL", f"Status: {response.status_code}")
                return None
        else:
            print_status("Dry Run Execution", "FAIL", f"Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return None
            
    except Exception as e:
        print_status("Execution Service", "FAIL", str(e))
        return None


def analyze_gaps():
    """Analyze what's missing or needs improvement."""
    print_header("ANALYSE DES MANQUES", "📊")
    
    gaps = {
        "Critiques": [],
        "Importants": [],
        "Améliorations": []
    }
    
    # Critical gaps
    gaps["Critiques"].extend([
        "Intégrations réelles (Gmail, Groq, Slack) - actuellement en mock",
        "Gestion des secrets (credentials en dur dans le code)",
        "Persistance des exécutions (pas de base de données)",
    ])
    
    # Important gaps
    gaps["Importants"].extend([
        "Correlation ID global pour tracer tout le pipeline",
        "Politiques d'erreur configurables (retry, continue, stop)",
        "Validation d'approbation stricte (actuellement juste un warning)",
        "Tests de contrat entre services",
    ])
    
    # Improvements
    gaps["Améliorations"].extend([
        "UI Console pour approuver les plans",
        "Monitoring et métriques (durée, taux de succès)",
        "Logs structurés JSON",
        "Timeouts et limites de sécurité",
        "Versioning des schémas (schema_version)",
        "Exécution parallèle des steps indépendants",
    ])
    
    for category, items in gaps.items():
        print(f"\n🔴 {category}:")
        for i, item in enumerate(items, 1):
            print(f"   {i}. {item}")
    
    return gaps


def main():
    """Run complete diagnostic."""
    print("\n" + "="*80)
    print("🔍 DIAGNOSTIC COMPLET - SYSTÈME MULTI-AGENT")
    print("="*80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("\nCe script va tester tous les agents dans l'ordre du pipeline.\n")
    
    results = {
        "agent_1_chat": False,
        "agent_2_interpretation": None,
        "agent_3_orchestrator": None,
        "agent_debugger": None,
        "agent_4_executor": None,
    }
    
    # Test each agent in sequence
    results["agent_1_chat"] = test_agent_1_chat()
    
    agent_spec = test_agent_2_interpretation()
    results["agent_2_interpretation"] = agent_spec is not None
    
    orchestration_result = test_agent_3_orchestrator(agent_spec)
    results["agent_3_orchestrator"] = orchestration_result is not None
    
    debug_result = test_agent_debugger(agent_spec)
    results["agent_debugger"] = debug_result is not None
    
    execution_result = test_agent_4_executor(orchestration_result)
    results["agent_4_executor"] = execution_result is not None
    
    # Summary
    print_header("RÉSUMÉ DU DIAGNOSTIC", "📋")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nRésultats: {passed}/{total} agents fonctionnels\n")
    
    for agent, status in results.items():
        emoji = "✅" if status else "❌"
        agent_name = agent.replace("_", " ").title()
        print(f"{emoji} {agent_name}: {'OK' if status else 'FAIL'}")
    
    # Analyze gaps
    gaps = analyze_gaps()
    
    # Final recommendations
    print_header("RECOMMANDATIONS", "💡")
    
    if passed == total:
        print("✅ Tous les agents sont fonctionnels en mode POC (avec mocks)!")
        print("\n📌 Prochaines étapes recommandées:")
        print("   1. Implémenter les intégrations réelles (Gmail, Groq, Slack)")
        print("   2. Ajouter la gestion des secrets (SecretProvider)")
        print("   3. Mettre en place la persistance (Redis/Postgres)")
        print("   4. Ajouter le Correlation ID global")
        print("\n📖 Voir ROADMAP_V2.md pour le plan détaillé")
    else:
        print("⚠️  Certains agents ne fonctionnent pas correctement.")
        print("\n🔧 Actions à prendre:")
        print("   1. Vérifier que le serveur est démarré: python run_api.py")
        print("   2. Vérifier les logs du serveur pour les erreurs")
        print("   3. Tester chaque agent individuellement")
    
    print("\n" + "="*80)
    print("🏁 DIAGNOSTIC TERMINÉ")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
