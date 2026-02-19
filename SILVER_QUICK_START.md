# 🚀 SILVER TIER - QUICK START

**Start here after Bronze tier is complete!**

---

## What You Get

✅ **Gmail Integration** - Monitor inbox, send emails with approval
✅ **WhatsApp Monitoring** - Detect urgent messages, send replies
✅ **LinkedIn Posting** - Auto-publish posts about completed work
✅ **Enhanced Approvals** - Safety checks for all external actions
✅ **Audit Logging** - Track every action taken

---

## Setup in 3 Steps

### Step 1: Install Dependencies (5 minutes)

```bash
cd /mnt/c/Users/a/Documents/GitHub/Personal-AI-Employee

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
python3 -m playwright install
```

### Step 2: Configure Credentials (15 minutes)

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env

# For Gmail:
# - Follow GMAIL_SETUP.md to download credentials.json
# - Place credentials.json in project root
# - Add GMAIL_CREDENTIALS_PATH=./credentials.json to .env

# For LinkedIn:
# - Add your email and password to .env
# - LINKEDIN_EMAIL=your-email@gmail.com
# - LINKEDIN_PASSWORD=your-app-password

# For WhatsApp:
# - Run: python whatsapp_watcher.py --vault ./AI_Employee_Vault --setup
# - Scan QR code when browser opens
```

### Step 3: Test Everything (10 minutes)

```bash
# Test Gmail
python gmail_watcher.py --vault ./AI_Employee_Vault --test

# Test WhatsApp
python whatsapp_watcher.py --vault ./AI_Employee_Vault --test

# Test LinkedIn
python linkedin_poster.py --vault ./AI_Employee_Vault --demo
```

---

## What's New

### New Python Scripts
- `gmail_watcher.py` - Monitor Gmail
- `whatsapp_watcher.py` - Monitor WhatsApp
- `linkedin_poster.py` - Publish to LinkedIn

### New Agent Skills
- `/send-email` - Send emails with approval
- `/send-whatsapp` - Send WhatsApp messages
- `/post-to-linkedin` - Publish LinkedIn posts

### New MCP Servers
- `mcp_servers/email_mcp.js` - Email operations
- `mcp_servers/whatsapp_mcp.js` - WhatsApp operations
- `mcp_servers/linkedin_mcp.js` - LinkedIn operations

### New Folders in Vault
- `Inbox/` - Email drafts
- `WhatsApp_Chats/` - Chat transcripts
- `Social_Media/` - Social content
- `In_Progress/` - Active tasks

---

## Quick Workflow

### Email Example

```
1. Email arrives → Gmail watcher detects
2. Creates action file in Needs_Action/
3. You run: /process-inbox
4. Claude drafts reply → Pending_Approval/
5. You approve (move to Approved/)
6. Email MCP sends
7. Logged & moved to Done/
```

### LinkedIn Example

```
1. You complete project
2. Run: /post-to-linkedin auto_generate: true
3. Claude generates post draft
4. Creates Pending_Approval/LINKEDIN_*.md
5. You review & approve
6. LinkedIn poster publishes
7. Analytics tracked
```

### WhatsApp Example

```
1. Urgent message arrives
2. WhatsApp watcher detects
3. Creates action in Needs_Action/
4. Claude analyzes urgency
5. Creates approval request
6. You approve
7. Message sent via browser
```

---

## Running Continuously

### Option A: PM2 (Recommended)

```bash
npm install -g pm2

# Start all watchers
pm2 start gmail_watcher.py --name gmail
pm2 start whatsapp_watcher.py --name whatsapp
pm2 start linkedin_poster.py --name linkedin

# Make persistent
pm2 save
pm2 startup

# Monitor
pm2 monit
pm2 logs gmail
```

### Option B: Cron (Linux/Mac)

```bash
crontab -e

# Add these lines:
*/2 * * * * cd /path && python gmail_watcher.py --vault ./AI_Employee_Vault
*/1 * * * * cd /path && python whatsapp_watcher.py --vault ./AI_Employee_Vault
*/5 * * * * cd /path/AI_Employee_Vault && claude /process-inbox
```

### Option C: Manual (Development)

```bash
# Terminal 1: Gmail
python gmail_watcher.py --vault ./AI_Employee_Vault

# Terminal 2: WhatsApp
python whatsapp_watcher.py --vault ./AI_Employee_Vault

# Terminal 3: Claude (in vault)
cd AI_Employee_Vault && claude /process-inbox
```

---

## Important Files

| File | Purpose |
|------|---------|
| SILVER_SETUP.md | Detailed setup (follow this!) |
| SILVER_TIER_COMPLETE.md | Feature summary |
| GMAIL_SETUP.md | Gmail authentication |
| requirements.txt | Python dependencies |
| .env.example | Configuration template |
| .env | Your credentials (don't commit!) |

---

## First Time Setup

**If starting from scratch:**

1. ✅ Complete Bronze tier (should already be done)
2. ✅ Read this file (you are here)
3. ✅ Follow SILVER_SETUP.md step-by-step
4. ✅ Test each component
5. ✅ Start watchers (PM2 or manual)
6. ✅ Monitor Dashboard.md
7. ✅ Review logs in Logs/

---

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Gmail won't authenticate | Read GMAIL_SETUP.md |
| WhatsApp session expired | Run `python whatsapp_watcher.py --setup` |
| LinkedIn won't post | Check file in /Approved/ folder |
| Email not sending | Check logs: `tail -f Logs/email_mcp.log` |
| High CPU usage | Increase check intervals in .env |

For more help: See "TROUBLESHOOTING" section in SILVER_SETUP.md

---

## Safety Features

✅ **Auto-Approve Only:**
- Known recipients
- Short messages
- Working hours
- Below rate limits

⚠️ **Requires Approval:**
- New recipients
- Long messages
- Urgent/sensitive
- Outside working hours

🚫 **Always Blocked:**
- Phishing patterns
- Spam patterns
- Rate limit exceeded
- Confidential data

Configure in: `AI_Employee_Vault/Company_Handbook.md`

---

## Next: Run Your AI Employee

```bash
# Start all watchers
pm2 start gmail_watcher.py --name gmail
pm2 start whatsapp_watcher.py --name whatsapp
pm2 start linkedin_poster.py --name linkedin

# Monitor activity
cd AI_Employee_Vault
open Dashboard.md  # Or: cat Dashboard.md

# Check logs
tail -f Logs/2026-02-18.json

# Process items
claude /process-inbox

# Publish pending posts
python linkedin_poster.py --vault ./AI_Employee_Vault --post
```

---

## Performance Tips

```
Gmail check interval:    120-300 seconds (adjust in .env)
WhatsApp check interval: 30-60 seconds
LinkedIn posts:          Max 3 per day (LinkedIn limit)
Max emails/hour:         20 (adjust MAX_EMAILS_PER_HOUR in .env)
```

---

**Ready?** Follow SILVER_SETUP.md for complete guide!

Questions? Check the troubleshooting section in SILVER_SETUP.md.

**Let's automate!** 🚀
