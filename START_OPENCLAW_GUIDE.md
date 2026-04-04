# 🚀 START OPENCLAW - Step-by-Step Guide

## 📍 **Your Public URL**
```
https://model-exchange-2.preview.emergentagent.com
```

---

## ✅ **STEP-BY-STEP INSTRUCTIONS**

### **Step 1: Open the Application**

Open your browser and navigate to:
```
https://model-exchange-2.preview.emergentagent.com
```

You'll see the **OpenClaw Setup** page with:
- 🦞 OpenClaw logo
- "Sign in with Google" button
- Message: "Sign in with Google to configure and access your personal OpenClaw instance."

---

### **Step 2: Sign In with Google**

1. Click the **"Sign in with Google"** button
2. You'll be redirected to Google's authentication page
3. Choose your Google account
4. Authorize the application
5. You'll be redirected back to the OpenClaw setup page

**What happens:**
- Your session is created and secured
- The instance is locked to your account
- You gain access to all OpenClaw features

---

### **Step 3: Configure OpenClaw**

After signing in, you'll see the **provider selection page**:

**Provider Options:**

**Option A: Emergent (Recommended)** ✅
- ✅ **No API key required**
- ✅ Access to GPT-5.2, Claude 4, Gemini 2.5 Pro
- ✅ Works immediately
- ✅ Pay-as-you-go via Emergent LLM Key
- ✅ **SELECT THIS ONE**

**Option B: OpenAI**
- Requires your OpenAI API key
- Direct access to OpenAI models

**Option C: Anthropic**
- Requires your Anthropic API key
- Direct access to Claude models

**For most users: Choose "Emergent"**

---

### **Step 4: Start OpenClaw**

1. Select provider: **Emergent**
2. Click **"Start OpenClaw"** button
3. Wait 10-20 seconds for the gateway to initialize
4. You'll see a success message

**What happens behind the scenes:**
- OpenClaw gateway starts on port 18789
- Control UI becomes available on port 18791
- Supervisor manages the process (auto-restart on crash)
- Your session token is configured
- The gateway connects to Emergent's LLM services

---

### **Step 5: Verify It's Running**

**Method 1: Check Status via API**
```bash
curl https://model-exchange-2.preview.emergentagent.com/api/openclaw/status
```

**Expected Response:**
```json
{
  "running": true,
  "pid": 12345,
  "provider": "emergent",
  "started_at": "2026-04-02T06:13:00Z",
  "controlUrl": "/api/openclaw/ui/",
  "owner_user_id": "your-email@gmail.com",
  "is_owner": true
}
```

**Method 2: Visit O&M Dashboard**
Navigate to: `https://model-exchange-2.preview.emergentagent.com/maintenance`

You should see:
- ✅ OpenClaw Gateway: **healthy** (green status)
- Process ID (PID)
- Provider: emergent
- Uptime

**Method 3: Visit OpenClaw Info**
Navigate to: `https://model-exchange-2.preview.emergentagent.com/openclaw-info`

You should see:
- Gateway status badge (green)
- GitHub stats (345k+ stars)
- Capabilities grid
- Health monitoring

---

## 🎯 **What You Can Do Now**

Once OpenClaw is running, you have access to:

### **1. AI Assistant Features**
- Code generation and editing
- Multi-file refactoring
- Git operations
- Test generation
- Code review and optimization

### **2. Multimodal AI**
- Text-to-Speech (Coqui TTS)
- Speech-to-Text (Whisper)
- Vision/Image analysis (CLIP)
- Document processing

### **3. Smart LLM Routing**
- ERNIE 5.0 for cost optimization (99% savings vs GPT-4)
- Automatic task-based routing
- Multi-provider fallback

### **4. System Management**
- Real-time health monitoring
- Work order tracking
- WhatsApp integration
- System diagnostics

---

## 🧪 **Test Your Setup**

### **Test 1: Quick API Test**
```bash
# Check capabilities
curl https://model-exchange-2.preview.emergentagent.com/api/openclaw/capabilities

# Check health
curl https://model-exchange-2.preview.emergentagent.com/api/openclaw/health

# Check GitHub info
curl https://model-exchange-2.preview.emergentagent.com/api/openclaw/github-info
```

### **Test 2: Smart LLM Chat**
```bash
curl -X POST https://model-exchange-2.preview.emergentagent.com/api/llm/chat \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, test message"}],
    "task_type": "general",
    "budget": "low"
  }'
```

### **Test 3: Multimodal TTS**
```bash
curl -X POST https://model-exchange-2.preview.emergentagent.com/api/multimodal/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from OpenClaw!"}'
```

---

## 🆘 **Troubleshooting**

### **Problem: "Sign in with Google" button doesn't work**
**Solution:**
- Ensure you're using the public URL (not localhost)
- Check browser console for errors
- Try a different browser or incognito mode

### **Problem: Gateway fails to start**
**Solution:**
1. Check backend logs:
   ```bash
   tail -f /var/log/supervisor/backend.err.log
   ```
2. Check gateway logs:
   ```bash
   tail -f /var/log/supervisor/openclaw-gateway.err.log
   ```
3. Restart backend:
   ```bash
   sudo supervisorctl restart backend
   ```

### **Problem: "Not authenticated" error**
**Solution:**
- Sign in with Google first
- Session might have expired (7-day expiry)
- Re-authenticate by signing in again

### **Problem: Gateway shows "offline" status**
**Solution:**
1. Refresh the page
2. Wait 10 seconds (might still be starting)
3. Check supervisor status:
   ```bash
   sudo supervisorctl status openclaw-gateway
   ```
4. Manually restart:
   ```bash
   sudo supervisorctl restart openclaw-gateway
   ```

---

## 📊 **Current System Status**

- ✅ **Backend**: Running (pid 42, uptime 10+ min)
- ✅ **Frontend**: Running (pid 44, uptime 10+ min)
- ✅ **MongoDB**: Connected (6 active connections)
- ✅ **Public URL**: `https://model-exchange-2.preview.emergentagent.com`
- 🔵 **OpenClaw**: Ready to start (awaiting your authentication)

---

## 🎯 **Summary - Quick Start**

**3 Simple Steps:**

1. **Visit**: https://model-exchange-2.preview.emergentagent.com
2. **Click**: "Sign in with Google"
3. **Select**: Emergent provider → Click "Start OpenClaw"

**That's it!** 🎉

---

## 📞 **Need Help?**

**Check Status:**
- O&M Dashboard: `/maintenance`
- OpenClaw Info: `/openclaw-info`
- API Status: `/api/openclaw/status`

**View Logs:**
```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Gateway
tail -f /var/log/supervisor/openclaw-gateway.err.log

# Frontend
tail -f /var/log/supervisor/frontend.err.log
```

**Restart Services:**
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart openclaw-gateway
```

---

## ✅ **You're All Set!**

Your Nexus AI Social Marketplace is ready with:
- ✅ Enhanced OpenClaw integration
- ✅ ERNIE 5.0 Smart LLM routing
- ✅ Multimodal AI capabilities
- ✅ Real-time monitoring
- ✅ 60+ hybrid autonomous services

**Start building with AI now!** 🚀

*Last updated: April 2, 2026*
