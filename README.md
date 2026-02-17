# 🤖 Personal AI Employee - Bronze Tier

**Build Your Own AI Employee in 8-12 Hours**

A complete, local-first implementation of an autonomous AI agent that manages your personal and business affairs using Claude Code and Obsidian.

---

## 🎯 What is This?

Personal AI Employee transforms Claude Code into a **24/7 digital assistant** that:

- 📥 **Captures** tasks and communications automatically
- 🧠 **Thinks** about what needs to be done
- ✅ **Plans** actions with checkboxes and steps
- ⏳ **Waits** for your approval on sensitive items
- 🚀 **Executes** approved actions
- 📋 **Reports** everything in audit logs
- 🎓 **Learns** from Company_Handbook.md rules

**Local-First:** Everything stays on your computer. Privacy guaranteed.

---

## 🥉 Bronze Tier Features

This is the **minimum viable deliverable** for the hackathon:

✅ **Obsidian Vault**
- Dashboard.md - Real-time summary
- Company_Handbook.md - Rules of engagement
- Folder structure for workflow

✅ **One Working Watcher**
- FileSystem watcher for new items
- Monitors specified folder
- Creates action files automatically

✅ **Claude Code Integration**
- Reads vault files
- Creates action plans
- Manages approvals
- Updates dashboard

✅ **Agent Skills**
- /process-inbox - Process tasks
- /generate-briefing - Create reports
- /manage-approvals - Handle workflow

✅ **Audit Trail**
- Comprehensive logging
- JSON activity records
- 90-day retention

---

## 📁 Project Structure

```
Personal-AI-Employee/
│
├── 📄 README.md                 ← You are here
├── 📄 BRONZE_SETUP.md          ← Quick start guide
├── 📄 INTEGRATION_GUIDE.md      ← Claude integration
│
├── 🐍 base_watcher.py          ← Template for watchers
├── 🐍 filesystem_watcher.py    ← File drop monitoring
│
├── 🏛️ AI_Employee_Vault/
│   ├── 📄 Dashboard.md         ← Real-time summary
│   ├── 📄 Company_Handbook.md  ← Rules of engagement
│   │
│   ├── 📁 Needs_Action/        ← Input folder
│   ├── 📁 Plans/               ← Action plans
│   ├── 📁 Done/                ← Completed work
│   ├── 📁 Pending_Approval/    ← Awaiting your decision
│   ├── 📁 Approved/            ← Ready to execute
│   ├── 📁 Rejected/            ← Declined items
│   ├── 📁 Logs/                ← Audit trail
│   │
│   └── 📁 .claude/skills/      ← Agent Skills
│       ├── process-inbox/
│       ├── generate-briefing/
│       └── manage-approvals/
│
└── 🐍 run_ai_employee.sh       ← Daily scheduler
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Open Vault in Obsidian

```bash
# Open Obsidian
# File → Open folder as vault
# Select: AI_Employee_Vault/
```

You should see the vault structure with Dashboard.md visible.

### 2. Verify Claude Code

```bash
claude --version  # Should show version
```

### 3. Test Watcher

```bash
# Test filesystem watcher
python filesystem_watcher.py \
  --vault ./AI_Employee_Vault \
  --watch ~/Downloads \
  --demo
```

Expected output: ✅ FileSystem Watcher initialized

### 4. Test Claude Integration

```bash
cd AI_Employee_Vault
claude "List all files in the vault"
```

Expected: Claude shows vault structure

### 5. Create Test Task

```bash
# Create test file
echo "# Test Task" > AI_Employee_Vault/Needs_Action/TEST_001.md

# Have Claude process it
cd AI_Employee_Vault
claude /process-inbox

# Check results
ls Plans/   # Should show new plan
ls Logs/    # Should show log entry
```

✅ **If all 5 steps work, you're ready!**

---

## 📖 Documentation

Start here based on your needs:

### 🏃 I Want to Run It Fast
→ Read: **[BRONZE_SETUP.md](BRONZE_SETUP.md)** (30-60 minutes)

### 🔧 I Want to Integrate with Claude
→ Read: **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** (1-2 hours)

### 🎓 I Want to Understand Architecture
→ Read: **[Technical Details](#technical-details)** below

### 📚 I Want Full Hackathon Details
→ Read: **[Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md](Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)**

---

## 🏗️ Technical Details

### Architecture

```
┌──────────────────────────┐
│  Your Computer (You)     │
├──────────────────────────┤
│  • Browser               │
│  • Email client          │
│  • File explorer         │
└─────────┬────────────────┘
          │ drop files
          ↓
┌──────────────────────────┐
│  File System Watcher     │  (Python)
│  • Monitors ~/Downloads  │
│  • Creates .md files     │
└─────────┬────────────────┘
          │ new files appear
          ↓
┌──────────────────────────┐
│  Obsidian Vault          │  (Local files)
│  • /Needs_Action/        │
│  • Dashboard.md          │
│  • Company_Handbook.md   │
└─────────┬────────────────┘
          │ reads & writes
          ↓
┌──────────────────────────┐
│  Claude Code             │  (AI reasoning)
│  • Analyzes              │
│  • Plans                 │
│  • Decides               │
└─────────┬────────────────┘
          │ file moves
          ↓
┌──────────────────────────┐
│  /Approved folder        │  (human decision)
│  • Ready to execute      │
└──────────────────────────┘
```

### Workflow: From File to Done

```
1. FILE DETECTION (Watcher)
   └─ New file in ~/Downloads
   └─ Creates FILE_*.md in /Needs_Action

2. ANALYSIS (Claude)
   └─ Reads /Needs_Action
   └─ Creates PLAN_*.md
   └─ If needs approval: creates approval file

3. APPROVAL (You)
   └─ Review approval request
   └─ Move to /Approved (or /Rejected)

4. EXECUTION (Claude + MCP)
   └─ Detects approved file
   └─ Executes action
   └─ Logs result

5. COMPLETION (Organization)
   └─ Moves to /Done
   └─ Updates Dashboard
   └─ Records in Logs
```

### Key Files

| File | Purpose | Edited By |
|------|---------|-----------|
| `Dashboard.md` | Real-time summary | Claude |
| `Company_Handbook.md` | Rules & policies | You |
| `Needs_Action/*.md` | Input tasks | Watcher |
| `Plans/PLAN_*.md` | Action plans | Claude |
| `Pending_Approval/*.md` | Awaiting decision | Claude |
| `Approved/*.md` | Ready to execute | You |
| `Done/*.md` | Completed work | Claude |
| `Logs/*.json` | Audit trail | Claude |

---

## 🤝 Using Agent Skills

Skills are reusable AI-powered tasks. Once installed, use like commands:

### Available Skills

```bash
# Process all items in Needs_Action
/process-inbox

# Generate daily briefing
/generate-briefing --period daily

# Manage approval workflow
/manage-approvals review
```

### Running Skills

```bash
cd AI_Employee_Vault

# Run a skill
/process-inbox

# Run with options
/generate-briefing --period weekly --include-financials

# Check skill status
claude "What skills are available?"
```

---

## 🔐 Security & Privacy

### What's Protected

✅ Everything stays local on your machine
✅ No cloud sync (optional: you can add git)
✅ Credentials never in vault (use .env)
✅ All actions logged and reviewable
✅ Human approval required for sensitive items

### Best Practices

```bash
# 1. Create .env for secrets
cat > .env << 'EOF'
GMAIL_API_KEY=your_key
BANK_TOKEN=your_token
EOF

# 2. Add to .gitignore
echo ".env" >> .gitignore

# 3. Load before running
set -a
source .env
set +a
claude "process inbox"
```

### Audit Your AI

```bash
# Check what Claude did today
cat AI_Employee_Vault/Logs/2026-02-17.json | jq '.'

# Search for payments
grep -r "payment" AI_Employee_Vault/Logs/

# Review actions taken
cat AI_Employee_Vault/Done/*.md
```

---

## 🧪 Testing Checklist

Before running in production, test:

- [ ] Obsidian vault opens without errors
- [ ] Claude can read vault files
- [ ] FileSystem watcher detects new files
- [ ] Test task creates plan successfully
- [ ] Approval workflow works (manual move)
- [ ] Dashboard updates after processing
- [ ] Logs are created
- [ ] Company_Handbook rules are respected

---

## 🐛 Troubleshooting

### Claude can't read vault

```bash
# Check directory exists
ls -la AI_Employee_Vault/

# Make sure Claude is running from vault directory
cd AI_Employee_Vault
claude "list files"
```

### Watcher not detecting files

```bash
# Install watchdog
pip install watchdog

# Test watch folder exists
ls ~/Downloads/

# Run watcher in demo mode
python filesystem_watcher.py \
  --vault ./AI_Employee_Vault \
  --watch ~/Downloads \
  --demo
```

### Files not moving to Done

```bash
# Check permissions
ls -la AI_Employee_Vault/Done/

# Claude might need approval first
# Check /Pending_Approval folder
ls AI_Employee_Vault/Pending_Approval/
```

More troubleshooting in **[BRONZE_SETUP.md](BRONZE_SETUP.md#-troubleshooting)**

---

## 📈 Next Levels

Once Bronze is working, upgrade to:

### 🥈 Silver Tier (20-30 hours)
- Email watcher (Gmail)
- WhatsApp integration
- LinkedIn posting
- Multiple watchers
- MCP servers

### 🥇 Gold Tier (40+ hours)
- Full business integration
- Odoo accounting system
- Facebook & Instagram
- CEO briefings
- Advanced Ralph Wiggum loop

### 🔷 Platinum Tier (60+ hours)
- Cloud deployment
- Always-on agent
- Multi-agent coordination
- Advanced delegation

See full requirements in the hackathon document.

---

## 🤖 Agent Skills Reference

### `/process-inbox`

Processes all items in `/Needs_Action`:
- Analyzes each item
- Creates action plans
- Identifies items needing approval
- Organizes by priority

```bash
/process-inbox --verbose --dry-run
```

### `/generate-briefing`

Creates executive briefing:
- Summarizes completed tasks
- Analyzes financial data
- Identifies bottlenecks
- Makes recommendations

```bash
/generate-briefing --period daily --include-financials
```

### `/manage-approvals`

Handles approval workflow:
- Reviews pending approvals
- Executes approved actions
- Escalates urgent items
- Maintains audit trail

```bash
/manage-approvals review --priority high
```

---

## 📚 Learning Resources

### Official Documentation
- [Obsidian Help](https://help.obsidian.md)
- [Claude Code Guide](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)

### Video Tutorials
- [Claude Code + Obsidian Integration](https://www.youtube.com/watch?v=sCIS05Qt79Y)
- [Building Claude Agent Teams](https://www.youtube.com/watch?v=0J2_YGuNrDo)
- [Claude Agent Skills](https://www.youtube.com/watch?v=nbqqnl3JdR0)

### Community
- Hackathon Discussion: [Research Meeting on Zoom](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- Recording & Materials: [@panaversity on YouTube](https://www.youtube.com/@panaversity)

---

## 📝 File Templates

### Adding to Needs_Action

```yaml
---
type: task | email | file_drop | message
status: pending
priority: low | medium | high
from: source_info
created: 2026-02-17T10:00:00Z
---

# Task Title

Description of what needs to be done.

## Details
- Item 1
- Item 2
```

### Creating Approvals

```yaml
---
type: approval_request
action: email | payment | post | other
priority: medium
created: 2026-02-17T10:00:00Z
expires: 2026-02-18T10:00:00Z
---

## What Will Happen

[Description of action]

## To Approve
Move this file to `/Approved`

## To Reject
Move this file to `/Rejected`
```

---

## ✅ Submission Checklist

Before submitting to hackathon:

- [ ] All Bronze requirements met
- [ ] README.md updated with setup instructions
- [ ] Code is well-commented
- [ ] Security handled (no credentials in code)
- [ ] Tested and working
- [ ] Demo video recorded (5-10 min)
- [ ] GitHub repository public/shared
- [ ] Tier declaration: Bronze ✅
- [ ] Submit via form: [Submission Form](https://forms.gle/JR9T1SJq5rmQyGkGA)

---

## 🎉 Success Criteria

Your Bronze Tier is complete when:

✅ Vault opens in Obsidian without errors
✅ FileSystem watcher successfully detects files
✅ Claude Code processes items and creates plans
✅ Approval workflow works (manual move to /Approved)
✅ Logs are created and tracking actions
✅ Dashboard updates reflect activity
✅ All files use proper markdown frontmatter
✅ Audit trail is maintained

---

## 💡 Tips for Success

1. **Start simple** - Get basic workflow working before adding features
2. **Test incrementally** - Test each component before integrating
3. **Document your rules** - Keep Company_Handbook.md clear and updated
4. **Check logs regularly** - Review `/Logs/` to understand what Claude does
5. **Use dry-run** - Test actions before approving
6. **Backup vault** - Regular git commits or backups
7. **Iterate quickly** - Small improvements compound

---

## 📞 Support & Questions

### Getting Help

1. Check documentation first:
   - [BRONZE_SETUP.md](BRONZE_SETUP.md)
   - [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
   - Troubleshooting sections

2. Review examples:
   - Look at existing `.md` files in vault
   - Check `/Logs/` for patterns
   - Test with simple examples first

3. Ask Claude:
   ```bash
   claude "Help me troubleshoot: [your issue]"
   ```

4. Community:
   - Wednesday Research Meetings
   - Hackathon discussion channel
   - Review others' implementations

---

## 📄 License

This implementation is part of the Personal AI Employee Hackathon.

Created: 2026-02-17
Version: 0.1-bronze
Status: Ready for deployment

---

## 🎓 What You'll Learn

By building this, you'll understand:
- ✅ How to orchestrate Claude Code as an autonomous agent
- ✅ File-based workflows and state management
- ✅ Human-in-the-loop approval patterns
- ✅ Audit logging and compliance
- ✅ Local-first privacy architecture
- ✅ Agent skills and reusable automation

**This is not just a project—it's a blueprint for AI Employee architecture.**

---

## 🚀 Ready to Build?

1. **Start here:** Read [BRONZE_SETUP.md](BRONZE_SETUP.md)
2. **Then integrate:** Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
3. **Test everything:** Follow testing checklist
4. **Submit:** Record demo and submit via form

Good luck! The future of autonomous agents is yours to build. 🤖

---

*Personal AI Employee Hackathon*
*Bronze Tier Complete Implementation*
*Built with Claude Code + Obsidian*
*2026-02-17*
