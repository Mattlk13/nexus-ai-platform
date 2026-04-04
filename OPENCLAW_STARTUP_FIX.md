# OpenClaw Startup Issue - Root Cause & Fix

## 🔍 Problem Identified

**Symptom:** OpenClaw gateway showed `FATAL - Exited too quickly` in supervisor

**Root Causes Found:**

### 1. Node Version Mismatch
- **Issue**: Supervisor was not using Node 22 (required for OpenClaw 2026.4.1)
- **Evidence**: Logs showed "Config was last written by newer OpenClaw (2026.4.1); current version is 2026.3.2"
- **Cause**: Supervisor environment didn't include NVM path for Node 22

### 2. Port Conflict
- **Issue**: OpenClaw was already running on port 18789 from manual start
- **Evidence**: "Gateway failed to start: another gateway instance is already listening on ws://0.0.0.0:18789"
- **Cause**: Process from earlier testing session still running

### 3. Supervisor Configuration Missing PATH
- **Issue**: Supervisor couldn't find Node 22 binary
- **Cause**: No PATH environment variable pointing to NVM's Node 22 installation

## ✅ Solution Implemented

### Fix 1: Update Supervisor Configuration

**File:** `/etc/supervisor/conf.d/openclaw_gateway.conf`

**Added:**
```ini
environment=HOME="/root",USER="root",PATH="/root/.nvm/versions/node/v22.22.2/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
```

This ensures supervisor uses Node 22.22.2 from NVM.

### Fix 2: Kill Conflicting Processes

```bash
# Kill all existing OpenClaw processes
kill -9 $(ps aux | grep "[o]penclaw" | awk '{print $2}')
```

### Fix 3: Restart with Correct Configuration

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start openclaw-gateway
```

## ✅ Verification

**After Fix:**
```bash
$ sudo supervisorctl status openclaw-gateway
openclaw-gateway                 RUNNING   pid 958, uptime 0:00:14

$ curl http://localhost:18789/__openclaw__/health
# Returns OpenClaw Control UI (HTML)

$ tail /var/log/supervisor/openclaw-gateway.out.log
[gateway] listening on ws://0.0.0.0:18789 (PID 1497)
[gateway] agent model: emergent-claude/claude-opus-4-6
```

**Success Indicators:**
- ✅ Status: RUNNING (not FATAL)
- ✅ Gateway listening on ws://0.0.0.0:18789
- ✅ Using correct Node version (v22.22.2)
- ✅ Using correct OpenClaw version (2026.4.1)
- ✅ Control UI accessible
- ✅ Health endpoint responding

## 🔧 Wrapper Script Updates

**File:** `/root/run_openclaw_supervised.sh`

**Key Changes:**
```bash
#!/bin/bash
set -e

# Load NVM to access Node 22 and OpenClaw
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 22 > /dev/null 2>&1

# ... rest of script
```

This ensures the wrapper script always uses Node 22 via NVM.

## 📊 Current Status

**OpenClaw Gateway:**
- **Status**: ✅ RUNNING
- **PID**: 1497 (via supervisor process 958)
- **Port**: 18789
- **Node Version**: v22.22.2
- **OpenClaw Version**: 2026.4.1 (da64a97)
- **Agent Model**: emergent-claude/claude-opus-4-6
- **Supervisor**: Managed and auto-restart enabled

**Control UI:**
- **URL**: http://localhost:18789
- **WebSocket**: ws://0.0.0.0:18789
- **Canvas**: http://0.0.0.0:18789/__openclaw__/canvas/
- **Health**: http://localhost:18789/__openclaw__/health

## 🎯 Lessons Learned

1. **Always specify PATH for supervisor** when using version managers (NVM, pyenv, etc.)
2. **Check for port conflicts** before starting services
3. **Verify Node version** matches OpenClaw requirements
4. **Use proper environment variables** in supervisor config
5. **Test wrapper scripts** independently before supervisor integration

## 🚀 Deployment Checklist

When deploying OpenClaw to production:

- [ ] Ensure Node 22+ is installed
- [ ] Set NVM path in supervisor environment
- [ ] Check port 18789 is available
- [ ] Verify gateway.env exists
- [ ] Configure authentication token
- [ ] Test Control UI accessibility
- [ ] Verify WebSocket connectivity
- [ ] Check logs for errors
- [ ] Confirm agent model is configured

## ✅ ISSUE RESOLVED

OpenClaw is now fully operational and will start reliably via supervisor! 🎉
