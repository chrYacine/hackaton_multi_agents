"""
Test script for Approval Workflow
Tests the complete approval flow: Orchestrate → Approve → Execute
"""

import requests
import json
import uuid


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_orchestrate_creates_pending_plan():
    """Test that orchestration creates a plan with pending approval."""
    print_section("TEST 1: Orchestrate → Pending Plan")
    
    # Create orchestration request
    request_data = {
        "request_id": str(uuid.uuid4()),
        "user_id": "yacine",
        "agent_spec": {
            "high_level_goal": "Résume mes emails non lus et envoie sur Slack",
            "agent_type": "EMAIL_SUMMARY_AGENT",
            "inputs": {
                "gmail_credentials": "mock_creds"
            },
            "outputs": {
                "slack_webhook": "https://hooks.slack.com/mock"
            }
        }
    }
    
    print("📤 Sending orchestration request...")
    response = requests.post(f"{BASE_URL}/api/orchestrate", json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"✅ Orchestration successful!")
        print(f"   Correlation ID: {result['correlation_id']}")
        print(f"   Plan ID: {result['execution_plan']['plan_id']}")
        print(f"   Approval Status: {result['approval']['status']}")
        print(f"   Approval Required: {result['approval']['required']}")
        print(f"   Approved By: {result['approval']['approved_by']}")
        
        # Verify approval is pending
        assert result['approval']['status'] == 'pending', "Approval should be pending"
        assert result['approval']['required'] == True, "Approval should be required"
        assert result['approval']['approved_by'] is None, "Should not be approved yet"
        
        print("\n✅ TEST 1 PASSED: Plan created with pending approval")
        return result
    else:
        print(f"❌ Orchestration failed: {response.status_code}")
        print(response.text)
        raise AssertionError("Orchestration failed")


def test_list_pending_plans(expected_count=1):
    """Test listing pending plans."""
    print_section("TEST 2: List Pending Plans")
    
    response = requests.get(f"{BASE_URL}/api/orchestrate/pending")
    
    if response.status_code == 200:
        pending = response.json()
        
        print(f"✅ Retrieved {len(pending)} pending plan(s)")
        
        for i, plan in enumerate(pending, 1):
            print(f"\n   Plan {i}:")
            print(f"      Plan ID: {plan['execution_plan']['plan_id']}")
            print(f"      Agent Type: {plan['execution_plan']['agent_type']}")
            print(f"      Status: {plan['approval']['status']}")
        
        assert len(pending) >= expected_count, f"Expected at least {expected_count} pending plan(s)"
        
        print(f"\n✅ TEST 2 PASSED: Found {len(pending)} pending plan(s)")
        return pending
    else:
        print(f"❌ Failed to list pending plans: {response.status_code}")
        raise AssertionError("Failed to list pending plans")


def test_approve_plan(plan_id: str):
    """Test approving a plan."""
    print_section("TEST 3: Approve Plan")
    
    approve_data = {
        "approved_by": "yacine"
    }
    
    print(f"📤 Approving plan {plan_id}...")
    response = requests.post(
        f"{BASE_URL}/api/orchestrate/{plan_id}/approve",
        json=approve_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"✅ Plan approved successfully!")
        print(f"   Plan ID: {result['execution_plan']['plan_id']}")
        print(f"   Approval Status: {result['approval']['status']}")
        print(f"   Approved By: {result['approval']['approved_by']}")
        print(f"   Approved At: {result['approval']['approved_at']}")
        
        # Verify approval
        assert result['approval']['status'] == 'approved', "Status should be approved"
        assert result['approval']['approved_by'] == 'yacine', "Should be approved by yacine"
        assert result['approval']['approved_at'] is not None, "Should have approval timestamp"
        
        print("\n✅ TEST 3 PASSED: Plan approved successfully")
        return result
    else:
        print(f"❌ Approval failed: {response.status_code}")
        print(response.text)
        raise AssertionError("Approval failed")


def test_execute_with_approval(orchestration_response):
    """Test executing an approved plan."""
    print_section("TEST 4: Execute Approved Plan")
    
    # Create execution request from orchestration response
    execution_request = {
        "correlation_id": orchestration_response['correlation_id'],
        "request_id": str(uuid.uuid4()),
        "agent_instance": orchestration_response['agent_instance'],
        "execution_plan": orchestration_response['execution_plan'],
        "approval": orchestration_response['approval'],
        "dry_run": True
    }
    
    print(f"📤 Executing approved plan...")
    print(f"   Correlation ID: {execution_request['correlation_id']}")
    print(f"   Approval Status: {execution_request['approval']['status']}")
    
    response = requests.post(f"{BASE_URL}/api/execute", json=execution_request)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✅ Execution successful!")
        print(f"   Status: {result['status']}")
        print(f"   Steps Executed: {len(result['steps'])}")
        
        for step in result['steps']:
            status_emoji = "✅" if step['status'] == 'success' else "❌"
            print(f"      {status_emoji} Step {step['step_id']}: {step['tool']}")
        
        assert result['status'] in ['success', 'partial_success'], "Execution should succeed"
        
        print("\n✅ TEST 4 PASSED: Approved plan executed successfully")
        return result
    else:
        print(f"❌ Execution failed: {response.status_code}")
        print(response.text)
        raise AssertionError("Execution failed")


def test_execute_without_approval():
    """Test that execution is blocked without approval."""
    print_section("TEST 5: Execute Without Approval (Should Fail)")
    
    # Create a new plan
    request_data = {
        "request_id": str(uuid.uuid4()),
        "user_id": "yacine",
        "agent_spec": {
            "high_level_goal": "Test plan for rejection",
            "agent_type": "EMAIL_SUMMARY_AGENT",
            "inputs": {"gmail_credentials": "mock"},
            "outputs": {"slack": "mock"}
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/orchestrate", json=request_data)
    orchestration = response.json()
    
    # Try to execute WITHOUT approving
    execution_request = {
        "correlation_id": orchestration['correlation_id'],
        "request_id": str(uuid.uuid4()),
        "agent_instance": orchestration['agent_instance'],
        "execution_plan": orchestration['execution_plan'],
        "approval": orchestration['approval'],  # Still pending!
        "dry_run": True
    }
    
    print(f"📤 Attempting to execute unapproved plan...")
    print(f"   Approval Status: {execution_request['approval']['status']}")
    
    response = requests.post(f"{BASE_URL}/api/execute", json=execution_request)
    
    # Should fail with 403 (PermissionError)
    if response.status_code == 403:
        print(f"\n✅ Execution correctly blocked!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Error: {response.json().get('detail', 'N/A')[:100]}...")
        
        print("\n✅ TEST 5 PASSED: Unapproved plan was blocked")
        return True
    else:
        print(f"❌ Execution should have been blocked (403) but got status: {response.status_code}")
        if response.status_code == 422:
             print(f"   Validation Error: {response.text}")
        raise AssertionError(f"Execution should have been blocked with 403, got {response.status_code}")


def test_correlation_id_propagation(orchestration_response, execution_result):
    """Test that correlation_id is propagated through the pipeline."""
    print_section("TEST 6: Correlation ID Propagation")
    
    corr_id = orchestration_response['correlation_id']
    
    print(f"Checking correlation_id: {corr_id}")
    
    # Check in orchestration response
    assert orchestration_response['correlation_id'] == corr_id
    assert orchestration_response['agent_instance']['correlation_id'] == corr_id
    assert orchestration_response['execution_plan']['correlation_id'] == corr_id
    print("   ✅ Orchestration Response")
    
    # Check in execution result
    assert execution_result['correlation_id'] == corr_id
    print("   ✅ Execution Result")
    
    print(f"\n✅ TEST 6 PASSED: Correlation ID propagated correctly")


def main():
    """Run all approval workflow tests."""
    print("\n" + "="*80)
    print("  APPROVAL WORKFLOW - COMPLETE TEST SUITE")
    print("="*80)
    print("\nThis test validates the complete approval workflow:")
    print("  1. Orchestrate → Plan with pending approval")
    print("  2. List pending plans")
    print("  3. Approve plan")
    print("  4. Execute approved plan")
    print("  5. Block unapproved execution")
    print("  6. Verify correlation_id propagation")
    print("\nMake sure the API server is running: python run_api.py\n")
    
    try:
        # Test 1: Create plan with pending approval
        orchestration = test_orchestrate_creates_pending_plan()
        plan_id = orchestration['execution_plan']['plan_id']
        
        # Test 2: List pending plans
        test_list_pending_plans(expected_count=1)
        
        # Test 3: Approve the plan
        approved_plan = test_approve_plan(plan_id)
        
        # Test 4: Execute approved plan
        execution_result = test_execute_with_approval(approved_plan)
        
        # Test 5: Try to execute without approval (should fail)
        test_execute_without_approval()
        
        # Test 6: Verify correlation_id propagation
        test_correlation_id_propagation(approved_plan, execution_result)
        
        # Final summary
        print_section("✅ ALL TESTS PASSED!")
        print("The approval workflow is working correctly:")
        print("  ✅ Plans are created with pending approval")
        print("  ✅ Pending plans can be listed")
        print("  ✅ Plans can be approved by commandeur")
        print("  ✅ Approved plans execute successfully")
        print("  ✅ Unapproved plans are blocked")
        print("  ✅ Correlation ID is propagated end-to-end")
        print("\n🎉 The approval system is ready for production!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server.")
        print("Please make sure the server is running: python run_api.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
