# 🚀 Quick Start Checklist for www.nexussocialmarket.com

## Current Status: ✅ App Running | ⏳ Domain Pending | 🔴 OpenClaw Not Started

---

## Step 1: Link Domain (IN PROGRESS - YOU'RE DOING THIS NOW!)
**Time:** 10-20 minutes

### What to Do:
1. ✅ Open Emergent Dashboard: https://app.emergentagent.com
2. ✅ Find your app (OpenClaw Hosting)
3. ✅ Click "Link Domain"
4. ✅ Enter: `www.nexussocialmarket.com`
5. ✅ Choose "Use Entri"
6. ⏳ Wait 10-15 minutes for DNS propagation

### How to Verify:
```bash
# Test in browser (after 10-15 minutes):
https://www.nexussocialmarket.com

# Should show: OpenClaw Setup page with Google sign-in
```

---

## Step 2: Start OpenClaw Gateway
**Time:** 2 minutes  
**Status:** 🔴 Not Started (waiting for you to sign in)

### What to Do:
1. Visit: https://www.nexussocialmarket.com (or model-exchange-2.preview.emergentagent.com)
2. Click "Sign in with Google"
3. Authorize with your Google account
4. You'll see the Setup page with:
   - Provider choice (Emergent/OpenAI/Anthropic)
   - "Start OpenClaw" button
5. Click "Start OpenClaw"
6. Choose provider: **"Emergent"** (uses universal key - no API key needed)

### What Happens:
- OpenClaw gateway starts running in the background
- You get access to the Control UI
- WhatsApp integration becomes available
- AI coding assistant is ready

---

## Step 3: Verify Everything Works
**Time:** 5 minutes

### Backend API Test:
```bash
curl https://www.nexussocialmarket.com/api/
# Expected: {"message":"OpenClaw Hosting API"}
```

### OpenClaw Status Check:
```bash
curl https://www.nexussocialmarket.com/api/openclaw/status
# Expected: {"running": true, "provider": "emergent", ...}
```

### Frontend Access:
- Browser: https://www.nexussocialmarket.com
- Should show: OpenClaw Control UI (if started) or Setup page

---

## Step 4: Optional Cleanup
**Time:** 2 minutes

### Remove Conflicting Cloudflare DNS (if domain linking worked):
1. Go to: https://dash.cloudflare.com
2. Select: nexussocialmarket.com
3. DNS → Records
4. Find: www CNAME record
5. Delete it (Emergent now handles DNS)

**OR** keep it and set to "DNS only" (grey cloud) as backup

---

## 📊 Current Configuration

### App Details:
- **Platform:** OpenClaw Hosting (Moltbot Gateway)
- **Current URL:** https://model-exchange-2.preview.emergentagent.com
- **Target URL:** https://www.nexussocialmarket.com
- **Backend:** FastAPI (running ✅)
- **Frontend:** React (running ✅)
- **Database:** MongoDB (running ✅)

### Authentication:
- **Method:** Emergent Google OAuth
- **Instance Locking:** First user to sign in becomes owner
- **Session:** 7-day cookie-based

### OpenClaw Status:
- **Installed:** ✅ Yes
- **Running:** ❌ No (waiting for user to start)
- **Provider:** None (not configured yet)
- **WhatsApp:** Not linked

---

## 🎯 What's Next After Setup?

### Immediate (Today):
1. ✅ Link domain → www.nexussocialmarket.com
2. ✅ Sign in with Google
3. ✅ Start OpenClaw gateway

### Short-term (This Week):
1. Test all API endpoints
2. Configure WhatsApp integration (if needed)
3. Set up monitoring/alerts
4. Update any external services pointing to old URL

### Medium-term (Next 2 Weeks):
1. Deploy NEXUS AI features (if in GitHub repos)
2. Add 60+ hybrid services (if planned)
3. Enterprise Slack integration (if planned)
4. Cloudflare Admin UI (if planned)
5. CI/CD pipeline setup (if planned)

---

## 🚨 Known Issues & Resolutions

### Issue 1: www.nexussocialmarket.com returns 403 Error 1014
**Status:** 🔧 Being Fixed  
**Cause:** Cloudflare cross-account CNAME conflict  
**Solution:** Emergent domain linking (IN PROGRESS)  
**ETA:** 10-20 minutes from now

### Issue 2: OpenClaw Not Running
**Status:** ⏳ Waiting for User Action  
**Cause:** Gateway must be manually started by authenticated user  
**Solution:** Sign in → Click "Start OpenClaw"  
**ETA:** 2 minutes after you sign in

---

## 📞 Need Help?

### If Domain Linking Fails:
1. Check email for Entri authorization link
2. Verify you have admin access to domain registrar
3. Try manual DNS setup (see EMERGENT_DOMAIN_LINKING_GUIDE.md)
4. Contact Emergent support via dashboard

### If OpenClaw Won't Start:
1. Check browser console for errors (F12)
2. Verify you're signed in (check for user email in UI)
3. Try clearing browser cache
4. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`

### If Site Shows Wrong Content:
1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
2. Wait 5 more minutes for DNS propagation
3. Try incognito/private browsing mode
4. Check DNS: `nslookup www.nexussocialmarket.com 8.8.8.8`

---

## ✅ Success Criteria

You'll know everything is working when:

- ✅ `https://www.nexussocialmarket.com` loads without errors
- ✅ "OpenClaw Setup" page shows with Google sign-in button
- ✅ After signing in, you can start OpenClaw
- ✅ OpenClaw Control UI is accessible
- ✅ API responds: `curl www.nexussocialmarket.com/api/`
- ✅ SSL certificate shows as valid in browser
- ✅ No Cloudflare errors (403, 1014, etc.)

---

**Current Step:** Go to Emergent Dashboard → Link Domain → Use Entri → Enter www.nexussocialmarket.com

**Estimated Time to Live Site:** 10-20 minutes from now

**I'll be here monitoring. Let me know once you've initiated the domain linking!**
