# 🚀 Quick Start Guide - Nexus AI & OpenClaw

## ⚡ Fast Start (3 Steps)

### **Step 1: Access the Application**
Open in browser:
```
https://model-exchange-2.preview.emergentagent.com
```

### **Step 2: Sign In with Google**
- Click "Sign in with Google" button
- Authorize with your Google account
- This creates your user session

### **Step 3: Start OpenClaw**
On the Setup page:
1. Choose provider: **Emergent** (recommended - no API key needed)
2. Click **"Start OpenClaw"** button
3. Wait 10-20 seconds for gateway to start

✅ **Done!** OpenClaw is now running.

---

## 📍 Quick Links

| Page | URL | Description |
|------|-----|-------------|
| **Main App** | `/` | Setup & Start OpenClaw |
| **OpenClaw Info** | `/openclaw-info` | Capabilities & GitHub stats |
| **O&M Dashboard** | `/maintenance` | System health & diagnostics |

---

## 🔧 Provider Options

### **Option A: Emergent (Recommended)** ✅
- ✅ No API key required
- ✅ Access to GPT-5.2, Claude 4, Gemini 2.5 Pro
- ✅ Works immediately
- ✅ Pay-as-you-go via Emergent LLM Key

### **Option B: OpenAI**
- ⚠️ Requires your OpenAI API key
- Direct access to OpenAI models

### **Option C: Anthropic**
- ⚠️ Requires your Anthropic API key
- Direct access to Claude models

---

## 🎯 What You Can Do

Once OpenClaw is running:

### **1. AI Assistant Tasks**
- Code generation and editing
- Multi-file refactoring
- Document analysis
- Image/vision tasks
- Browser automation

### **2. Smart LLM Routing**
- Automatic cost optimization with ERNIE 5.0 (99% savings)
- Fallback to Emergent for premium tasks
- Task-based routing (coding, reasoning, multimodal)

### **3. Multimodal AI**
- Text-to-Speech (Coqui TTS)
- Speech-to-Text (Whisper)
- Vision/Image analysis (CLIP)

### **4. System Monitoring**
- Real-time health checks
- Hardware diagnostics
- Work order tracking
- WhatsApp integration status

---

## 🧪 Test Your Setup

### **Test 1: Check OpenClaw Status**
```bash
curl https://model-exchange-2.preview.emergentagent.com/api/openclaw/status
```

### **Test 2: View Capabilities**
Navigate to: `/openclaw-info`

### **Test 3: Check System Health**
Navigate to: `/maintenance`

---

## 🆘 Troubleshooting

### **Problem: Gateway Won't Start**
**Solutions:**
1. Refresh the page and try again
2. Check you're signed in with Google
3. Verify you selected a provider (Emergent recommended)

### **Problem: "Not Authenticated" Error**
**Solution:** Click "Sign in with Google" on the main page first

### **Problem: Gateway Crashed**
**Solution:** Supervisor auto-restarts. Wait 10 seconds and check status again.

---

## 📊 API Quick Reference

All endpoints require authentication (session cookie from Google sign-in).

### **OpenClaw Control:**
```bash
# Start gateway
POST /api/openclaw/start
Body: {"provider": "emergent"}

# Stop gateway
POST /api/openclaw/stop

# Check status
GET /api/openclaw/status

# Health check
GET /api/openclaw/health
```

### **Smart LLM:**
```bash
# Chat completion (auto-routed)
POST /api/llm/chat
Body: {
  "messages": [{"role": "user", "content": "Hello"}],
  "task_type": "general",
  "budget": "low"
}

# Provider status
GET /api/llm/providers/status

# Cost calculator
GET /api/llm/cost/calculator?tokens=10000000
```

### **Multimodal AI:**
```bash
# Text-to-Speech
POST /api/multimodal/tts
Body: {"text": "Hello world"}

# Speech-to-Text
POST /api/multimodal/stt
Body: {"audio": "<base64>"}

# Vision analysis
POST /api/multimodal/vision
Body: {"image": "<url or base64>"}
```

---

## 🎨 Features Overview

### **✅ Implemented:**
- Google OAuth authentication
- Multi-provider OpenClaw gateway
- ERNIE 5.0 smart LLM routing (99% cost savings)
- InclusionAI multimodal (TTS, STT, Vision)
- O&M diagnostics dashboard
- WhatsApp business integration
- 60+ hybrid autonomous services
- Real-time health monitoring

### **📋 Coming Soon:**
- atoms.dev integrations
- Advanced analytics
- Automated investor packages
- Custom domain (Cloudflare)

---

## 📞 Support

**For Issues:**
1. Check `/maintenance` dashboard for diagnostics
2. View backend logs: `tail -f /var/log/supervisor/backend.err.log`
3. View gateway logs: `tail -f /var/log/supervisor/openclaw-gateway.err.log`

**For Questions:**
- Check `/openclaw-info` for capabilities and documentation
- Review integration guides in `/app/` directory

---

## 🎯 Next Steps

1. ✅ Sign in with Google
2. ✅ Start OpenClaw with Emergent provider
3. ✅ Explore `/openclaw-info` dashboard
4. ✅ Check `/maintenance` for system health
5. ✅ Try smart LLM routing with ERNIE 5.0
6. ✅ Test multimodal AI features

---

**Ready to build with AI? Start now!** 🚀

*Last updated: April 2, 2026*
