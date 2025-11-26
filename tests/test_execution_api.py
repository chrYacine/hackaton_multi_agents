"""
Test script for Execution Service API
Tests the /api/execute endpoint with various scenarios.
"""

import requests
import json
from datetime import datetime
import uuid


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_health_check():
    """Test the health check endpoint."""
    print_section("TEST 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["service"] == "execution_service"
    print("✅ Health check passed!")


def test_list_tools():
    """Test listing available tools."""
    print_section("TEST 2: List Available Tools")
    
    response = requests.get(f"{BASE_URL}/api/tools")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    tools = response.json()["tools"]
    assert "gmail_auth" in tools
    assert "gmail_fetch" in tools
    assert "llm_summarize" in tools
    assert "slack_post" in tools
    print("✅ Tool listing passed!")


def test_execute_dry_run():
    """Test execution in dry-run mode."""
    print_section("TEST 3: Execute Plan (Dry Run)")
    
    # Create a sample execution request
    request_data = {
        "request_id": str(uuid.uuid4()),
        "agent_instance": {
            "agent_id": "agent_001",
            "agent_type": "EMAIL_SUMMARY_AGENT",
            "config": {
                "inputs": {
                    "gmail_credentials": "mock_credentials"
                },
                "outputs": {
                    "slack_webhook": "https://hooks.slack.com/services/mock"
                }
            }
        },
        "execution_plan": {
            "plan_id": str(uuid.uuid4()),
            "agent_type": "EMAIL_SUMMARY_AGENT",
            "steps": [
                {
                    "step_id": "1",
                    "name": "Connect to Gmail",
                    "description": "Authenticate with Gmail API",
                    "tool": "gmail_auth",
                    "parameters": {}
                },
                {
                    "step_id": "2",
                    "name": "Fetch Unread Emails",
                    "description": "Retrieve unread emails from the last 30 minutes",
                    "tool": "gmail_fetch",
                    "parameters": {
                        "filter": "is:unread newer_than:30m"
                    }
                },
                {
                    "step_id": "3",
                    "name": "Summarize with LLM",
                    "description": "Generate a summary using Groq LLM",
                    "tool": "llm_summarize",
                    "parameters": {
                        "format": "text"
                    }
                },
                {
                    "step_id": "4",
                    "name": "Post to Slack",
                    "description": "Send summary to Slack channel",
                    "tool": "slack_post",
                    "parameters": {
                        "channel": "#email-summaries"
                    }
                }
            ]
        },
        "dry_run": True,
        "approved_by": "yacine",
        "approval_mode": "manual"
    }
    
    print("📤 Sending execution request (dry_run=True)...")
    print(f"Request ID: {request_data['request_id']}")
    print(f"Plan ID: {request_data['execution_plan']['plan_id']}")
    print(f"Steps: {len(request_data['execution_plan']['steps'])}")
    
    response = requests.post(
        f"{BASE_URL}/api/execute",
        json=request_data
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Execution Result:")
        print(f"   Status: {result['status']}")
        print(f"   Steps Executed: {len(result['steps'])}")
        
        print(f"\n📋 Step Results:")
        for step in result['steps']:
            status_emoji = "✅" if step['status'] == 'success' else "❌"
            print(f"   {status_emoji} Step {step['step_id']}: {step['tool']} - {step['status']}")
            if step.get('output'):
                print(f"      Output: {step['output']}")
        
        assert result['status'] in ['success', 'partial_success']
        assert len(result['steps']) == 4
        print("\n✅ Dry run execution passed!")
    else:
        print(f"❌ Error: {response.text}")
        raise AssertionError("Dry run execution failed")


def test_execute_actual():
    """Test actual execution (with mock tools)."""
    print_section("TEST 4: Execute Plan (Actual Execution)")
    
    # Create a sample execution request
    request_data = {
        "request_id": str(uuid.uuid4()),
        "agent_instance": {
            "agent_id": "agent_002",
            "agent_type": "EMAIL_SUMMARY_AGENT",
            "config": {
                "inputs": {
                    "gmail_credentials": "mock_credentials"
                },
                "outputs": {
                    "slack_webhook": "https://hooks.slack.com/services/mock"
                }
            }
        },
        "execution_plan": {
            "plan_id": str(uuid.uuid4()),
            "agent_type": "EMAIL_SUMMARY_AGENT",
            "steps": [
                {
                    "step_id": "1",
                    "name": "Connect to Gmail",
                    "description": "Authenticate with Gmail API",
                    "tool": "gmail_auth",
                    "parameters": {}
                },
                {
                    "step_id": "2",
                    "name": "Fetch Unread Emails",
                    "description": "Retrieve unread emails",
                    "tool": "gmail_fetch",
                    "parameters": {
                        "filter": "is:unread newer_than:1h"
                    }
                },
                {
                    "step_id": "3",
                    "name": "Summarize with LLM",
                    "description": "Generate a summary",
                    "tool": "llm_summarize",
                    "parameters": {}
                },
                {
                    "step_id": "4",
                    "name": "Post to Slack",
                    "description": "Send to Slack",
                    "tool": "slack_post",
                    "parameters": {
                        "channel": "#general"
                    }
                }
            ]
        },
        "dry_run": False,
        "approved_by": "yacine",
        "approval_mode": "manual"
    }
    
    print("📤 Sending execution request (dry_run=False)...")
    print(f"Request ID: {request_data['request_id']}")
    
    response = requests.post(
        f"{BASE_URL}/api/execute",
        json=request_data
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Execution Result:")
        print(f"   Status: {result['status']}")
        print(f"   Duration: {(datetime.fromisoformat(result['finished_at'].replace('Z', '+00:00')) - datetime.fromisoformat(result['created_at'].replace('Z', '+00:00'))).total_seconds():.2f}s")
        
        print(f"\n📋 Step Results:")
        for step in result['steps']:
            status_emoji = "✅" if step['status'] == 'success' else "❌"
            duration = (datetime.fromisoformat(step['ended_at'].replace('Z', '+00:00')) - datetime.fromisoformat(step['started_at'].replace('Z', '+00:00'))).total_seconds()
            print(f"   {status_emoji} Step {step['step_id']}: {step['tool']} ({duration:.3f}s)")
        
        # Check final context
        if result.get('context'):
            print(f"\n📦 Final Context Keys: {list(result['context'].keys())}")
            
            # Show summary if available
            if 'summary_text' in result['context']:
                print(f"\n📝 Generated Summary:")
                print(result['context']['summary_text'])
        
        assert result['status'] == 'success'
        assert len(result['steps']) == 4
        assert all(step['status'] == 'success' for step in result['steps'])
        print("\n✅ Actual execution passed!")
    else:
        print(f"❌ Error: {response.text}")
        raise AssertionError("Actual execution failed")


def test_execute_with_error():
    """Test execution with a non-existent tool (error handling)."""
    print_section("TEST 5: Execute Plan with Error (Unknown Tool)")
    
    request_data = {
        "request_id": str(uuid.uuid4()),
        "agent_instance": {
            "agent_id": "agent_003",
            "agent_type": "TEST_AGENT"
        },
        "execution_plan": {
            "plan_id": str(uuid.uuid4()),
            "agent_type": "TEST_AGENT",
            "steps": [
                {
                    "step_id": "1",
                    "name": "Unknown Tool",
                    "description": "This tool doesn't exist",
                    "tool": "unknown_tool",
                    "parameters": {}
                }
            ]
        },
        "dry_run": False,
        "approved_by": "yacine"
    }
    
    print("📤 Sending execution request with unknown tool...")
    
    response = requests.post(
        f"{BASE_URL}/api/execute",
        json=request_data
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Execution Result:")
        print(f"   Status: {result['status']}")
        
        # Should have failed
        assert result['status'] == 'failed'
        assert len(result['steps']) == 1
        assert result['steps'][0]['status'] == 'failed'
        
        error = result['steps'][0]['error']
        print(f"\n❌ Expected Error Caught:")
        print(f"   Type: {error['type']}")
        print(f"   Message: {error['message']}")
        
        print("\n✅ Error handling test passed!")
    else:
        print(f"❌ Unexpected error: {response.text}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  EXECUTION SERVICE API TESTS")
    print("="*70)
    print("\nMake sure the API server is running on http://localhost:8000")
    print("Run: python run_api.py")
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: List tools
        test_list_tools()
        
        # Test 3: Dry run execution
        test_execute_dry_run()
        
        # Test 4: Actual execution
        test_execute_actual()
        
        # Test 5: Error handling
        test_execute_with_error()
        
        print_section("ALL TESTS PASSED! ✅")
        print("The Execution Service is working correctly!")
        print("\n🎉 Agent 4 - Executor is ready to use!")
        
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
