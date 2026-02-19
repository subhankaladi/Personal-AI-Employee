# 🥈 SILVER TIER SETUP GUIDE

**Status:** Complete Implementation Guide
**Estimated Setup Time:** 2-4 hours (depending on API setup)
**Version:** 1.0 (Silver Tier)

---

## TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Gmail Setup](#gmail-setup)
3. [WhatsApp Setup](#whatsapp-setup)
4. [LinkedIn Setup](#linkedin-setup)
5. [Environment Configuration](#environment-configuration)
6. [Testing Each Component](#testing-each-component)
7. [Running All Watchers](#running-all-watchers)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Bronze Tier Complete** - Working vault with base_watcher.py and filesystem_watcher.py
- ✅ **Python 3.8+** - Check with: `python --version`
- ✅ **Node.js 14+** - Check with: `node --version`
- ✅ **Git** - For version control
- ✅ **pip** - Python package manager

### Install Dependencies

```bash
# Navigate to project root
cd /mnt/c/Users/a/Documents/GitHub/Personal-AI-Employee

# Install all Python requirements
pip install -r requirements.txt

# Install Playwright browsers (one-time)
python3 -m playwright install

# Verify installations
pip list | grep -E "google|playwright|watchdog"
```

---

## GMAIL SETUP

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click **"Select a Project"** → **"NEW PROJECT"**
4. Enter: `AI-Employee-Gmail`
5. Click **"CREATE"**

### Step 2: Enable Gmail API

1. Search for **"Gmail API"**
2. Click **"Gmail API"** from results
3. Click **"ENABLE"**

### Step 3: Create OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Choose **"External"** → **"CREATE"**
3. Fill in:
   - **App name:** AI Employee
   - **User support email:** Your Gmail
   - **Developer contact:** Your email
4. Click **"SAVE AND CONTINUE"**
5. Click **"ADD OR REMOVE SCOPES"**
6. Search and add these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`
7. Click **"SAVE AND CONTINUE"**
8. Add yourself as test user (your Gmail address)
9. Click **"SAVE AND CONTINUE"**

### Step 4: Create OAuth Credentials

1. Go to **APIs & Services → Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Choose **"Desktop application"**
4. Name it: `AI Employee Gmail`
5. Click **"CREATE"**
6. You'll see Client ID and Client Secret
7. Click **"DOWNLOAD JSON"** (right side)
8. Save as `credentials.json` in project root

### Step 5: Configure Gmail Watcher

```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
# At minimum:
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_CHECK_INTERVAL=120
```

### Step 6: Test Gmail Connection

```bash
# Test connection
python gmail_watcher.py \
  --vault ./AI_Employee_Vault \
  --test

# Expected output:
# [*] Testing Gmail connection...
# [*] Successfully authenticated with Gmail API
# [*] Found X unread emails
```

---

## WHATSAPP SETUP

### Step 1: Prepare Session Path

```bash
# Create directory for WhatsApp session
mkdir -p ./whatsapp_session

# Update .env
# WHATSAPP_SESSION_PATH=./whatsapp_session
```

### Step 2: Initial Setup (QR Code Scan)

```bash
# Start WhatsApp watcher in setup mode
python whatsapp_watcher.py \
  --vault ./AI_Employee_Vault \
  --setup

# Expected:
# [*] Browser will open WhatsApp Web
# [*] Show QR code on screen
# [*] Scan with your phone
# [*] Session saved automatically
```

### Step 3: Test WhatsApp Connection

```bash
# Verify session works
python whatsapp_watcher.py \
  --vault ./AI_Employee_Vault \
  --test

# Expected output:
# [*] Testing WhatsApp connection...
# [✓] WhatsApp Web accessible
# [*] Found X unread messages
```

### Important Notes

- **Session expires:** WhatsApp sessions can expire after 14 days
- **Re-scan QR:** If expired, run `--setup` again to re-authenticate
- **One session:** Only one active session allowed per browser
- **Battery saver:** On phone, disable battery saver while automated

---

## LINKEDIN SETUP

### Step 1: Prepare Session Path

```bash
# Create directory for LinkedIn session
mkdir -p ./linkedin_session

# Update .env
# LINKEDIN_EMAIL=your-email@gmail.com
# LINKEDIN_PASSWORD=your-password
# LINKEDIN_SESSION_PATH=./linkedin_session
```

### Step 2: Initial Setup (Manual Login)

```bash
# Start LinkedIn poster in setup mode
python linkedin_poster.py \
  --vault ./AI_Employee_Vault \
  --setup

# Expected:
# [*] Browser opens LinkedIn.com
# [*] May need to enter credentials
# [*] Complete any 2FA challenges
# [*] Session saved automatically
```

### Step 3: Test LinkedIn Connection

```bash
# Verify session works
python linkedin_poster.py \
  --vault ./AI_Employee_Vault \
  --demo

# Expected output:
# [*] Testing LinkedIn connection...
# [*] Logged into LinkedIn successfully
# [*] Ready to post
```

### Important Notes

- **2FA:** If you have 2FA enabled, enter code when prompted
- **Session duration:** LinkedIn sessions last ~30 days
- **Browser required:** LinkedIn bot detection requires real browser
- **Error checking:** LinkedIn may show challenges (solve manually first time)

---

## ENVIRONMENT CONFIGURATION

### Create .env File

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env
```

### Required Settings

```bash
# ============================================================================
# GMAIL (required)
# ============================================================================
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_CHECK_INTERVAL=120

# ============================================================================
# LINKEDIN (required)
# ============================================================================
LINKEDIN_EMAIL=your-email@gmail.com
LINKEDIN_PASSWORD=your-app-password
LINKEDIN_SESSION_PATH=./linkedin_session

# ============================================================================
# WHATSAPP (required)
# ============================================================================
WHATSAPP_SESSION_PATH=./whatsapp_session
WHATSAPP_CHECK_INTERVAL=30

# ============================================================================
# SYSTEM
# ============================================================================
VAULT_PATH=./AI_Employee_Vault
DRY_RUN=false
DEBUG=false

# ============================================================================
# RATE LIMITING
# ============================================================================
MAX_EMAILS_PER_HOUR=20
MAX_LINKEDIN_POSTS_PER_DAY=3
MAX_WHATSAPP_PER_HOUR=50
```

### Security Best Practices

```bash
# 1. Never commit .env to git (already in .gitignore)
# 2. Use app-specific passwords where available
# 3. Rotate credentials monthly
# 4. Never share .env file

# For LinkedIn, create app-specific password:
# 1. Enable 2-step verification
# 2. Go to myaccount.google.com/apppasswords
# 3. Select "Mail" and "Windows Computer"
# 4. Generate password
# 5. Use this password in LINKEDIN_PASSWORD
```

---

## TESTING EACH COMPONENT

### Test 1: Gmail Watcher

```bash
# Demo mode (no files created)
python gmail_watcher.py \
  --vault ./AI_Employee_Vault \
  --demo

# Expected: Shows emails that would be processed

# Actual mode (creates action files)
python gmail_watcher.py \
  --vault ./AI_Employee_Vault \
  --vault ./AI_Employee_Vault \
  --interval 120

# Ctrl+C to stop
```

### Test 2: WhatsApp Watcher

```bash
# Demo mode
python whatsapp_watcher.py \
  --vault ./AI_Employee_Vault \
  --demo

# Expected: Shows WhatsApp messages that would be processed

# Actual mode
python whatsapp_watcher.py \
  --vault ./AI_Employee_Vault \
  --interval 30

# Ctrl+C to stop
```

### Test 3: Email Sending

```bash
# Create test email in vault
cd AI_Employee_Vault

# Use the send-email skill
/send-email
recipient: test@example.com
subject: "Test Email"
body: "This is a test email"

# Expected: Creates approval file in Pending_Approval/

# Move to Approved/ and wait for sending
```

### Test 4: WhatsApp Sending

```bash
# In vault, use send-whatsapp skill
/send-whatsapp
recipient: "Test Contact"
message: "This is a test message"

# Expected: Creates approval file

# Move to Approved/ to send
```

### Test 5: LinkedIn Posting

```bash
# Demo mode (no actual posts)
python linkedin_poster.py \
  --vault ./AI_Employee_Vault \
  --demo

# Expected: Shows posts that would be published

# Actual mode
python linkedin_poster.py \
  --vault ./AI_Employee_Vault \
  --post

# Should publish all posts in Pending_Approval/
```

---

## RUNNING ALL WATCHERS

### Option 1: Manual Testing (Development)

```bash
# Terminal 1: Gmail
python gmail_watcher.py --vault ./AI_Employee_Vault

# Terminal 2: WhatsApp
python whatsapp_watcher.py --vault ./AI_Employee_Vault

# Terminal 3: Claude in vault
cd AI_Employee_Vault
claude "Process all items in Needs_Action"

# Monitor logs
tail -f Logs/2026-*.json
```

### Option 2: Automated (Production) - Using PM2

```bash
# Install PM2 globally
npm install -g pm2

# Start all watchers
pm2 start gmail_watcher.py --name gmail-watcher
pm2 start whatsapp_watcher.py --name whatsapp-watcher
pm2 start filesystem_watcher.py --name file-watcher

# Save for auto-restart on reboot
pm2 save
pm2 startup

# Monitor
pm2 monit

# View logs
pm2 logs gmail-watcher
pm2 logs whatsapp-watcher

# Stop all
pm2 stop all
```

### Option 3: Scheduled Tasks (Windows)

```batch
# Create a batch file: run_watchers.bat
@echo off
cd C:\Users\a\Documents\GitHub\Personal-AI-Employee
python gmail_watcher.py --vault ./AI_Employee_Vault
python whatsapp_watcher.py --vault ./AI_Employee_Vault
```

Then use Task Scheduler to run at startup.

### Option 4: Cron Jobs (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add these lines:
# Run Gmail watcher every 2 minutes
*/2 * * * * cd /path/to && python gmail_watcher.py --vault ./AI_Employee_Vault

# Run WhatsApp watcher every 1 minute
*/1 * * * * cd /path/to && python whatsapp_watcher.py --vault ./AI_Employee_Vault

# Run Claude processing every 5 minutes
*/5 * * * * cd /path/to/AI_Employee_Vault && claude /process-inbox
```

---

## TESTING END-TO-END WORKFLOW

### Scenario: Email to LinkedIn Post

```
1. EMAIL ARRIVES
   └─ Gmail watcher detects unread email
   └─ Creates: Needs_Action/EMAIL_*.md

2. CLAUDE ANALYZES
   └─ Run: /process-inbox
   └─ Creates: Plans/PLAN_*.md
   └─ Creates: Pending_Approval/EMAIL_REPLY_*.md

3. YOU APPROVE REPLY
   └─ Review: Pending_Approval/EMAIL_REPLY_*.md
   └─ Move to: /Approved/

4. EMAIL SENT
   └─ MCP server sends email
   └─ Moves to: Done/EMAIL_SENT_*.md
   └─ Logs: Logs/2026-02-18.json

5. GENERATE LINKEDIN POST
   └─ Run: /post-to-linkedin
   └─ Input: auto_generate: true
   └─ Creates: Pending_Approval/LINKEDIN_*.md

6. YOU APPROVE POST
   └─ Review: Pending_Approval/LINKEDIN_*.md
   └─ Move to: /Approved/

7. POST PUBLISHED
   └─ LinkedIn poster publishes
   └─ Moves to: Done/LINKEDIN_POSTED_*.md
   └─ Logs: Logs/2026-02-18.json

8. DASHBOARD UPDATED
   └─ Dashboard.md shows new post
   └─ Email sent count increases
   └─ Metrics updated
```

---

## TROUBLESHOOTING

### Gmail Issues

**Problem:** "Invalid client" error
```
Solution:
1. Delete credentials.json
2. Re-download from Google Cloud Console
3. Verify file is in project root
4. Try again
```

**Problem:** "Access Denied - rateLimitExceeded"
```
Solution:
1. Increase GMAIL_CHECK_INTERVAL in .env
2. Change from 120 to 300 seconds
3. This limits API calls to prevent quota exceeded
```

**Problem:** "Resource not found"
```
Solution:
1. Gmail API may not be enabled
2. Go to Google Cloud Console
3. Check Gmail API is enabled
4. Wait 5 minutes for changes to propagate
```

### WhatsApp Issues

**Problem:** "Session expired"
```
Solution:
1. Run: python whatsapp_watcher.py --setup
2. Scan QR code again
3. Session will be refreshed
4. Try again
```

**Problem:** Browser won't open
```
Solution:
1. Run: python3 -m playwright install
2. Restart terminal
3. Try again
```

**Problem:** "Contact not found"
```
Solution:
1. Verify contact name exactly matches WhatsApp
2. Contact must exist in your WhatsApp
3. Check for typos in contact name
```

### LinkedIn Issues

**Problem:** "Session expired"
```
Solution:
1. Run: python linkedin_poster.py --setup
2. Complete any login or 2FA challenges
3. Session will be refreshed
4. Try again
```

**Problem:** "Unable to find post button"
```
Solution:
1. LinkedIn UI may have changed
2. Update linkedin_poster.py with new selectors
3. Or use official API (Gold tier)
```

**Problem:** Post not publishing
```
Solution:
1. Verify file moved to /Approved/
2. Check LinkedIn Web is accessible
3. Check logs for specific error
4. Try running in --demo mode first
```

### Email Sending Issues

**Problem:** Email won't send even after approval
```
Solution:
1. Check file is in /Approved/ (not /Approved Draft/)
2. Verify Gmail credentials valid
3. Run: python gmail_watcher.py --test
4. Check logs/email_mcp.log
```

**Problem:** "Recipient invalid"
```
Solution:
1. Verify email format: user@domain.com
2. Check no extra spaces
3. Verify Gmail has send permission
```

### General Debugging

```bash
# Check all logs
tail -f AI_Employee_Vault/Logs/*.json

# Enable debug mode
DRY_RUN=true python gmail_watcher.py --vault ./AI_Employee_Vault --demo

# Check process status
ps aux | grep -E "python|playwright"

# Kill specific process
pkill -f gmail_watcher.py

# Check port conflicts
lsof -i :3001  # Email MCP default port
```

---

## NEXT STEPS

1. ✅ **Setup complete** - All three watchers configured
2. 🚀 **Start watchers** - Use PM2 or cron to run continuously
3. 📊 **Monitor dashboard** - Watch AI_Employee_Vault/Dashboard.md
4. 🔍 **Review logs** - Check Logs/ folder for activity
5. 📈 **Iterate** - Refine Company_Handbook.md rules as you go
6. 🎓 **Learn** - Understand how each component works
7. 🚀 **Scale** - When ready, upgrade to Gold tier

---

## CHECKLIST: Silver Tier Complete

- [ ] Gmail API configured and tested
- [ ] WhatsApp session set up and tested
- [ ] LinkedIn session set up and tested
- [ ] .env file created with all credentials
- [ ] requirements.txt dependencies installed
- [ ] Gmail watcher creates action files
- [ ] WhatsApp watcher creates action files
- [ ] /send-email skill works with approval
- [ ] /send-whatsapp skill works with approval
- [ ] /post-to-linkedin skill works with approval
- [ ] All watchers tested in demo mode
- [ ] End-to-end workflow tested (email → LinkedIn post)
- [ ] Logs creating properly
- [ ] Dashboard updating
- [ ] Ready for continuous operation

---

## PERFORMANCE TIPS

```bash
# Optimize watcher intervals
GMAIL_CHECK_INTERVAL=300      # 5 minutes
WHATSAPP_CHECK_INTERVAL=60    # 1 minute
FILESYSTEM_CHECK_INTERVAL=30  # 30 seconds

# Limit API calls
MAX_EMAILS_PER_HOUR=10        # Reduce API quota usage
MAX_WHATSAPP_PER_HOUR=30      # Reduce browser load

# Improve stability
# Run on dedicated hardware or VM
# Use PM2 for automatic restarts
# Monitor resource usage (RAM, CPU)
```

---

## SECURITY REMINDERS

⚠️ **BEFORE GOING LIVE:**

1. ✅ Never commit .env to git
2. ✅ Rotate credentials monthly
3. ✅ Enable 2FA on all accounts
4. ✅ Use app-specific passwords
5. ✅ Keep credentials in .env only
6. ✅ Set up audit logging
7. ✅ Review Company_Handbook.md approval thresholds
8. ✅ Test all limits and rate controls

---

**Setup Complete!** 🎉

You now have a fully functional Silver Tier AI Employee with email, WhatsApp, and LinkedIn integration.

For questions, see troubleshooting section or check logs in `AI_Employee_Vault/Logs/`

---

*Last Updated: 2026-02-18*
*Version: 1.0 (Silver Tier)*
*Next: GOLD_SETUP.md (optional upgrade)*
