# OpenClaw Gateway Startup Guide

## 🚀 How to Start OpenClaw

OpenClaw requires user authentication before starting. Follow these steps:

### Step 1: Access the Application
Go to: **https://model-exchange-2.preview.emergentagent.com**

(Or your custom domain when www.nexussocialmarket.com is configured)

### Step 2: Sign In with Google
1. Click the **"Sign in with Google"** button
2. Authorize with your Google account
3. This creates your user session and locks the instance to your account

### Step 3: Start OpenClaw Gateway
After signing in, you'll see the Setup page with:
- Provider choice (Emergent/OpenAI/Anthropic)
- **"Start OpenClaw"** button

**Choose a provider:**

**Option A: Emergent (Recommended)**
- ✅ No API key needed
- ✅ Uses the universal Emergent LLM key
- ✅ Access to multiple models (GPT, Claude, Gemini)
- ✅ Works immediately

**Option B: OpenAI**
- Requires your OpenAI API key
- Direct access to OpenAI models

**Option C: Anthropic**
- Requires your Anthropic API key
- Direct access to Claude models

### Step 4: Verify It's Running
Once started, you can:
- Check status at: `/api/openclaw/status`
- Monitor health at: `/maintenance` dashboard
- Use the OpenClaw Control UI

---

## 🔧 Starting OpenClaw via API (After Authentication)

If you're already authenticated, you can start OpenClaw via API:

```bash
# Get your session cookie first by signing in through the browser

# Start with Emergent provider (no API key needed)
curl -X POST "https://model-exchange-2.preview.emergentagent.com/api/openclaw/start" \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -d '{"provider": "emergent"}'

# Start with OpenAI provider (requires API key)
curl -X POST "https://model-exchange-2.preview.emergentagent.com/api/openclaw/start" \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -d '{"provider": "openai", "apiKey": "sk-..."}'

# Start with Anthropic provider (requires API key)
curl -X POST "https://model-exchange-2.preview.emergentagent.com/api/openclaw/start" \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -d '{"provider": "anthropic", "apiKey": "sk-ant-..."}'
```

---

## 📊 Verify OpenClaw Status

### Via API:
```bash
curl https://model-exchange-2.preview.emergentagent.com/api/openclaw/status
```

**Expected Response (when running):**
```json
{
  "running": true,
  "pid": 12345,
  "provider": "emergent",
  "started_at": "2026-04-02T01:30:00Z",
  "controlUrl": "http://localhost:18791",
  "owner_user_id": "user@example.com",
  "is_owner": true
}
```

### Via O&M Dashboard:
Visit: **https://model-exchange-2.preview.emergentagent.com/maintenance**

You'll see:
- ✅ OpenClaw Gateway: **healthy** (green) when running
- 🔵 OpenClaw Gateway: **info** (blue) when stopped

---

## 🛠️ Troubleshooting

### Issue: "Not authenticated" error
**Solution:** Sign in with Google first at the main app page

### Issue: Gateway won't start
**Check:**
1. Supervisor logs: `tail -50 /var/log/supervisor/openclaw-gateway.err.log`
2. Backend logs: `tail -50 /var/log/supervisor/backend.err.log`
3. Ensure Emergent API key is set in `/app/backend/.env`

### Issue: Gateway crashes immediately
**Check:**
1. Provider credentials are valid
2. Emergent API key has balance (for Emergent provider)
3. OpenAI/Anthropic keys are correct (for those providers)

---

## 🎯 Next Steps After Starting

Once OpenClaw is running:

1. **Access Control UI**: Navigate to the control URL shown in status
2. **Monitor Performance**: Check `/maintenance` dashboard for health metrics
3. **View Logs**: Check supervisor logs for any issues
4. **Test Functionality**: Try a simple coding task through OpenClaw

---

## 🔄 Stopping/Restarting OpenClaw

### Via API:
```bash
curl -X POST "https://model-exchange-2.preview.emergentagent.com/api/openclaw/stop" \
  -H "Cookie: session_id=YOUR_SESSION_ID"
```

### Via Supervisor:
```bash
sudo supervisorctl stop openclaw-gateway
sudo supervisorctl start openclaw-gateway
```

---

## 📈 Monitoring

The O&M Dashboard (`/maintenance`) automatically monitors:
- ✅ Gateway running status
- ✅ Process PID
- ✅ Provider in use
- ✅ Uptime tracking
- ✅ Health checks every 30 seconds

---

**For assistance, check the troubleshooting section or create a work order in the O&M dashboard!**
