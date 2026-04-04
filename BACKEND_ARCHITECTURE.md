# Nexus AI Social Marketplace - Backend Architecture

## 📁 Project Structure

```
/app/backend/
├── models/                    # Pydantic models & schemas
│   ├── __init__.py           # Model exports
│   └── schemas.py            # API request/response models
│
├── routes/                    # API route handlers
│   ├── llm_router.py         # ERNIE 5.0 Smart LLM routing
│   ├── maintenance_router.py # O&M diagnostics & monitoring
│   ├── multimodal_router.py  # InclusionAI TTS/STT/Vision
│   └── openclaw_router.py    # Enhanced OpenClaw integration
│
├── services/                  # Business logic & integrations
│   ├── llm_providers/        # LLM provider implementations
│   │   ├── ernie.py          # Baidu ERNIE 5.0 integration
│   │   ├── emergent.py       # Emergent Universal Key
│   │   └── smart_router.py   # Smart routing logic
│   ├── nexus_maintenance/    # O&M system diagnostics
│   ├── inclusionai/          # Multimodal AI services
│   └── openclaw_integration.py # OpenClaw task management
│
├── tests/                     # Unit & integration tests
│   └── (test files)
│
├── server.py                  # Main FastAPI application (1359 lines)
├── gateway_config.py          # OpenClaw gateway configuration
├── supervisor_client.py       # Supervisor process management
└── whatsapp_monitor.py        # WhatsApp connection monitoring
```

---

## 🎯 Key Components

### **1. API Routes** (`/routes/`)

#### **LLM Router** (`llm_router.py`)
- Smart LLM routing with ERNIE 5.0 cost optimization
- Multi-provider support (ERNIE, Emergent)
- Endpoints: `/api/llm/*`

#### **Maintenance Router** (`maintenance_router.py`)
- Limble-style O&M diagnostics
- System health monitoring
- Work order management
- Endpoints: `/api/maintenance/*`

#### **Multimodal Router** (`multimodal_router.py`)
- InclusionAI TTS (Coqui)
- Whisper STT
- CLIP Vision analysis
- Endpoints: `/api/multimodal/*`

#### **OpenClaw Router** (`openclaw_router.py`)
- Enhanced OpenClaw APIs
- GitHub integration data
- Health monitoring
- Endpoints: `/api/openclaw/*`

---

### **2. Services** (`/services/`)

#### **LLM Providers** (`llm_providers/`)
- **ERNIE Provider**: Baidu ERNIE 5.0 integration (99% cost savings vs GPT-4)
- **Emergent Provider**: Universal LLM key (GPT-5.2, Claude 4, Gemini 2.5)
- **Smart Router**: Intelligent routing based on task type & budget

#### **Nexus Maintenance** (`nexus_maintenance/`)
- System diagnostics (`psutil`)
- Hardware health monitoring
- Work order tracking

#### **InclusionAI** (`inclusionai/`)
- Text-to-Speech (Coqui TTS)
- Speech-to-Text (Whisper)
- Vision analysis (CLIP)

#### **OpenClaw Integration** (`openclaw_integration.py`)
- Task manager (async task tracking)
- Health monitoring
- High-level API methods

---

### **3. Models** (`/models/`)

Pydantic schemas for type safety and validation:
- `StatusCheck`, `StatusCheckCreate`
- `OpenClawStartRequest`, `OpenClawStartResponse`, `OpenClawStatusResponse`
- `User`, `SessionRequest`

---

### **4. Core Application** (`server.py`)

**Main FastAPI app** (1359 lines) containing:
- MongoDB connection setup
- Authentication system (Google OAuth via Emergent)
- Session management
- OpenClaw gateway management
- Hybrid autonomous services (60+)
- WebSocket handlers
- CORS middleware

**Key Features:**
- Multi-provider LLM routing
- Supervisor-managed OpenClaw gateway
- WhatsApp business integration
- Real-time monitoring
- Per-user authentication & access control

---

## 🔧 Configuration Files

- `.env` - Environment variables (MongoDB, API keys)
- `requirements.txt` - Python dependencies
- `supervisor.conf` - Process management (via Supervisor)

---

## 🚀 API Endpoints

### **Authentication**
- `POST /api/auth/session` - Create/validate session
- `GET /api/auth/user` - Get current user
- `GET /api/auth/instance-owner` - Get instance owner

### **OpenClaw Gateway**
- `POST /api/openclaw/start` - Start gateway
- `POST /api/openclaw/stop` - Stop gateway
- `GET /api/openclaw/status` - Gateway status
- `GET /api/openclaw/health` - Health check
- `GET /api/openclaw/capabilities` - AI capabilities
- `GET /api/openclaw/features` - Integration features
- `GET /api/openclaw/github-info` - GitHub repo stats

### **Smart LLM Routing**
- `POST /api/llm/chat` - Smart chat completion
- `POST /api/llm/providers/ernie/chat` - Direct ERNIE 5.0
- `POST /api/llm/providers/emergent/chat` - Direct Emergent
- `GET /api/llm/providers/status` - Provider status
- `GET /api/llm/routing/rules` - Routing rules
- `GET /api/llm/cost/comparison` - Cost comparison
- `GET /api/llm/cost/calculator` - Cost calculator

### **Multimodal AI**
- `POST /api/multimodal/tts` - Text-to-Speech
- `POST /api/multimodal/stt` - Speech-to-Text
- `POST /api/multimodal/vision` - Image analysis
- `GET /api/multimodal/status` - Service status

### **Maintenance & Diagnostics**
- `GET /api/maintenance/health` - System health
- `POST /api/maintenance/work-orders` - Create work order
- `GET /api/maintenance/work-orders` - List work orders

---

## 🗄️ Database (MongoDB)

**Collections:**
- `users` - User accounts (Google OAuth)
- `sessions` - Active sessions
- `instance_config` - Instance ownership
- `moltbot_configs` - OpenClaw gateway config
- `status_checks` - Health check history
- `work_orders` - O&M work orders

---

## 🔐 Security

- **Authentication**: Google OAuth via Emergent
- **Session Management**: 7-day expiry
- **Instance Locking**: Per-user gateway ownership
- **API Keys**: Stored in `.env`, never hardcoded
- **CORS**: Configurable origins

---

## 📊 Integrations

### **External Services:**
- **ERNIE 5.0** (Baidu) - Cost-optimized LLM
- **Emergent Universal Key** - Multi-LLM access
- **OpenClaw** - AI assistant gateway
- **WhatsApp Business** - Messaging integration
- **Cloudflare** - DNS & CDN (pending custom domain)

### **Internal Services:**
- **Supervisor** - Process lifecycle management
- **MongoDB** - Data persistence
- **Nginx** (Kubernetes) - Reverse proxy

---

## 🧪 Testing

Located in `/app/backend/tests/`:
- Unit tests for routes
- Integration tests for services
- End-to-end API tests

**Run tests:**
```bash
pytest /app/backend/tests/
```

---

## 📝 Development Guidelines

### **Adding New Routes:**
1. Create router in `/app/backend/routes/`
2. Define Pydantic models in `/app/backend/models/schemas.py`
3. Implement business logic in `/app/backend/services/`
4. Include router in `server.py`
5. Add tests in `/app/backend/tests/`

### **Code Style:**
- Use type hints
- Follow PEP 8
- Document with docstrings
- Lint with `ruff`

### **Best Practices:**
- Never hardcode URLs or API keys
- Use `.env` for configuration
- Implement proper error handling
- Log important events
- Write comprehensive tests

---

## 🔄 Process Management

**Supervisor manages:**
- `backend` - FastAPI application (port 8001)
- `frontend` - React application (port 3000)
- `openclaw-gateway` - OpenClaw gateway (port 18789)

**Commands:**
```bash
# Check status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart openclaw-gateway
```

---

## 📚 Documentation

- `/app/OPENCLAW_INTEGRATION_COMPLETE.md` - OpenClaw integration guide
- `/app/OPENCLAW_STARTUP_GUIDE.md` - User startup guide
- `/app/NEXUS_OM_INTEGRATION_PLAN.md` - O&M integration plan
- `/app/ERNIE_5_INTEGRATION_PLAN.md` - ERNIE 5.0 integration
- `/app/BACKEND_ARCHITECTURE.md` - This file

---

## 🎯 Roadmap

**Completed:**
- ✅ OpenClaw enhanced integration
- ✅ ERNIE 5.0 smart routing
- ✅ InclusionAI multimodal
- ✅ O&M diagnostics dashboard
- ✅ Directory structure refactoring

**In Progress:**
- 🔄 Code modularization (server.py → smaller modules)

**Planned:**
- 📋 atoms.dev integration
- 📋 Comprehensive unit testing
- 📋 Automated investor package generation
- 📋 Advanced analytics dashboard

---

**Last Updated:** April 2, 2026  
**Total Backend LOC:** ~5000+ lines  
**Active Integrations:** 10+  
**Autonomous Services:** 60+
