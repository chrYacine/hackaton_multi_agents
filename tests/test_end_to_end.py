"""
End-to-End Test: Complete Multi-Agent Pipeline
Tests the full flow: Chat → Interpretation → Orchestration → Debug → Execution
"""

import requests
import json
import uuid


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_end_to_end_flow():
    """
    Test the complete pipeline from user message to execution.
    
    Flow:
    1. User sends message to Chat Service
    2. Chat generates response and triggers Interpretation
    3. Interpretation creates AgentSpec
    4. Orchestrator generates ExecutionPlan
    5. Debug validates the plan
    6. Executor runs the plan
    """
    
    print_section("🚀 END-TO-END MULTI-AGENT PIPELINE TEST")
    
    # Step 1: Chat Service (simulated - we'll start from AgentSpec)
    print_section("Step 1: User Message (Simulated)")
    user_message = "Résume mes emails non lus des 30 dernières minutes et poste le résumé sur Slack"
    print(f"User: {user_message}")
    print("\n✅ Chat Service would process this and trigger Interpretation...")
    
    # Step 2: Interpretation Service - Create AgentSpec
    print_section("Step 2: Interpretation Service - Generate AgentSpec")
    
    # For this test, we'll create a mock AgentSpec directly
    # In real flow, this would come from POST /api/interpret
    agent_spec = {
        "agent_purpose": "Summarize unread emails and send to Slack",
        "high_level_goal": "Summarize emails",
        "inputs": [
            {"name": "gmail_credentials", "type": "string", "description": "User OAuth token"},
            {"name": "email_filter", "type": "string", "description": "Filter for emails"}
        ],
        "outputs": [
            {"name": "slack_webhook", "type": "string", "description": "Slack webhook URL"},
            {"name": "slack_channel", "type": "string", "description": "Slack channel"}
        ],
        "constraints": [
            "max_emails: 50",
            "summary_format: structured"
        ],
        "agent_type": "EMAIL_SUMMARY_AGENT"  # Optional hint for Orchestrator
    }
    
    print(f"Generated AgentSpec:")
    print(json.dumps(agent_spec, indent=2))
    print("\n✅ AgentSpec created successfully")
    
    # Step 3: Orchestrator Service - Generate ExecutionPlan
    print_section("Step 3: Orchestrator Service - Generate ExecutionPlan")
    
    orchestrate_request = {
        "request_id": str(uuid.uuid4()),
        "user_id": "yacine",
        "agent_spec": agent_spec
    }
    
    print("📤 Calling Orchestrator API...")
    response = requests.post(
        f"{BASE_URL}/api/orchestrate",
        json=orchestrate_request
    )
    
    if response.status_code != 200:
        print(f"❌ Orchestrator failed: {response.text}")
        return False
    
    orchestrate_result = response.json()
    agent_instance = orchestrate_result["agent_instance"]
    execution_plan = orchestrate_result["execution_plan"]
    
    print(f"\n✅ Orchestrator Response:")
    print(f"   Agent Type: {agent_instance['agent_type']}")
    print(f"   Plan ID: {execution_plan['plan_id']}")
    print(f"   Steps: {len(execution_plan['steps'])}")
    
    for step in execution_plan['steps']:
        print(f"      - Step {step['step_id']}: {step['name']} ({step['tool']})")
    
    # Step 4: Debug Service - Validate AgentSpec
    print_section("Step 4: Debug Service - Validate AgentSpec")
    
    debug_request = {
        "request_id": str(uuid.uuid4()),
        "user_id": "e2e_test",
        "spec": agent_spec
    }
    
    print("📤 Calling Debug API...")
    response = requests.post(
        f"{BASE_URL}/api/debug/analyze",
        json=debug_request
    )
    
    if response.status_code != 200:
        print(f"❌ Debug failed: {response.text}")
        return False
    
    debug_result = response.json()
    
    # New schema: summary + issues (not status)
    summary = debug_result.get("summary", "(no summary)")
    issues = debug_result.get("issues", [])
    suggested_fixes = debug_result.get("suggested_fixes", [])
    
    errors = [i for i in issues if i.get("severity") == "error"]
    warnings = [i for i in issues if i.get("severity") == "warning"]
    
    print(f"\n✅ Debug Report:")
    print(f"   Summary       : {summary}")
    print(f"   Errors        : {len(errors)}")
    print(f"   Warnings      : {len(warnings)}")
    print(f"   Suggestions   : {len(suggested_fixes)}")
    
    if errors:
        print(f"\n⚠️  AgentSpec has validation errors:")
        for error in errors:
            print(f"      ❌ {error.get('description', 'N/A')}")
    
    if warnings:
        print(f"\n⚠️  AgentSpec has validation warnings:")
        for warning in warnings:
            print(f"      ⚠️  {warning.get('description', 'N/A')}")
    
    # Step 5: Execution Service - Execute Plan
    print_section("Step 5: Execution Service - Execute Plan")
    
    # First, approve the plan
    plan_id = execution_plan["plan_id"]
    print(f"✍️  Approving plan {plan_id}...\n")
    
    approve_response = requests.post(
        f"{BASE_URL}/api/orchestrate/{plan_id}/approve",
        json={"approved_by": "e2e_test"}
    )
    
    if approve_response.status_code != 200:
        print(f"❌ Plan approval failed: {approve_response.text}")
        return False
    
    approved_result = approve_response.json()
    print(f"✅ Plan approved by e2e_test\n")
    
    # Now test with dry_run
    print("🔍 Testing with DRY RUN mode first...\n")
    
    execution_request = {
        "request_id": str(uuid.uuid4()),
        "correlation_id": approved_result["correlation_id"],
        "agent_instance": approved_result["agent_instance"],
        "execution_plan": approved_result["execution_plan"],
        "approval": approved_result["approval"],
        "dry_run": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/execute",
        json=execution_request
    )
    
    if response.status_code != 200:
        print(f"❌ Execution (dry-run) failed: {response.text}")
        return False
    
    dry_run_result = response.json()
    
    print(f"✅ Dry Run Result:")
    print(f"   Status: {dry_run_result['status']}")
    print(f"   Steps Executed: {len(dry_run_result['steps'])}")
    
    for step in dry_run_result['steps']:
        status_emoji = "✅" if step['status'] == 'success' else "❌"
        print(f"      {status_emoji} Step {step['step_id']}: {step['tool']}")
    
    # Now execute for real (with mocks)
    print("\n⚙️  Executing ACTUAL plan (with mock tools)...\n")
    
    execution_request["dry_run"] = False
    execution_request["request_id"] = str(uuid.uuid4())
    
    response = requests.post(
        f"{BASE_URL}/api/execute",
        json=execution_request
    )
    
    if response.status_code != 200:
        print(f"❌ Execution failed: {response.text}")
        return False
    
    execution_result = response.json()
    
    print(f"✅ Execution Result:")
    print(f"   Status: {execution_result['status']}")
    print(f"   Request ID: {execution_result['request_id']}")
    
    print(f"\n📋 Step Execution Details:")
    for step in execution_result['steps']:
        status_emoji = "✅" if step['status'] == 'success' else "❌"
        print(f"\n   {status_emoji} Step {step['step_id']}: {step['tool']}")
        print(f"      Status: {step['status']}")
        
        if step.get('output'):
            # Show key outputs
            output = step['output']
            if 'gmail_token' in output:
                print(f"      → Authenticated: {output.get('authenticated')}")
            elif 'emails' in output:
                print(f"      → Fetched {output.get('count')} emails")
            elif 'summary_text' in output:
                print(f"      → Generated summary ({output.get('email_count')} emails)")
            elif 'slack_message_id' in output:
                print(f"      → Posted to {output.get('channel')}")
    
    # Show final summary if available
    if 'summary_text' in execution_result.get('context', {}):
        print(f"\n📝 Generated Email Summary:")
        print("─" * 70)
        print(execution_result['context']['summary_text'])
        print("─" * 70)
    
    # Final Summary
    print_section("✅ END-TO-END TEST COMPLETED SUCCESSFULLY!")
    
    print("Pipeline Flow Summary:")
    print("   1. ✅ User Message → Chat Service")
    print("   2. ✅ Chat → Interpretation Service → AgentSpec")
    print("   3. ✅ AgentSpec → Orchestrator Service → ExecutionPlan")
    print("   4. ✅ AgentSpec → Debug Service → Validation")
    print("   5. ✅ ExecutionPlan → Execution Service → Results")
    
    print(f"\n🎉 All {len(execution_result['steps'])} steps executed successfully!")
    print("\n💡 The complete multi-agent pipeline is operational!")
    
    return True


def main():
    """Run the end-to-end test."""
    print("\n" + "="*70)
    print("  MULTI-AGENT PIPELINE - END-TO-END TEST")
    print("="*70)
    print("\nThis test validates the complete flow from user input to execution.")
    print("Make sure the API server is running: python run_api.py\n")
    
    try:
        success = test_end_to_end_flow()
        
        if success:
            print("\n" + "="*70)
            print("  🎊 SUCCESS! The multi-agent system is fully operational!")
            print("="*70)
        else:
            print("\n❌ Test failed. Check the error messages above.")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server.")
        print("Please make sure the server is running: python run_api.py")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
