# /send-email - Send Email via Gmail

**Status:** Silver Tier
**Category:** Communication
**Safety Level:** High (Requires Approval)

---

## Overview

Send emails through Gmail with built-in human approval workflow. This skill enables the AI Employee to compose and send professional emails while maintaining human oversight over all outgoing communications.

## When to Use

Use this skill when:
- Responding to customer inquiries
- Sending invoices or proposals
- Following up on projects
- Notifying stakeholders
- Sending automated reports

## Input Parameters

```yaml
recipient: email@example.com              # Required: Single recipient
recipients: [email1@, email2@]           # Optional: Multiple recipients
subject: "Invoice #123"                   # Required: Email subject
body: "Please find attached..."           # Required: Email body (markdown supported)
cc: [cc@example.com]                     # Optional: CC recipients
bcc: [bcc@example.com]                   # Optional: BCC recipients
attachment_paths: [./invoice.pdf]        # Optional: Files to attach
reply_to: noreply@company.com            # Optional: Reply-to address
is_draft: false                           # Optional: Create draft without sending
priority: normal                          # Optional: normal|high|low
```

## Process Flow

```
Input Email Request
        ↓
Analyze Recipient (Known or New?)
        ↓
If New Recipient → REQUIRES APPROVAL
If Known Recipient + Auto-Approve → Draft Only
If Known Recipient + User Choice → Draft for Review
        ↓
Create Draft File in Pending_Approval/
        ↓
Log Action to Audit Trail
        ↓
Human Reviews in Obsidian
        ↓
Move to /Approved/ → Execute Send
Move to /Rejected/ → Delete Draft
        ↓
Complete & Log Result
```

## Quick Examples

### Example 1: Simple Reply (Known Contact)

```markdown
/send-email
recipient: john@client.com
subject: "Re: Project Status Update"
body: |
  Hi John,

  Thanks for checking in. Project Alpha is 80% complete and on track for delivery next week.

  Best regards,
  AI Assistant
```

**Result:** Draft created in `/Pending_Approval/EMAIL_draft_john.md`

### Example 2: New Contact (Requires Approval)

```markdown
/send-email
recipient: newclient@company.com
subject: "Partnership Opportunity"
body: |
  Hello,

  I'd like to introduce an exciting partnership opportunity...

  Looking forward to hearing from you.
priority: high
```

**Result:** Approval request created with high priority flag

### Example 3: Bulk Email (Multiple Recipients)

```markdown
/send-email
recipients:
  - alice@company.com
  - bob@company.com
  - carol@company.com
subject: "Weekly Status Report"
body: "Please see attached report."
cc: manager@company.com
```

**Result:** Three separate emails queued for approval

### Example 4: With Attachment

```markdown
/send-email
recipient: client@example.com
subject: "Invoice Attached"
body: |
  Please find your invoice attached.

  Thank you!
attachment_paths:
  - ./invoices/INV-2026-001.pdf
```

## Safety Features

### Auto-Approval Conditions

Email can be auto-sent WITHOUT approval when:
- ✅ Recipient is in known contacts list (Company_Handbook.md)
- ✅ Email body < 500 characters
- ✅ No external links (http://, https://)
- ✅ Sent during working hours (configurable in .env)
- ✅ Less than 5 emails to same recipient in last hour

### Approval Required When

Email REQUIRES approval when:
- ❌ Recipient is NEW (not in known contacts)
- ❌ Email > 500 characters
- ❌ Contains external links or attachments
- ❌ Priority marked as HIGH
- ❌ Sent outside working hours
- ❌ Multiple recipients (CC/BCC)
- ❌ Contains sensitive keywords (contract, payment, urgent, legal)

### Always Blocked

Email is REJECTED when:
- 🚫 Recipient contains suspicious patterns (typos in domain)
- 🚫 Sender would be someone other than your account
- 🚫 Attachment is executable or suspicious type
- 🚫 Email looks like spam or phishing
- 🚫 Rate limit exceeded (> 20 emails/hour)

## Configuration (Company_Handbook.md)

Define your email rules in `AI_Employee_Vault/Company_Handbook.md`:

```markdown
## Email Auto-Approve Rules

### Known Contacts (Auto-Approve)
- john@client.com
- manager@company.com
- support@vendor.com

### Signature
All emails signed with:
"Best regards,
AI Assistant (powered by Claude)"

### Response Time
Aim to respond within 24 hours of receipt.

### Email Tone
- Professional but friendly
- Clear and concise
- Always proof-read before approval
```

## Output Files

When email is ready to send:

**Location:** `AI_Employee_Vault/Pending_Approval/EMAIL_*.md`

**Format:**
```yaml
---
type: email
action: send
status: pending_approval
recipient: email@example.com
subject: "Subject Line"
created: 2026-02-18T10:00:00Z
expires: 2026-02-19T10:00:00Z
priority: normal
---

# Email to email@example.com

## Subject
Subject Line

## Body
[Full email text here]

## Metadata
- To: email@example.com
- CC: cc@example.com
- Attachments: 0

## To Approve
Move this file to `/Approved/` to send.

## To Reject
Move this file to `/Rejected/` to cancel.
```

## Human Workflow

1. **Review** - Open `Pending_Approval/EMAIL_*.md` in Obsidian
2. **Read** - Check subject, body, recipient
3. **Decide:**
   - ✅ Approve: Drag file to `/Approved/` folder
   - ❌ Reject: Drag file to `/Rejected/` folder
   - ✏️ Edit: Move back to `/Needs_Action/`, make changes, re-process
4. **Execute:** AI Employee detects moved file and sends email
5. **Audit:** Review `/Logs/` for send confirmation

## Audit Logging

Every email action is logged:

```json
{
  "timestamp": "2026-02-18T10:15:30Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "email_id": "EMAIL_12345",
  "recipient": "john@client.com",
  "subject": "Project Status",
  "status": "sent",
  "approved_by": "human",
  "approval_time": "2026-02-18T10:10:00Z",
  "send_time": "2026-02-18T10:15:30Z",
  "error": null
}
```

Location: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

## Troubleshooting

### Email Won't Send

**Problem:** Approval not executing
- Check that file is in `/Approved/` (not `/Approved Draft/`)
- Ensure Gmail credentials are valid (.env, credentials.json)
- Check logs for error details

**Problem:** "Invalid recipient" error
- Verify email address format (user@domain.com)
- Check that Gmail account has send permission

**Problem:** "Attachment too large"
- Gmail limit is 25MB per message
- Compress files or use cloud storage link instead

### Email Requires Approval But Shouldn't

**Problem:** Auto-approve not working
- Check Company_Handbook.md has recipient listed
- Verify email body < 500 characters
- Ensure email has no links or attachments
- Check that rate limit not exceeded

## Related Skills

- `/process-inbox` - Analyze incoming emails and create responses
- `/generate-briefing` - Create email summary reports
- `/manage-approvals` - Review and execute pending approvals

## Performance & Limitations

| Aspect | Limit | Notes |
|--------|-------|-------|
| Email Size | 25MB | Gmail API limit |
| Recipients | 100 | Per single email |
| Attachments | 5 | Per email |
| Rate Limit | 20/hour | Prevent spam |
| Approval Expiry | 24h | Old approvals auto-cancel |
| Response Time | 2-5 seconds | Via MCP |

## Implementation Details

This skill:
1. Validates recipient and content
2. Checks auto-approve conditions
3. Creates markdown draft file
4. Logs to audit trail
5. Waits for human approval
6. Executes send via Gmail MCP
7. Logs send confirmation
8. Moves to Done/

Uses Gmail API v1 via MCP server (`mcp_servers/email_mcp.js`)

---

**Last Updated:** 2026-02-18
**Version:** 1.0 (Silver Tier)
**Stability:** Production Ready
