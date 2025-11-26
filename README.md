# 🤖 Multi-Agent System

A modular, production-ready multi-agent orchestration system built with Python and FastAPI.

## 🎯 Overview

This system implements a complete pipeline of specialized agents that work together to interpret user requests, generate execution plans, validate them, and execute actions using various tools (Gmail, Slack, LLM, etc.).

### Architecture

```
User Input → Chat → Interpretation → Orchestration → Debug → Execution → Results
```

## 🏗️ System Components

| Agent | Purpose | Status |
|-------|---------|--------|
| **Agent 1 - Chat** | User interaction and conversation management | ✅ Complete |
| **Agent 2 - Interpretation** | Natural language understanding and intent extraction | ✅ Complete |
| **Agent 3 - Orchestrator** | Plan generation and tool selection | ✅ Complete |
| **Agent Debugger** | Static validation and error detection | ✅ Complete |
| **Agent 4 - Executor** | Step-by-step plan execution | ✅ Complete |

## 📁 Project Structure

```
Multi_agent/
├── chat_service/              # Agent 1 - Chat Service
│   ├── domain/               # Domain models
│   ├── interfaces/           # Port abstractions
│   ├── infrastructure/       # Adapters (LLM, storage)
│   ├── application/          # Business logic
│   └── api/                  # HTTP endpoints
│
├── interpretation_service/    # Agent 2 - Interpretation
│   ├── domain/
│   ├── interfaces/
│   ├── infrastructure/
│   ├── core/
│   └── api/
│
├── orchestrator_service/      # Agent 3 - Orchestrator
│   ├── domain/
│   ├── core/
│   └── api/
│
├── debug_service/             # Agent Debugger
│   ├── domain/
│   ├── core/
│   └── api/
│
├── execution_service/         # Agent 4 - Executor
│   ├── domain/
│   ├── interfaces/
│   ├── infrastructure/
│   │   ├── tools/           # Gmail, Slack, LLM tools
│   │   └── state/           # State management
│   ├── core/                # Execution engine
│   └── api/
│
├── tests/                     # All test scripts
├── run_api.py                # Main application entry point
├── ETAT_SYSTEME.md           # System status documentation
├── ROADMAP_V2.md             # V2 development roadmap
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Multi_agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env with your configuration
```

### Running the System

```bash
# Start the API server
python run_api.py
```

The server will start on `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

All test scripts are located in the `tests/` directory.

```bash
# Run complete system diagnostic
python tests/diagnostic_complete.py

# Run end-to-end test
python tests/test_end_to_end.py

# Run individual service tests
python tests/test_chat_api.py
python tests/test_orchestrator_api.py
python tests/test_debug_service.py
python tests/test_execution_api.py
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

## 📖 Documentation

- **[ETAT_SYSTEME.md](ETAT_SYSTEME.md)** - Current system status, what's implemented, and what's missing
- **[ROADMAP_V2.md](ROADMAP_V2.md)** - Detailed V2 development roadmap with priorities
- **[tests/README.md](tests/README.md)** - Testing documentation

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# LLM Configuration
GROQ_API_KEY=your_groq_api_key_here

# Gmail Configuration (for V2)
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret

# Slack Configuration (for V2)
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

## 🏛️ Architecture Principles

This project follows **Hexagonal Architecture** (Ports & Adapters):

- **Domain**: Core business models and logic
- **Interfaces**: Port abstractions (protocols)
- **Infrastructure**: Concrete adapters (Gmail, Slack, LLM)
- **Application/Core**: Use cases and orchestration
- **API**: HTTP endpoints (FastAPI)

### Benefits

- ✅ **Testability**: Easy to mock dependencies
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Flexibility**: Easy to swap implementations
- ✅ **Scalability**: Independent service scaling

## 🔄 Development Workflow

### Current Status (V1)

✅ All agents implemented and functional  
✅ Complete pipeline working with mock tools  
✅ Comprehensive test coverage  
⚠️ Using mock integrations (Gmail, Slack, LLM)

### Next Steps (V2)

See [ROADMAP_V2.md](ROADMAP_V2.md) for detailed V2 plan:

1. **Real Integrations** - Gmail API, Groq LLM, Slack API
2. **Secret Management** - Secure credential handling
3. **Persistence** - Database for execution history
4. **Correlation ID** - End-to-end request tracing
5. **Error Policies** - Retry, continue, stop strategies

## 🤝 Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public APIs
- Keep functions focused and small

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: description of changes"

# Push and create PR
git push origin feature/your-feature-name
```

### Commit Message Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/tooling changes

## 📊 System Status

**Version**: 1.0.0 (POC)  
**Status**: ✅ Functional with mock tools  
**Production Ready**: ⚠️ Requires real integrations

For detailed status, see [ETAT_SYSTEME.md](ETAT_SYSTEME.md)

## 📝 License

[Your License Here]

## 👥 Authors

[Your Name/Team]

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Groq for LLM capabilities
- Pydantic for data validation

---

**Need Help?** Check the documentation or open an issue.
