# Emergent Domain Linking Guide for www.nexussocialmarket.com

## ✅ What You're About to Do
Link your custom domain `www.nexussocialmarket.com` to your Emergent-hosted app using Entri for automatic DNS configuration.

---

## 📋 Step-by-Step Instructions

### Step 1: Access Emergent Dashboard
1. Go to: **https://app.emergentagent.com** (or your Emergent dashboard URL)
2. Sign in with your account
3. Navigate to **"My Apps"** or **"Projects"**

### Step 2: Find Your App
1. Look for your app: **"OpenClaw Hosting"** or **"NEXUS Social Marketplace"**
2. Click on the app to open its details
3. You should see the current URL: `model-exchange-2.preview.emergentagent.com`

### Step 3: Link Custom Domain
1. Look for **"Link Domain"** or **"Custom Domain"** button
2. Click it to open the domain linking dialog
3. Enter your domain: `www.nexussocialmarket.com`
4. Choose method: **"Use Entri"** (automatic DNS setup)

### Step 4: Entri Automatic Setup
**Entri will:**
- Auto-detect your domain registrar (GoDaddy, Namecheap, Google Domains, etc.)
- Ask you to sign in to your registrar account
- Automatically configure DNS records
- Set up SSL certificate
- Enable CDN and DDoS protection

**What you need:**
- Your domain registrar login credentials (where you bought nexussocialmarket.com)
- 2-3 minutes for the authorization

### Step 5: Wait for Propagation
- **Entri setup**: 2-3 minutes
- **DNS propagation**: 5-15 minutes
- **SSL certificate**: Auto-provisioned (5 minutes)

You'll receive email notifications at each stage.

---

## 🔧 Alternative: Manual DNS Setup

If Entri doesn't work or you prefer manual setup:

### In Emergent Dashboard:
1. Click "Link Domain"
2. Choose **"Manual Setup"**
3. Emergent will provide you with DNS records to add

### Typical DNS Records:
```
Type: CNAME
Name: www
Value: model-exchange-2.preview.emergentagent.com
TTL: 3600 (or Auto)
```

### Add to Your DNS Provider:
**Cloudflare:**
1. Go to: https://dash.cloudflare.com
2. Select domain: nexussocialmarket.com
3. Go to: DNS → Records
4. Find existing www record
5. **IMPORTANT**: Set Proxy status to **"DNS only"** (grey cloud ☁️)
6. Or delete and recreate with the records Emergent provides

**GoDaddy / Namecheap / Other:**
1. Log in to your registrar
2. Find DNS Management
3. Add/update the CNAME record as provided by Emergent

---

## ✅ Verification

### After Setup, Test:
```bash
# Check DNS (wait 5-15 minutes after setup)
curl -I https://www.nexussocialmarket.com

# Should return 200 OK with SSL certificate

# Test your app
curl https://www.nexussocialmarket.com/api/
# Should return: {"message":"OpenClaw Hosting API"}
```

### In Browser:
Open: `https://www.nexussocialmarket.com`  
You should see: **OpenClaw Setup** page with Google sign-in

---

## 🚨 Important Notes

### Cloudflare Conflict Resolution
Since you already have a DNS record in Cloudflare, you have two options:

**Option 1 (Recommended):** Let Entri handle it
- Entri will detect the existing Cloudflare record
- It will update it automatically during authorization

**Option 2:** Delete the existing record first
1. Go to Cloudflare Dashboard
2. DNS → Records
3. Delete the `www` CNAME record
4. Then proceed with Emergent linking

### Current Cloudflare Record:
```
Type: CNAME
Name: www.nexussocialmarket.com
Target: model-exchange-2.preview.emergentagent.com
Proxied: ✅ (This is causing the 403 error)
```

---

## 📊 What Changes

### Before:
```
User → www.nexussocialmarket.com → ❌ Cloudflare Error 1014
                                    (Cross-account CNAME blocked)
```

### After Emergent Linking:
```
User → www.nexussocialmarket.com → Emergent Edge (CDN)
                                 → Your App
                                 → ✅ Working!
```

---

## ⏱️ Timeline

| Step | Time | Status |
|------|------|--------|
| Entri Authorization | 2-3 min | During setup |
| DNS Update | Instant | Automatic |
| DNS Propagation | 5-15 min | Wait period |
| SSL Certificate | 5-10 min | Auto-provisioned |
| **Total Time** | **10-20 minutes** | **From start to live** |

---

## 🆘 Troubleshooting

### "Domain already in use"
- This means the domain is already linked in your Emergent account
- Check if it's linked to a different app
- Contact Emergent support to unlink

### "Cannot verify domain"
- Wait 5-15 minutes for DNS propagation
- Clear your DNS cache: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)
- Try a different DNS: `nslookup www.nexussocialmarket.com 8.8.8.8`

### Entri Authorization Failed
- Make sure you have admin access to your domain registrar account
- Try manual DNS setup instead
- Check if your registrar is supported by Entri

### Still Getting 403 Error
1. Wait 15 minutes for full DNS propagation
2. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
3. Try incognito/private browsing mode
4. Check Cloudflare record is removed or set to "DNS only"

---

## 📞 Support

**Emergent Support:**
- Dashboard: https://app.emergentagent.com
- Help docs: https://docs.emergentagent.com
- Support chat: In-app support button

**Current App Info:**
- App Name: OpenClaw Hosting / NEXUS Social Marketplace
- Current URL: https://model-exchange-2.preview.emergentagent.com
- Target Domain: www.nexussocialmarket.com
- Cloudflare Zone: nexussocialmarket.com (0befffe8f39e38684186182fa8919f92)

---

## ✅ Next Steps After Domain is Live

Once `www.nexussocialmarket.com` is working:

1. **Start OpenClaw Gateway** (if needed):
   - Sign in with Google
   - Click "Start OpenClaw"
   - Configure your AI provider (Emergent/OpenAI/Anthropic)

2. **Update Any Hardcoded URLs** (if applicable):
   - Check your GitHub repos for any references to the old URL
   - Update API endpoints in any external services

3. **Set Up Analytics** (optional):
   - Add Google Analytics
   - Enable Emergent monitoring
   - Set up error tracking

4. **Test All Features**:
   - Authentication flow
   - OpenClaw gateway
   - API endpoints
   - Database connections

---

**Ready? Head to your Emergent Dashboard and click "Link Domain"!**

I'll be here to help if you run into any issues. Just share the error message or screenshot.
