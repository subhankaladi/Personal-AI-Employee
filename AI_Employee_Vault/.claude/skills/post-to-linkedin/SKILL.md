# /post-to-linkedin - Post to LinkedIn

**Status:** Silver Tier
**Category:** Social Media
**Safety Level:** Medium (Requires Approval)

---

## Overview

Automatically generate and post professional content to LinkedIn to build business visibility and generate leads. This skill analyzes your completed work and creates engaging posts that showcase your expertise and value.

## When to Use

Use this skill when:
- Completing a major project milestone
- Sharing business insights or lessons learned
- Announcing new services or offerings
- Celebrating team achievements
- Building thought leadership content
- Generating visibility for business growth

## Input Parameters

```yaml
content: "Your post content"                # Required: Main post text
hashtags: ["#AI", "#Automation"]           # Optional: Relevant hashtags
image_path: "./screenshot.png"             # Optional: Image to attach
auto_generate: false                       # Optional: Auto-generate from recent work
source_file: "Done/PLAN_project.md"       # Optional: Source file for content
schedule_time: "10:00"                     # Optional: Schedule for later
```

## Process Flow

```
Input LinkedIn Post Request
        ↓
Auto-Generate Content (if requested)
  - Read recent completed tasks
  - Extract key achievements
  - Craft compelling narrative
        ↓
Validate Content
  - Check for brand voice alignment
  - Verify no sensitive data
  - Count characters
        ↓
Create Draft in Pending_Approval/
        ↓
Human Reviews in Obsidian
  - Read content
  - Add/edit hashtags
  - Optional: Add image
        ↓
Move to /Approved/ → Schedule/Publish
Move to /Rejected/ → Delete Draft
        ↓
Post Published & Analytics Tracked
```

## Quick Examples

### Example 1: Auto-Generate from Completed Work

```markdown
/post-to-linkedin
auto_generate: true
```

**Result:**
- Claude reads completed tasks from `Done/`
- Generates compelling LinkedIn post
- Creates draft with hashtags
- Requires approval before posting

### Example 2: Curated Post with Image

```markdown
/post-to-linkedin
content: |
  Just completed Project Alpha! Key learnings:

  1️⃣ Automation saves 85% of manual effort
  2️⃣ AI-powered workflows free up creative time
  3️⃣ Scale without hiring

  The future of work is here. 🚀
hashtags: ["#AI", "#Automation", "#Productivity"]
image_path: ./project_alpha_screenshot.png
```

**Result:** Post drafted with image, ready for approval

### Example 3: Scheduled Post

```markdown
/post-to-linkedin
content: "Weekly insight: The best time to automate is before it becomes critical."
hashtags: ["#BusinessAutomation"]
schedule_time: "10:00"
```

**Result:** Post scheduled for 10:00 AM

### Example 4: Generate from Specific File

```markdown
/post-to-linkedin
auto_generate: true
source_file: "Done/PROJECT_client_success.md"
```

**Result:** Post based on specific completed project

## Safety Features

### Auto-Approval Conditions

Post can be auto-published WITHOUT approval when:
- ✅ Content < 500 characters
- ✅ No external links or URLs
- ✅ No mentions of clients by name (generic reference OK)
- ✅ Matches brand voice guidelines
- ✅ Less than 1 post per day
- ✅ Scheduled (not immediate publish)

### Approval Required When

Post REQUIRES approval when:
- ❌ Content > 500 characters
- ❌ Contains external links
- ❌ Mentions clients or confidential projects
- ❌ Immediate publish (not scheduled)
- ❌ Includes statistics or claims
- ❌ Deviates from brand voice

### Always Blocked

Post is REJECTED when:
- 🚫 Contains sensitive company information
- 🚫 Violates LinkedIn terms of service
- 🚫 Looks like spam or promotional
- 🚫 Rate limit exceeded (> 3 posts/day)
- 🚫 Client confidentiality compromised

## Configuration (Company_Handbook.md)

Define your LinkedIn strategy in `AI_Employee_Vault/Company_Handbook.md`:

```markdown
## LinkedIn Posting Strategy

### Brand Voice
- Professional but conversational
- Focus on value and insights
- Show personality and passion
- Share lessons and learnings

### Posting Schedule
- Optimal times: 9 AM - 11 AM (weekdays)
- 3 posts per week maximum
- Mix of wins, insights, and engagement

### What to Post
✅ Project completions (generic)
✅ Industry insights
✅ Business lessons learned
✅ Process improvements
✅ Thought leadership

### What NOT to Post
❌ Client names (unless permission)
❌ Confidential financial data
❌ Negative comments about clients
❌ Personal complaints or drama
❌ Competitive intelligence

### Hashtags (Your Favorites)
#AI #Automation #Productivity
#BusinessGrowth #Leadership
#Innovation #Technology

### Call-to-Actions
- What to say for engagement
- When to ask for comments
- How to encourage shares
```

## Output Files

When post is ready to publish:

**Location:** `AI_Employee_Vault/Pending_Approval/LINKEDIN_*.md`

**Format:**
```yaml
---
type: linkedin_post
action: publish
status: pending_approval
created: 2026-02-18T10:00:00Z
expires: 2026-02-19T10:00:00Z
scheduled_time: 2026-02-18T14:30:00Z
character_count: 245
image: screenshot.png
---

# LinkedIn Post

## Content
Your post content here with formatting

## Hashtags
#AI #Automation #Productivity

## Metadata
- Character Count: 245 / 3000
- Image: Yes (screenshot.png)
- Scheduled: 2026-02-18 14:30 UTC
- Performance Goal: 500+ impressions

## To Approve
Move this file to `/Approved/` to publish.

## To Reject
Move this file to `/Rejected/` to discard.

## To Edit
Move back to `/Needs_Action/`, edit content, re-process.
```

## Post Performance Tracking

After posting, LinkedIn metrics are tracked:

**Location:** `AI_Employee_Vault/Social_Media/LinkedIn_Analytics.md`

**Tracked Metrics:**
- Impressions (views)
- Engagement (likes, comments, shares)
- Click-through rate
- Follower growth
- Profile views
- Post reach

## Human Workflow

1. **Review** - Open `Pending_Approval/LINKEDIN_*.md` in Obsidian
2. **Read** - Check content, hashtags, and image
3. **Enhance (optional):**
   - Add emojis or formatting
   - Revise hashtags
   - Optimize call-to-action
4. **Decide:**
   - ✅ Approve: Drag file to `/Approved/` folder
   - ❌ Reject: Drag file to `/Rejected/` folder
   - ✏️ Edit: Modify content and re-process
5. **Publish:** AI Employee posts immediately or at scheduled time
6. **Track:** Monitor performance in LinkedIn_Analytics.md

## Audit Logging

Every post is logged:

```json
{
  "timestamp": "2026-02-18T14:30:00Z",
  "action_type": "linkedin_post_published",
  "actor": "claude_code",
  "post_id": "POST_12345",
  "content_preview": "Post content here...",
  "character_count": 245,
  "status": "published",
  "approved_by": "human",
  "approval_time": "2026-02-18T10:00:00Z",
  "publish_time": "2026-02-18T14:30:00Z",
  "has_image": true,
  "hashtags": ["#AI", "#Automation"],
  "error": null
}
```

Location: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

## Content Generation (Auto)

When `auto_generate: true`, Claude:

1. Reads recent completed items from `Done/`
2. Extracts key achievements and learnings
3. Generates 3-5 post options
4. Selects best fit for LinkedIn
5. Adds relevant hashtags
6. Creates draft for review

This ensures consistent, valuable content without manual effort.

## Limitations & Considerations

- Browser automation (not official API)
- Session must be maintained active
- Images limited by LinkedIn (8MB)
- Links require LinkedIn approval
- Rate limited to 3 posts/day
- Video not currently supported

## Troubleshooting

### "Session Expired" Error

**Solution:**
- Run: `python linkedin_poster.py --vault ./AI_Employee_Vault --setup`
- Re-authenticate with your LinkedIn account
- Session will be refreshed

### "Post Failed to Publish"

**Solution:**
- Check that file is in `/Approved/` folder
- Verify LinkedIn Web is accessible
- Check logs for specific error
- Retry posting

### Post Looks Different Than Draft

**LinkedIn Formatting:**
- LinkedIn applies its own formatting
- Links may be displayed differently
- Images auto-optimized for platform
- This is normal behavior

### Low Engagement

**Recommendations:**
- Post at optimal times (9-11 AM)
- Use 3-5 relevant hashtags
- Include call-to-action (ask for comments)
- Mix of content types for variety
- Engage with comments to boost reach

## Related Skills

- `/process-inbox` - Create posts from completed work
- `/generate-briefing` - Gather content for posts
- `/manage-approvals` - Review and publish posts

## Performance & Limitations

| Aspect | Limit | Notes |
|--------|-------|-------|
| Content Length | 3,000 chars | LinkedIn limit |
| Image Size | 8MB | Per LinkedIn |
| Hashtags | 30 | Recommended 3-5 |
| Rate Limit | 3/day | Prevent spam |
| Approval Expiry | 24h | Auto-discard old posts |
| Publish Time | 2-5 seconds | Via browser |

---

**Last Updated:** 2026-02-18
**Version:** 1.0 (Silver Tier)
**Stability:** Production Ready
**Real-Time Analytics:** Coming in Gold Tier
