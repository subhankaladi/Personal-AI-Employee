# 🔌 Claude Code + Obsidian Integration Guide

**Purpose:** Step-by-step instructions for integrating Claude Code with your AI Employee vault

---

## 🎯 Integration Overview

Claude Code will interact with your Obsidian vault using:
1. **File System Tools** - Read/write markdown files
2. **Folder Watching** - Monitor for new items
3. **Agent Skills** - Reusable AI-powered tasks
4. **MCP Servers** - External integrations (email, payments, etc.)

---

## 📋 Step 1: Vault Configuration

### 1.1 Verify Vault Exists

```bash
# From your project directory
ls -la AI_Employee_Vault/

# Should show:
# Dashboard.md
# Company_Handbook.md
# Needs_Action/
# Plans/
# Done/
# ... (other folders)
```

### 1.2 Create .vault-metadata

Add metadata file to help Claude understand structure:

```bash
cat > AI_Employee_Vault/.vault-metadata.json << 'EOF'
{
  "name": "AI Employee Vault",
  "version": "0.1-bronze",
  "tier": "bronze",
  "structure": {
    "input": "Needs_Action",
    "processing": "Plans",
    "approval": "Pending_Approval",
    "approved": "Approved",
    "rejected": "Rejected",
    "output": "Done",
    "logs": "Logs",
    "accounting": "Accounting"
  },
  "rules_file": "Company_Handbook.md",
  "dashboard": "Dashboard.md"
}
EOF
```

### 1.3 Create .gitignore

Protect sensitive files:

```bash
cat > AI_Employee_Vault/.gitignore << 'EOF'
# Secrets
.env
.env.local
secrets.json
credentials.json
*.key

# Logs (optional)
Logs/*.json

# OS files
.DS_Store
thumbs.db
EOF
```

---

## 🤖 Step 2: Claude Code Configuration

### 2.1 Verify Claude Installation

```bash
claude --version
# Output: Claude Code version X.X.X
```

### 2.2 Configure Claude for Vault

The simplest approach: **Run Claude from vault directory**

```bash
cd /path/to/AI_Employee_Vault

# Now Claude commands can reference files directly:
claude "List contents of Needs_Action folder"
claude "Read Dashboard.md and summarize"
```

### 2.3 Using Absolute Paths (Alternative)

If running from elsewhere:

```bash
# Use --cwd flag
claude --cwd /full/path/to/AI_Employee_Vault \
  "Process /Needs_Action folder"

# Or set environment variable
export CLAUDE_VAULT="/full/path/to/AI_Employee_Vault"
claude "Read $CLAUDE_VAULT/Dashboard.md"
```

---

## 📖 Step 3: Agent Skills Setup

### 3.1 Create Skills Directory

```bash
mkdir -p AI_Employee_Vault/.claude/skills
```

### 3.2 Available Skills (Already Included)

```
.claude/skills/
├── process-inbox/
│   └── SKILL.md         # Process /Needs_Action items
├── generate-briefing/
│   └── SKILL.md         # Create CEO briefing
└── manage-approvals/
    └── SKILL.md         # Handle approvals
```

### 3.3 Using Skills in Claude

```bash
# From vault directory:
cd AI_Employee_Vault

# Invoke skill
/process-inbox

# Invoke with options
/generate-briefing --period daily

# Manage approvals
/manage-approvals review
```

### 3.4 Creating Custom Skills (Optional)

To add your own skill:

```bash
# Create skill directory
mkdir -p .claude/skills/my-skill

# Create SKILL.md with:
# - Description
# - Usage examples
# - Input/output formats

# Then use it:
/my-skill --option value
```

---

## 🔄 Step 4: Workflow Automation

### 4.1 Basic Workflow Script

Create `run_ai_employee.sh`:

```bash
#!/bin/bash
# AI Employee Daily Run

VAULT_PATH="/path/to/AI_Employee_Vault"

echo "🤖 AI Employee - Starting Daily Cycle"
echo "Time: $(date)"
echo ""

# 1. Process inbox
echo "📥 Processing Needs_Action folder..."
cd $VAULT_PATH
claude /process-inbox --verbose
echo ""

# 2. Generate briefing
echo "📋 Generating daily briefing..."
claude /generate-briefing --period daily
echo ""

# 3. Review approvals
echo "⏳ Checking pending approvals..."
claude /manage-approvals status
echo ""

echo "✅ Daily cycle complete"
echo ""
```

Make executable:
```bash
chmod +x run_ai_employee.sh

# Run it
./run_ai_employee.sh
```

### 4.2 Scheduling with Cron (Mac/Linux)

```bash
# Edit crontab
crontab -e

# Add line to run daily at 8 AM
0 8 * * * /path/to/run_ai_employee.sh >> /path/to/logs/cron.log 2>&1
```

### 4.3 Scheduling with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task:
   - Name: `AI Employee Daily`
   - Trigger: Daily at 8:00 AM
   - Action: Start program
   - Program: `python`
   - Args: `/path/to/run_ai_employee.py`

---

## 🔗 Step 5: File System Integration

### 5.1 Connect FileSystem Watcher

```bash
# From project root (not vault)
cd /path/to/Personal-AI-Employee

# Start watcher pointing to vault
python filesystem_watcher.py \
  --vault ./AI_Employee_Vault \
  --watch ~/Downloads \
  --exclude .DS_Store thumbs.db
```

### 5.2 Create a Monitor Script

```python
# monitor_vault.py
import subprocess
import sys
from pathlib import Path

def main():
    vault_path = Path('AI_Employee_Vault').absolute()
    watch_folder = Path('~/Downloads').expanduser()

    # Keep watcher running
    cmd = [
        'python', 'filesystem_watcher.py',
        '--vault', str(vault_path),
        '--watch', str(watch_folder)
    ]

    print(f"🚀 Starting vault monitor...")
    print(f"   Vault: {vault_path}")
    print(f"   Watch: {watch_folder}")

    subprocess.run(cmd)

if __name__ == '__main__':
    main()
```

---

## 🧠 Step 6: Prompt Templates

### 6.1 Process Inbox Prompt

```
You are an AI Employee managing a personal vault.
Your Company_Handbook.md defines your rules.

TASK: Process all items in /Needs_Action

For each item:
1. Read the markdown file
2. Understand the request
3. Create a detailed action plan in /Plans
4. If approval needed, create file in /Pending_Approval
5. When done, summarize in /Logs

Use the /process-inbox skill if available.

Remember: Always respect Company_Handbook.md rules.
```

### 6.2 Briefing Generation Prompt

```
You are generating a CEO briefing for today.

TASK: Create a briefing report

Include:
1. Summary of completed tasks from /Done
2. Key metrics (files in /Accounting if present)
3. Pending items in /Plans
4. Alerts from /Logs
5. Recommendations for tomorrow

Output: Create /Briefings/YYYY-MM-DD_Briefing.md

Format as markdown with sections.
```

### 6.3 Approval Management Prompt

```
You are managing the approval workflow.

TASK: Process approvals

Steps:
1. Check /Pending_Approval for new requests
2. List pending items
3. For approved (moved to /Approved):
   - Log action to /Logs
   - Move to /Done
4. For rejected (moved to /Rejected):
   - Log decision
   - Archive

Report summary of actions taken.
```

---

## 🔐 Step 7: Security Setup

### 7.1 Environment Variables

```bash
# Create .env file (NEVER commit this!)
cat > .env << 'EOF'
# AI Employee Configuration
VAULT_PATH=/path/to/AI_Employee_Vault

# External services (if using MCP)
GMAIL_API_KEY=your_key_here
BANK_API_TOKEN=your_token_here

# Settings
DRY_RUN=true  # Start in dry-run mode
CHECK_INTERVAL=300  # 5 minutes
MAX_ACTIONS_PER_HOUR=10
EOF

# Add to .gitignore
echo ".env" >> .gitignore
```

### 7.2 Load Environment

```bash
# Before running Claude
set -a
source .env
set +a

# Then run
claude "Process inbox"
```

### 7.3 Credential Management

```python
# Instead of hardcoding
import os

api_key = os.getenv('GMAIL_API_KEY')
if not api_key:
    raise ValueError('GMAIL_API_KEY not set in environment')
```

---

## 🧪 Step 8: Testing Integration

### Test 1: File Reading

```bash
cd AI_Employee_Vault
claude "Read and summarize Dashboard.md"
```

Expected: Claude outputs the dashboard content

### Test 2: File Writing

```bash
cd AI_Employee_Vault
claude "Create a test file: create /Needs_Action/TEST_INTEGRATION.md with content 'Test passed'"
```

Expected: File is created in Needs_Action

### Test 3: Folder Processing

```bash
cd AI_Employee_Vault

# Create test item
echo "---
type: test
---

# Test Task
Process this." > Needs_Action/TEST_001.md

# Have Claude process
claude /process-inbox

# Check Plans folder
ls Plans/  # Should show new plan file
```

### Test 4: Full Workflow

```bash
# Start with clean test
rm Needs_Action/TEST* Plans/PLAN* Done/TEST*

# Create test file
echo "---
type: test
priority: medium
---

# New Task

This is a test task." > Needs_Action/TEST_FULL.md

# Process with Claude
claude "Process /Needs_Action/TEST_FULL.md and create plan"

# Verify outputs
ls Plans/
ls Logs/

# Run daily briefing
claude /generate-briefing

# Check briefing
ls Briefings/
```

---

## 🚀 Step 9: Running Your AI Employee

### Quick Start

```bash
# Terminal 1: Watcher
python filesystem_watcher.py \
  --vault ./AI_Employee_Vault \
  --watch ~/Downloads

# Terminal 2: Claude (in another window)
cd AI_Employee_Vault
claude "Process all items and create daily briefing"
```

### Production Setup

```bash
# 1. Install PM2
npm install -g pm2

# 2. Create ecosystem config
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'ai-employee',
      script: 'run_ai_employee.sh',
      interpreter: 'bash',
      cron_restart: '0 8 * * *',  // Daily at 8 AM
      error_file: './logs/error.log',
      out_file: './logs/output.log'
    }
  ]
};
EOF

# 3. Start
pm2 start ecosystem.config.js

# 4. Monitor
pm2 monit
```

---

## 📊 Monitoring & Debugging

### View Logs

```bash
# Today's log
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.'

# Filter for errors
grep -i error AI_Employee_Vault/Logs/*.json
```

### Check Vault State

```bash
cd AI_Employee_Vault

# What's pending?
ls Needs_Action/

# What's being processed?
ls Plans/

# What was approved?
ls Approved/

# What's done?
ls Done/
```

### Test MCP Connection (Future)

```bash
# When implementing MCP servers
claude "List available MCP servers"
claude "Test email MCP connection"
```

---

## ✅ Integration Checklist

- [ ] Vault directory created with proper structure
- [ ] Dashboard.md exists and formatted
- [ ] Company_Handbook.md configured
- [ ] Claude Code verified working
- [ ] Agent Skills installed in .claude/skills/
- [ ] FileSystem Watcher tested
- [ ] Test workflow completed successfully
- [ ] Logs being created
- [ ] Cron/Task Scheduler configured (optional)
- [ ] .env file created and ignored
- [ ] PM2 installed (optional, for always-on)

---

## 🎓 Next: Connect External Services

Once integration is solid, add:
- **Gmail Watcher** for email
- **Email MCP Server** for sending
- **Browser MCP** for web automation
- **Bank API** for transactions

See `SILVER_SETUP.md` for Silver Tier requirements.

---

*Integration Guide | Personal AI Employee Hackathon | Bronze Tier*
