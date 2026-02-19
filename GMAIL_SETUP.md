# 📧 Gmail Setup Guide for AI Employee

Complete guide to set up Gmail authentication for the AI Employee's email capabilities.

---

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click **"Select a Project"** at the top
4. Click **"NEW PROJECT"**
5. Enter project name: `AI-Employee-Gmail`
6. Click **"CREATE"**
7. Wait for project to be created (it may take a minute)

---

## Step 2: Enable Gmail API

1. In the Cloud Console, search for **"Gmail API"**
2. Click on **"Gmail API"** from results
3. Click **"ENABLE"**
4. Wait for it to be enabled (you'll see a blue "Manage" button)

---

## Step 3: Create OAuth Consent Screen

1. Click **"Manage"** on the Gmail API page (or go to APIs & Services → OAuth consent screen)
2. Click **"CREATE CONSENT SCREEN"**
3. Choose **"External"** (you're the only user)
4. Click **"CREATE"**
5. Fill in the form:
   - **App name:** `AI Employee`
   - **User support email:** Your Gmail address
   - **Developer contact information:** Your email
6. Click **"SAVE AND CONTINUE"**
7. Click **"ADD OR REMOVE SCOPES"**
8. Search for these scopes and add them:
   - `https://www.googleapis.com/auth/gmail.readonly` (read emails)
   - `https://www.googleapis.com/auth/gmail.send` (send emails)
   - `https://www.googleapis.com/auth/gmail.modify` (mark read, etc.)
9. Click **"SAVE AND CONTINUE"**
10. Add yourself as a test user:
    - Click **"ADD USERS"**
    - Enter your Gmail address
    - Click **"ADD"**
11. Click **"SAVE AND CONTINUE"**
12. Review and click **"BACK TO DASHBOARD"**

---

## Step 4: Create OAuth Credentials

1. Go to **APIs & Services → Credentials** (left sidebar)
2. Click **"+ CREATE CREDENTIALS"**
3. Choose **"OAuth client ID"**
4. If asked to create an OAuth consent screen, you've already done that ✓
5. Choose **"Desktop application"** for Application type
6. Name it: `AI Employee Gmail`
7. Click **"CREATE"**
8. You'll see a popup with your credentials:
   - **Client ID**
   - **Client Secret**
9. Click **"DOWNLOAD JSON"** (or click the download icon)
10. Save the file as `credentials.json` in your project root

---

## Step 5: Configure Your Project

### 5A. Place credentials.json in project root

```bash
# The file should be at:
/mnt/c/Users/a/Documents/GitHub/Personal-AI-Employee/credentials.json
```

### 5B. Create .env file

Create a `.env` file in the project root with:

```bash
# Gmail Configuration
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify
GMAIL_CHECK_INTERVAL=120

# LinkedIn Configuration (will be used later)
LINKEDIN_EMAIL=your-email@gmail.com
LINKEDIN_PASSWORD=your-password-or-app-password

# WhatsApp Configuration (will be used later)
WHATSAPP_SESSION_PATH=./whatsapp_session
```

⚠️ **IMPORTANT:** Never commit `.env` to git! It's already in `.gitignore`.

### 5C. Test the Setup

Run this to verify Gmail connection works:

```bash
cd /mnt/c/Users/a/Documents/GitHub/Personal-AI-Employee
python gmail_watcher.py --vault ./AI_Employee_Vault --test --demo
```

---

## Troubleshooting

### "Invalid client" error
- Make sure `credentials.json` is in the project root
- Verify the file contains your Client ID and Client Secret
- Try re-downloading credentials from Google Cloud Console

### "Access Denied" error
- You may need to add your email as a test user (see Step 3, section 10)
- Check that you've enabled all required scopes

### "Gmail API not enabled" error
- Go to Google Cloud Console
- Make sure the Gmail API is enabled (Step 2)
- Wait a minute and try again (sometimes it takes time to activate)

### Credentials not being read
- Verify `.env` file exists in project root
- Check that path in GMAIL_CREDENTIALS_PATH is correct
- Try absolute path instead of relative path

---

## Testing Email Operations

Once setup is complete, you can test:

```bash
# Test 1: List unread emails
python gmail_watcher.py --vault ./AI_Employee_Vault --list-unread

# Test 2: Create a test email in Needs_Action
python gmail_watcher.py --vault ./AI_Employee_Vault --test

# Test 3: Full watcher demo (read-only)
python gmail_watcher.py --vault ./AI_Employee_Vault --demo
```

---

## What You Can Do Now

With Gmail setup complete, the AI Employee can:

✅ Read unread emails automatically
✅ Create action items from important emails
✅ Draft responses
✅ Send emails (with human approval)
✅ Mark emails as read/archived
✅ Search emails
✅ Track email metrics in Dashboard

---

## Next Steps

1. Continue to **Phase 2: Email Skills** in SILVER_SETUP.md
2. Set up the Email MCP server
3. Create Email sending skill

---

## Security Notes

- ✅ Credentials stored in `.env` (never in code)
- ✅ OAuth tokens stored locally only
- ✅ All sensitive data stays on your machine
- ✅ No credentials logged or displayed
- ✅ Regular credential rotation recommended

For more info: [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)

