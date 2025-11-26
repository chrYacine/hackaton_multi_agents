# Tests Directory

This directory contains all test scripts and test outputs for the Multi-Agent System.

## Test Scripts

### Integration Tests
- `test_end_to_end.py` - Complete pipeline test (Chat → Interpretation → Orchestrator → Debug → Execution)
- `diagnostic_complete.py` - Full system diagnostic with gap analysis

### Service-Specific Tests
- `test_chat_api.py` - Agent 1 (Chat Service) tests
- `test_chat_flow.py` - Chat conversation flow tests
- `test_chat_model.py` - Chat model tests
- `test_orchestrator.py` - Agent 3 (Orchestrator) tests
- `test_orchestrator_api.py` - Orchestrator API tests
- `test_debug_service.py` - Debug Service tests
- `test_execution_api.py` - Agent 4 (Execution Service) tests

### Utility Tests
- `test_api_endpoint.py` - Generic API endpoint tests
- `test_api_script.py` - API testing utilities
- `test_provider_init.py` - Provider initialization tests

### Verification Scripts
- `verify_api.py` - API verification
- `verify_orchestrator_user.py` - Orchestrator user flow verification

### Debug Scripts
- `debug_api.py` - API debugging utilities
- `debug_settings.py` - Debug configuration

## Test Outputs

All test output files (`*_output*.txt`, `*.log`) are automatically ignored by git.

## Running Tests

### Prerequisites
Make sure the API server is running:
```bash
python run_api.py
```

### Run All Tests
```bash
# Complete diagnostic
python tests/diagnostic_complete.py

# End-to-end test
python tests/test_end_to_end.py
```

### Run Individual Service Tests
```bash
# Test Chat Service
python tests/test_chat_api.py

# Test Orchestrator
python tests/test_orchestrator_api.py

# Test Debug Service
python tests/test_debug_service.py

# Test Execution Service
python tests/test_execution_api.py
```

## Test Coverage

| Service | Test File | Status |
|---------|-----------|--------|
| Agent 1 - Chat | `test_chat_api.py` | ✅ |
| Agent 2 - Interpretation | (integrated in end-to-end) | ✅ |
| Agent 3 - Orchestrator | `test_orchestrator_api.py` | ✅ |
| Agent Debugger | `test_debug_service.py` | ✅ |
| Agent 4 - Executor | `test_execution_api.py` | ✅ |
| End-to-End Pipeline | `test_end_to_end.py` | ✅ |

## Notes

- All tests use mock data and mock tools (Gmail, Slack, LLM)
- For production testing with real APIs, see `ROADMAP_V2.md` Phase 1
- Test outputs are excluded from version control via `.gitignore`
