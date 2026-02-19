# Process Inbox Skill

## Description

Automatically processes items in the `/Needs_Action` folder, categorizes them, creates action plans, and manages the workflow through the vault.

## What This Skill Does

1. **Scans** `/Needs_Action` folder for new items
2. **Analyzes** each item to determine required action
3. **Creates** plan files in `/Plans` with actionable steps
4. **Identifies** items requiring human approval
5. **Moves** completed items to `/Done`
6. **Updates** Dashboard with summary

## Usage

Use this skill when you need Claude to:
- Process emails that have been captured
- Organize and categorize incoming tasks
- Create action plans automatically
- Triage items requiring approval vs auto-processing

## Example Commands

```bash
# Process all items in Needs_Action
/process-inbox

# Process with detailed logging
/process-inbox --verbose

# Dry-run mode (show what would happen)
/process-inbox --dry-run
```

## Input Files

The skill expects markdown files in `/Needs_Action` with frontmatter:

```yaml
---
type: email | task | file_drop | message
status: pending
priority: low | medium | high
from: sender_info
---

## Content
Description of the item to process
```

## Output

Creates files in:
- `/Plans/PLAN_*.md` - Detailed action plans
- `/Pending_Approval/*.md` - Items requiring approval
- `/Done/*.md` - Completed items

## Example Output

```yaml
---
type: action_plan
created: 2026-02-17T10:00:00Z
source: email_from_client
priority: high
status: pending_approval
---

## Objective
Send invoice to Client A

## Steps
- [x] Identified client email
- [x] Located invoice
- [ ] Requires approval to send

## Approval Needed
Move to /Pending_Approval for human review
```

## Safety Features

- **Human-in-the-loop** for sensitive actions
- **Dry-run mode** to test without changes
- **Detailed logging** of all decisions
- **Reversible operations** only (no deletions)

## Related Skills

- [`generate-briefing`](../generate-briefing/SKILL.md) - Create business briefings
- [`manage-approvals`](../manage-approvals/SKILL.md) - Handle approval workflows

## Requirements

- Obsidian vault with standard folder structure
- Claude Code with file system access
- `.md` files in `/Needs_Action` folder
