# Emergent Support Request - Custom Domain Setup

## Request Summary
Please add `www.nexussocialmarket.com` as a Custom Hostname in Emergent's Cloudflare for SaaS configuration to enable cross-account CNAME resolution.

---

## Issue Details

**My Domain:** www.nexussocialmarket.com  
**Target App:** model-exchange-2.preview.emergentagent.com  
**Problem:** Cloudflare Error 1014 (CNAME Cross-User Banned) and Error 1000 (DNS points to prohibited IP)

**Current DNS Configuration:**
- Type: A Record
- Name: www.nexussocialmarket.com
- Content: 104.18.10.243 (Cloudflare IP)
- Proxied: No

**Root Cause:**
My domain (nexussocialmarket.com) is managed in my Cloudflare account, while the target (model-exchange-2.preview.emergentagent.com) is in Emergent's Cloudflare account. Cloudflare blocks cross-account DNS pointing for security reasons.

---

## Requested Action

Please add `www.nexussocialmarket.com` as a **Custom Hostname** in Emergent's Cloudflare for SaaS setup.

**This will:**
1. Authorize the cross-account connection
2. Provision an SSL certificate for www.nexussocialmarket.com
3. Allow my domain to properly resolve to the Emergent app
4. Enable full Cloudflare CDN and protection features

---

## Technical Details

**My Cloudflare Account:**
- Zone: nexussocialmarket.com
- Zone ID: 0befffe8f39e38684186182fa8919f92
- Account ID: 9ea3a006589428efed0480da5c037163

**Emergent App:**
- Current URL: https://model-exchange-2.preview.emergentagent.com
- App Type: OpenClaw Hosting Platform
- Target Domain: www.nexussocialmarket.com

**Documentation Reference:**
https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/domain-support/create-custom-hostnames/

---

## Steps for Emergent Team

1. Log in to Cloudflare Dashboard for model-exchange-2.preview.emergentagent.com zone
2. Go to: **SSL/TLS → Custom Hostnames**
3. Click **"Add Custom Hostname"**
4. Enter:
   - Hostname: `www.nexussocialmarket.com`
   - SSL: HTTP DV (Domain Validation)
   - Enable HTTP/2: Yes
   - Min TLS Version: 1.2
5. Save and wait for SSL certificate issuance (5-15 minutes)

---

## Alternative Solutions Attempted

✅ Disabled Cloudflare proxy (grey cloud) - Still blocked  
✅ Changed CNAME to A record - Still blocked (Error 1000)  
✅ Verified all DNS configurations - Correct  
✅ Tried 3 different API tokens - All lack Custom Hostname permissions  
❌ Custom Hostname creation requires Cloudflare Business/Enterprise plan  

**Conclusion:** Only Emergent can authorize this custom domain by adding it to your Cloudflare for SaaS configuration.

---

## Contact Information

**User:** [Your Name/Email]  
**Domain:** www.nexussocialmarket.com  
**Emergent App:** model-exchange-2.preview.emergentagent.com  
**Created:** April 1, 2026  

---

## Expected Result

After adding the custom hostname:
- https://www.nexussocialmarket.com → Shows OpenClaw Setup page ✅
- No Cloudflare errors (1014, 1000, etc.) ✅
- SSL certificate auto-provisioned ✅
- Full CDN and DDoS protection active ✅

---

## Urgency

**Priority:** High  
**Impact:** Cannot use custom domain, must use preview URL  
**Business Impact:** Branding and user experience affected

---

## Additional Notes

- I cannot access the Emergent Dashboard currently (login issues)
- The app is working perfectly at the preview URL
- All Cloudflare tokens and configurations on my end are correct
- This is a standard Cloudflare for SaaS custom hostname request

**Thank you for your assistance!**
