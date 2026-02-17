# 🥉 Bronze Tier - Complete Setup Guide

**Estimated Time:** 8-12 hours
**Difficulty:** Intermediate
**Status:** Ready to Build

---

## 📋 What You'll Get

A fully functional local-first AI Employee that:
- ✅ Monitors your file system for new items
- ✅ Organizes tasks in Obsidian vault
- ✅ Creates action plans with human approval
- ✅ Logs all activities for audit trail
- ✅ Integrates with Claude Code
- ✅ Implements Agent Skills for automation

---

## 📦 Prerequisites

Before starting, ensure you have:

### Required Software
- ✅ **Claude Code** (Pro subscription or Gemini Router)
- ✅ **Obsidian** v1.10.6+ ([download](https://obsidian.md/download))
- ✅ **Python** 3.13+ ([download](https://www.python.org/downloads/))
- ✅ **Git** (for version control)

### Required Knowledge
- Comfortable with terminal/command line
- Basic understanding of file systems
- Familiarity with markdown
- Can run Python scripts

### Hardware
- Minimum: 4GB RAM, 2GB disk space
- Recommended: 8GB+ RAM, SSD

---

## 🚀 Quick Start (30 minutes)

### Step 1: Open Vault in Obsidian

1. Open **Obsidian** application
2. Click **"Open folder as vault"**
3. Navigate to: `/path/to/Personal-AI-Employee/AI_Employee_Vault`
4. Click **"Open"**

You should see:
```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Needs_Action/
├── Plans/
├── Done/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Logs/
└── Accounting/
```

### Step 2: Verify Vault Connectivity

In terminal:
```bash
cd /path/to/Personal-AI-Employee

# Test Claude Code can read vault
claude --version  # Should show version

# Create a test task
echo "Test task for processing" > AI_Employee_Vault/Needs_Action/TEST_001.md

# Read it back (Claude should be able to)
cat AI_Employee_Vault/Needs_Action/TEST_001.md
```

### Step 3: Install Python Dependencies

```bash
cd /path/to/Personal-AI-Employee

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install watcher dependencies
pip install watchdog
```

### Step 4: Test the Watchers

```bash
# Test base watcher
python base_watcher.py ./AI_Employee_Vault

# Test filesystem watcher (demo mode)
python filesystem_watcher.py \
  --vault ./AI_Employee_Vault \
  --watch ~/Downloads \
  --demo
```

---

## 🎯 Core Architecture

```
┌─────────────────────────────────┐
│   Your Computer (Local-First)   │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│   Obsidian Vault (Memory)       │  ← All data stored here
├─────────────────────────────────┤
│ Dashboard.md                    │
│ Handbook.md                     │
│ Needs_Action/ ← New items      │
│ Plans/ ← Action plans          │
│ Done/ ← Completed              │
│ Logs/ ← Audit trail            │
└─────────────────────────────────┘
         ↑↓
┌─────────────────────────────────┐
│   Watchers (Senses)             │  ← Background monitoring
├─────────────────────────────────┤
│ filesystem_watcher.py           │
│ (monitors folders)              │
└─────────────────────────────────┘
         ↑↓
┌─────────────────────────────────┐
│   Claude Code (Reasoning)       │  ← Your AI brain
├─────────────────────────────────┤
│ Reads: Needs_Action/            │
│ Thinks: Analyzes items          │
│ Writes: Plans + Approvals       │
│ Updates: Dashboard + Logs       │
└─────────────────────────────────┘
         ↑↓
┌─────────────────────────────────┐
│   Agent Skills (Automation)     │  ← Reusable AI tasks
├─────────────────────────────────┤
│ /process-inbox                  │
│ /generate-briefing              │
│ /manage-approvals               │
└─────────────────────────────────┘
```

---

## 📚 Using the Vault

### 1. Dashboard.md

Your **at-a-glance summary**. Updated regularly by Claude.

```markdown
# 🤖 AI Employee Dashboard

## Quick Stats
| Metric | Value | Status |
| Pending Tasks | 0 | ✅ |
| Approved Actions | 0 | ⏳ |

## Recent Activity
- [2026-02-17 10:45] Processed 3 emails
- [2026-02-17 09:30] System online
```

**Update frequency:** After each task cycle

---

### 2. Company_Handbook.md

Your **rules of engagement**. Claude follows these rules.

Key sections:
- ✅ **Auto-Approve:** What Claude can do without asking
- ⏳ **Requires Approval:** What needs your permission
- 🚫 **Always Blocked:** What Claude will never do

**Keep this updated** as your needs change.

---

### 3. Workflow Folders

#### `/Needs_Action`
📥 **INPUT** - New items waiting for Claude to process

1. Watcher creates `.md` files here
2. Claude reads and analyzes
3. Creates plans and approvals

Example:
```
FILE_2026-02-17_10-30.md ← New file detected
└─ Creates plan
```

#### `/Plans`
📋 **THINKING** - Claude's action plans

Shows Claude's thought process:
- What it found
- What it will do
- What needs approval

Example:
```yaml
---
type: action_plan
status: pending_approval
---

## Objective
Send invoice to Client A

## Steps
- [x] Identified invoice
- [ ] Requires approval to send
```

#### `/Pending_Approval`
⏳ **WAITING** - Items requiring your decision

Move file to:
- `/Approved/` → Execute the action
- `/Rejected/` → Decline the action

Example:
```yaml
---
type: approval_request
action: email
to: client@example.com
---

Send Email: Invoice #123

Status: Awaiting your decision
Move to /Approved to send
```

#### `/Approved`
✅ **APPROVED** - Ready for Claude to execute

Claude watches this folder:
- Executes approved actions
- Via MCP servers
- Moves to `/Done` when complete

#### `/Done`
✅ **COMPLETED** - All finished work

Keeps history of:
- Executed actions
- Completion timestamps
- Audit trail

---

## 🛠️ Running Your AI Employee

### Option 1: Manual (Learn Mode)

```bash
# Terminal 1: Start file watcher
python filesystem_watcher.py \
  --vault ./AI_Employee_Vault \
  --watch ~/Downloads

# Terminal 2: Run Claude to process
cd AI_Employee_Vault
claude "Process all items in /Needs_Action"
```

### Option 2: Scheduled (Daily)

Create a cron job (Mac/Linux):

```bash
# Edit crontab
crontab -e

# Add line to run daily at 8 AM
0 8 * * * cd /path/to && claude "Daily briefing"
```

Or use Task Scheduler (Windows):
1. Open Task Scheduler
2. Create new task
3. Set trigger: Daily 8:00 AM
4. Action: Run `claude "Daily briefing"`

### Option 3: Always-On (Production)

Use PM2 to keep watcher running:

```bash
# Install PM2
npm install -g pm2

# Start watcher
pm2 start filesystem_watcher.py \
  --name "file-watcher" \
  --interpreter python3

# Save and enable on reboot
pm2 save
pm2 startup
```

---

## 🤖 Using Claude Code with Your Vault

### Basic Commands

```bash
# Read the vault
cd AI_Employee_Vault
claude "What's in /Needs_Action?"

# Process items
claude "Process all files and create plans"

# Generate report
claude "Generate today's briefing"

# Manage approvals
claude "Check /Pending_Approval and tell me what needs deciding"
```

### Using Agent Skills

```bash
# Process inbox with skill
/process-inbox

# Generate briefing with skill
/generate-briefing --period daily

# Manage approvals
/manage-approvals review
```

---

## 📖 Common Workflows

### Workflow 1: Capture → Process → Approve

1. **Drop file** in monitored folder (e.g., `~/Downloads/`)
2. **Watcher detects** and creates `.md` in `/Needs_Action`
3. **Claude processes** via `/process-inbox` skill
4. **Creates plan** in `/Plans`
5. **Creates approval** in `/Pending_Approval` if needed
6. **You review** and move to `/Approved` or `/Rejected`
7. **Claude executes** and moves to `/Done`

### Workflow 2: Daily Briefing

1. **8:00 AM** - Scheduled Claude task runs
2. **Claude reads:**
   - `/Done` (what you completed)
   - `/Plans` (what's planned)
   - `/Logs` (activity log)
3. **Claude writes:** `/Briefings/2026-02-17_Morning.md`
4. **Dashboard updates** with summary

### Workflow 3: Task Processing

1. **New item arrives** → Watcher captures
2. **Claude analyzes** → Creates action plan
3. **Plan shows steps** → Some might need approval
4. **You review plan** → Approve or reject
5. **Claude executes** → Updates logs and Done folder

---

## 🔒 Security Best Practices

### 1. Credentials

❌ **NEVER** store in vault:
- API keys
- Passwords
- Bank tokens
- OAuth tokens

✅ **DO** use environment variables:

```bash
export GMAIL_API_KEY="your_key"
export BANK_TOKEN="your_token"

# Then in Python/Claude:
import os
api_key = os.getenv('GMAIL_API_KEY')
```

### 2. Dry-Run First

```bash
# Test without executing
python filesystem_watcher.py --demo
claude "Process files (dry-run only)"
```

### 3. Audit Logs

Check `/Logs/` daily for activity:

```bash
# View today's log
cat AI_Employee_Vault/Logs/2026-02-17.json | jq '.'

# Search for specific action
grep "payment" AI_Employee_Vault/Logs/*.json
```

### 4. Approval Always

When in doubt, require approval:
- Add threshold to `Company_Handbook.md`
- Create approval request file
- Have Claude wait for your decision

---

## 🧪 Testing

### Test 1: File Detection

```bash
# Create test file
echo "# Test Task" > test.md

# Run watcher in demo mode
python filesystem_watcher.py \
  --vault ./AI_Employee_Vault \
  --watch . \
  --demo

# Should show: "Test Task" file detected
```

### Test 2: Vault Connectivity

```bash
# Verify Claude can read vault
claude "List all files in /Needs_Action"

# Should show vault structure
```

### Test 3: Task Processing

```bash
# Create test task
cat > AI_Employee_Vault/Needs_Action/TEST_001.md << 'EOF'
---
type: test
status: pending
---

# Test Task

This is a test task for processing.
EOF

# Have Claude process it
claude "Process TEST_001.md and create a plan"

# Verify plan was created
ls AI_Employee_Vault/Plans/
```

---

## 📊 Monitoring & Maintenance

### Daily (2 minutes)
- Check Dashboard.md
- Review any alerts in `/Logs`

### Weekly (15 minutes)
- Review `/Done` folder
- Check approval audit trail
- Read briefing report

### Monthly (1 hour)
- Full security review
- Update Company_Handbook if needed
- Backup vault to external storage

---

## 🐛 Troubleshooting

### Claude Can't Read Vault

```bash
# Check permissions
ls -la AI_Employee_Vault/

# Should show: drwxrwxrwx (readable by all)

# Fix if needed
chmod 755 AI_Employee_Vault
```

### Watcher Not Detecting Files

```bash
# Check if watchdog installed
python -c "import watchdog; print('OK')"

# If error, install:
pip install watchdog

# Verify watch folder exists:
ls -la ~/Downloads/  # (or your watch folder)
```

### Claude Permission Denied

```bash
# Make sure running from right directory
cd AI_Employee_Vault
claude --version

# Or use absolute path
claude --cwd /full/path/to/AI_Employee_Vault "list files"
```

---

## 🎓 Next Steps

Once Bronze Tier is working:

1. **Add Email Watcher** → Process actual emails
2. **Create MCP Servers** → Execute real actions
3. **Implement Scheduling** → Automatic daily runs
4. **Add More Skills** → Custom agent skills
5. **Upgrade to Silver** → Multiple watchers, LinkedIn posting

---

## 📚 Resources

### Documentation
- [Obsidian Documentation](https://help.obsidian.md)
- [Claude Code Guide](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### Code Templates
- `base_watcher.py` - Template for creating watchers
- `filesystem_watcher.py` - File drop monitoring
- `.claude/skills/` - Agent Skills templates

### Example Files
- `Dashboard.md` - Real-time summary template
- `Company_Handbook.md` - Rules of engagement
- Agent Skills in `.claude/skills/`

---

## ✅ Bronze Tier Checklist

- [ ] Obsidian vault created and opened
- [ ] Dashboard.md configured
- [ ] Company_Handbook.md rules defined
- [ ] base_watcher.py tested
- [ ] filesystem_watcher.py running (test mode)
- [ ] Claude Code verified with vault
- [ ] Test task processed successfully
- [ ] Approval workflow tested
- [ ] Logs being created
- [ ] All files moved to vault

---

## 🎉 Congratulations!

You now have a working **Bronze Tier AI Employee** that:
- ✅ Monitors your file system
- ✅ Organizes tasks automatically
- ✅ Creates action plans
- ✅ Manages approvals
- ✅ Maintains audit logs
- ✅ Keeps everything in Obsidian

**Next milestone:** Add email monitoring for Silver Tier!

---

*Bronze Tier Implementation Guide | Personal AI Employee Hackathon*
*Generated: 2026-02-17*
