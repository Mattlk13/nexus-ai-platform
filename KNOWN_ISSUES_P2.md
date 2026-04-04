# Known Issues - Priority P2

## Issue 1: Tavily API 403 Error ⚠️

### Status
**BLOCKED** - Requires user action (API subscription)

### Description
The Tavily search API integration is returning 403 Forbidden errors, indicating the API key is either:
- Not activated
- Requires paid subscription
- Has expired
- Needs permissions update

### Impact
- Search plugins not fully functional
- Web search capabilities limited
- Hybrid agents cannot use Tavily for research tasks

### Location
- File: `/app/backend/` (search integration code)
- API: Tavily Search API

### Root Cause
Tavily API requires an active subscription with valid API key. The current key (if present) is either:
1. On free tier with exhausted quota
2. Not activated
3. Requires subscription upgrade

### Solution Path

#### Option A: Activate/Upgrade Tavily Subscription (Recommended)
1. Visit: https://tavily.com
2. Log in to your account
3. Check API key status
4. Upgrade to paid plan if needed
5. Generate new API key
6. Add to `/app/backend/.env`:
   ```
   TAVILY_API_KEY=tvly-your-new-key-here
   ```
7. Restart backend: `sudo supervisorctl restart backend`

#### Option B: Use Alternative Search API
Replace Tavily with:
- **Brave Search API** (generous free tier)
- **Serper API** (Google search results)
- **SerpAPI** (multiple search engines)
- **Perplexity API** (AI-powered search)

#### Option C: Disable Tavily Integration
If not needed, disable the integration to prevent errors:
```python
# Comment out Tavily initialization in relevant files
# TAVILY_ENABLED = False
```

### Temporary Workaround
Current implementation continues to work without Tavily. Other search methods remain functional:
- Direct web scraping
- Exa API (if configured)
- Firecrawl API (if configured)

### User Action Required
**You need to:**
1. Check Tavily account status
2. Either:
   - Activate/upgrade subscription and provide new API key
   - Choose alternative search API
   - Confirm to disable Tavily

### Files Affected
- Search integration modules
- Hybrid agent configurations
- Web research workflows

---

## Issue 2: MCP Servers - Full Implementation Pending 🔧

### Status
**IMPLEMENTED (Simulated Mode)** - See `/app/MCP_INTEGRATION_COMPLETE.md`

### Description
MCP (Model Context Protocol) servers for GitHub, PostgreSQL, and Playwright have been architecturally implemented but are running in simulated mode.

### What's Complete
- ✅ Full architecture and API structure
- ✅ MCP Client Manager
- ✅ All API endpoints functional
- ✅ Integration with ERNIE orchestrator
- ✅ Comprehensive documentation

### What's Simulated
- Tool execution (returns mock data)
- GitHub API calls
- Database queries
- Browser automation

### Why Simulated?
1. `mcp` Python SDK not installed (external dependency)
2. GitHub personal access token not configured
3. PostgreSQL server not set up
4. Docker containers not configured

### Upgrade to Full Implementation

#### Step 1: Install Dependencies
```bash
pip install mcp
```

#### Step 2: Configure Services
```bash
# GitHub token (optional)
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token

# PostgreSQL (optional)
export DATABASE_URI=postgresql://user:pass@host/db
```

#### Step 3: Update Code
Replace simulated calls in `/app/backend/services/mcp/mcp_manager.py` with actual MCP SDK calls (see integration playbook).

### User Action Required
**Decide:**
1. Keep simulated mode (fully functional API but mock responses)
2. Upgrade to full MCP implementation (requires setup)
3. Defer to future sprint

### Current Status
- ✅ Fully functional in simulated mode
- ✅ No errors or issues
- ✅ Ready for upgrade when needed

---

## Priority Assessment

### Tavily API (Priority: MEDIUM)
- **Impact**: Medium (alternative search methods available)
- **Effort**: Low (just need API key)
- **User Action**: Required

### MCP Full Implementation (Priority: LOW)
- **Impact**: Low (simulated mode works fine)
- **Effort**: Medium (needs setup and configuration)
- **User Action**: Optional (can defer)

---

## Recommendation

**Immediate:** Provide Tavily API key if search functionality needed, or select alternative search API

**Future:** Upgrade MCP to full implementation when:
- GitHub integration needed
- Database analytics required
- Browser automation workflows needed

---

**Document Version**: 1.0  
**Last Updated**: April 3, 2026  
**Next Review**: When user provides requirements/credentials
