# Manage Approvals Skill

## Description

Handles the human-in-the-loop approval workflow, monitoring pending approvals and executing actions based on approval decisions.

## What This Skill Does

1. **Monitors** `/Pending_Approval` folder for review
2. **Categorizes** approval requests by type and urgency
3. **Executes** approved actions from `/Approved` folder
4. **Logs** all approval decisions and actions
5. **Escalates** urgent items needing immediate attention
6. **Cleans up** completed approvals to `/Done`

## Usage

Use this skill to:
- Review pending approvals
- Execute approved actions
- Track approval status
- Escalate urgent items
- Log compliance trail

## Example Commands

```bash
# Review all pending approvals
/manage-approvals review

# Show only high-priority approvals
/manage-approvals review --priority high

# Execute approved actions
/manage-approvals execute

# Summarize approval status
/manage-approvals status

# Archive completed approvals
/manage-approvals archive
```

## Approval Types

### ✅ Auto-Approve (No Action Needed)
- File organization
- Task categorization
- Draft creation
- Internal planning

### ⏳ Requires Approval
- Email sending to new contacts
- Social media posts
- Payments > $50
- Calendar invitations
- File movements outside vault

### 🚫 Always Escalate
- Payments > $200
- New service integrations
- Sensitive communications
- Legal/contract matters

## Approval File Format

Create approval request in `/Pending_Approval`:

```yaml
---
type: approval_request
action: email | payment | post | other
priority: low | medium | high
amount: 0.00
created: 2026-02-17T10:00:00Z
expires: 2026-02-18T10:00:00Z
status: pending
---

## Approval Request

### Action
[Description of what will happen]

### Details
- **To/Recipient:** [Target]
- **Amount:** $[Amount if applicable]
- **Content:** [What will be sent/posted]

### To Approve
Move this file to `/Approved/`

### To Reject
Move this file to `/Rejected/`

### Questions
[Space for notes/questions]
```

## Workflow

### Step 1: Review (Human)
1. Check `/Pending_Approval` folder
2. Read approval requests
3. Add notes if needed
4. Move to `/Approved/` or `/Rejected/`

### Step 2: Execute (Skill)
1. Detect moved files
2. Execute approved action via MCP
3. Log result
4. Move to `/Done/`

### Step 3: Audit (Human)
1. Review `/Done/` to verify execution
2. Check logs for any issues
3. Provide feedback if needed

## Example Scenarios

### Email Approval
```yaml
---
type: approval_request
action: email
priority: medium
to: client@example.com
---

## Send Email: January Invoice

To: client@example.com
Subject: January 2026 Invoice

[Email body preview]

Status: Ready to send. Move to /Approved to proceed.
```

### Payment Approval
```yaml
---
type: approval_request
action: payment
priority: high
amount: 150.00
---

## Payment Authorization

**To:** Client Services
**Amount:** $150.00
**Reason:** Monthly subscription

Move to /Approved to authorize.
```

### Social Media Approval
```yaml
---
type: approval_request
action: post
priority: medium
platform: linkedin
---

## Post to LinkedIn

[Post preview]

Scheduled for: 2026-02-17 09:00 UTC

Approve to post now or move to /Approved to schedule.
```

## Audit Trail

All approvals logged to `/Logs/` in format:

```json
{
  "timestamp": "2026-02-17T10:30:00Z",
  "action_type": "email_send",
  "approval_status": "approved",
  "approved_by": "human_manual_move",
  "actor": "manage_approvals_skill",
  "target": "client@example.com",
  "parameters": {
    "subject": "Invoice #123"
  },
  "result": "success"
}
```

## Safety Features

- **Human authorization required** for all sensitive actions
- **Expiration dates** on approval requests (auto-cancel if expired)
- **Explicit moves** - Accidental actions prevented
- **Full audit trail** - Every decision logged
- **Dry-run mode** - Test workflow without executing

## Related Skills

- [`process-inbox`](../process-inbox/SKILL.md) - Create approval requests
- [`generate-briefing`](../generate-briefing/SKILL.md) - Review decisions

## Approval Thresholds

Reference your `Company_Handbook.md`:

| Action | Auto-Approve | Requires Approval | Always Escalate |
|--------|--------------|-------------------|-----------------|
| Email (known contact) | ✅ | | |
| Email (new contact) | | ✅ | |
| Payment < $50 | ✅ | | |
| Payment $50-$200 | | ✅ | |
| Payment > $200 | | | 🚫 |
| Social post | | ✅ | |

## Requirements

- Obsidian vault with approval folders
- Claude Code with file system access
- MCP servers for external actions (email, payments, etc.)
- Company_Handbook.md defining approval rules
