# /send-whatsapp - Send WhatsApp Message

**Status:** Silver Tier
**Category:** Communication
**Safety Level:** High (Requires Approval)

---

## Overview

Send WhatsApp messages through WhatsApp Web automation with built-in human approval workflow. Perfect for urgent client communications, status updates, and follow-ups.

## When to Use

Use this skill when:
- Responding to urgent client requests
- Sending time-sensitive updates
- Sharing files or documents
- Confirming meetings or deadlines
- Quick status checks with team

## Input Parameters

```yaml
recipient: "Contact Name"           # Required: Contact name (as in WhatsApp)
message: "Your message here"        # Required: Message text
is_urgent: false                    # Optional: Mark as urgent (faster approval)
file_path: "./document.pdf"         # Optional: File to attach
scheduled_time: "14:30"             # Optional: Schedule for later
```

## Process Flow

```
Input WhatsApp Request
        ↓
Validate Recipient (Known Contact?)
        ↓
Analyze Message (Length, Keywords, Urgency)
        ↓
If Urgent or New Contact → REQUIRES APPROVAL
If Known Contact + Brief → Draft Only
If Known Contact + Routine → Auto-Send (if enabled)
        ↓
Create Draft File in Pending_Approval/
        ↓
Human Reviews in Obsidian
        ↓
Move to /Approved/ → Execute Send
Move to /Rejected/ → Delete Draft
        ↓
Complete & Log Result
```

## Quick Examples

### Example 1: Urgent Message (Requires Approval)

```markdown
/send-whatsapp
recipient: "John Smith"
message: "Hi John, the project is ready for your review. Can you check it today?"
is_urgent: true
```

**Result:** Approval request created with urgent flag

### Example 2: Quick Status Update

```markdown
/send-whatsapp
recipient: "Client A"
message: "On track for delivery tomorrow ✓"
```

**Result:** Draft created, auto-approved if recipient is known

### Example 3: With Attachment

```markdown
/send-whatsapp
recipient: "Team Lead"
message: "Here's the latest report"
file_path: ./reports/monthly_report.pdf
```

**Result:** Message + attachment queued for approval

### Example 4: Scheduled Message

```markdown
/send-whatsapp
recipient: "Customer Support"
message: "Just checking in - how can I help?"
scheduled_time: "10:00"
```

**Result:** Message scheduled for 10:00 AM

## Safety Features

### Auto-Approval Conditions

Message can be auto-sent WITHOUT approval when:
- ✅ Recipient is in known contacts (WhatsApp_Contacts.md)
- ✅ Message < 200 characters
- ✅ Not marked as urgent
- ✅ No file attachments
- ✅ Less than 3 messages to same recipient in last hour
- ✅ Sent during working hours

### Approval Required When

Message REQUIRES approval when:
- ❌ Recipient is NEW (not in known contacts)
- ❌ Message > 200 characters
- ❌ Marked as urgent
- ❌ Contains file attachment
- ❌ Sent outside working hours
- ❌ Multiple recipients in thread

### Always Blocked

Message is REJECTED when:
- 🚫 Recipient name contains suspicious patterns
- 🚫 Message looks like spam or phishing
- 🚫 Rate limit exceeded (> 50 messages/hour)
- 🚫 Attachment is suspicious type

## Configuration (Company_Handbook.md)

Define your WhatsApp rules in `AI_Employee_Vault/Company_Handbook.md`:

```markdown
## WhatsApp Auto-Approve Rules

### Known Contacts (Quick responses OK)
- John Smith (Client)
- Manager (Direct supervisor)
- Team Support

### Message Tone
- Keep it brief
- Professional but friendly
- No informal slang

### Response Times
Aim to respond within 1 hour for urgent messages
Within 24 hours for routine messages

### When to Escalate
Flag if customer mentions complaints or issues
```

## Output Files

When message is ready to send:

**Location:** `AI_Employee_Vault/Pending_Approval/WHATSAPP_*.md`

**Format:**
```yaml
---
type: whatsapp_message
action: send
status: pending_approval
recipient: Contact Name
created: 2026-02-18T10:00:00Z
expires: 2026-02-18T18:00:00Z
is_urgent: false
---

# WhatsApp to Contact Name

## Message
Your message text here

## Attachments
None

## Metadata
- Contact: Contact Name
- Phone: (from WhatsApp)
- Last message: [date]

## To Approve
Move this file to `/Approved/` to send.

## To Reject
Move this file to `/Rejected/` to cancel.
```

## Human Workflow

1. **Review** - Open `Pending_Approval/WHATSAPP_*.md` in Obsidian
2. **Read** - Check message and recipient
3. **Decide:**
   - ✅ Approve: Drag file to `/Approved/` folder
   - ❌ Reject: Drag file to `/Rejected/` folder
   - ✏️ Edit: Move back to `/Needs_Action/`, modify, re-process
4. **Execute:** AI Employee detects moved file and sends message
5. **Audit:** Review `/Logs/` for send confirmation

## Audit Logging

Every message is logged:

```json
{
  "timestamp": "2026-02-18T10:15:30Z",
  "action_type": "whatsapp_send",
  "actor": "claude_code",
  "recipient": "John Smith",
  "message_preview": "Your message here",
  "status": "sent",
  "approved_by": "human",
  "approval_time": "2026-02-18T10:10:00Z",
  "send_time": "2026-02-18T10:15:30Z",
  "error": null
}
```

Location: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

## Limitations & Considerations

- WhatsApp requires keeping session active
- Message delivery depends on WhatsApp Web availability
- File attachments limited by WhatsApp (100MB typically)
- Scheduled messages stored locally until execution time
- No API integration (Web automation only)

## Troubleshooting

### "Session Expired" Error

**Solution:**
- Run: `python whatsapp_watcher.py --vault ./AI_Employee_Vault --setup`
- Manually scan QR code
- Session will be re-established

### "Contact Not Found" Error

**Solution:**
- Verify contact name matches exactly in WhatsApp
- Check for typos in contact name
- Contact may need to be added to WhatsApp first

### Message Not Sending

**Solution:**
- Check that file moved to `/Approved/`
- Verify WhatsApp Web is accessible
- Check logs for specific error

## Related Skills

- `/process-inbox` - Analyze incoming messages and create responses
- `/manage-approvals` - Review and execute pending approvals
- `/send-email` - Send email responses

## Performance & Limitations

| Aspect | Limit | Notes |
|--------|-------|-------|
| Message Length | 4,096 chars | WhatsApp limit |
| File Size | 100MB | WhatsApp typical limit |
| Attachments | 1 per message | Per WhatsApp rules |
| Rate Limit | 50/hour | Prevent spam |
| Approval Expiry | 24h | Auto-cancel old approvals |
| Response Time | 2-5 seconds | Via browser automation |

---

**Last Updated:** 2026-02-18
**Version:** 1.0 (Silver Tier)
**Stability:** Production Ready
