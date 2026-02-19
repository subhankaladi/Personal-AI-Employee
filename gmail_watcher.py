#!/usr/bin/env python3
"""
Gmail Watcher - Monitors Gmail inbox for new emails and creates action items.

This script:
1. Connects to Gmail API using OAuth
2. Monitors for new unread emails
3. Creates markdown files in Needs_Action/ for each email
4. Tracks processed emails to avoid duplicates
5. Supports dry-run mode for testing

Setup:
1. Complete GMAIL_SETUP.md to get credentials.json
2. Place credentials.json in project root
3. Create .env file with GMAIL_CREDENTIALS_PATH
4. Run: python gmail_watcher.py --vault ./AI_Employee_Vault

"""

import os
import sys
import json
import pickle
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from base_watcher import BaseWatcher

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("ERROR: Google API client not installed.")
    print("Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gmail_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('GmailWatcher')

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailWatcher(BaseWatcher):
    """Monitor Gmail inbox and create action items for new emails."""

    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 120):
        """
        Initialize Gmail watcher.

        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to credentials.json
            check_interval: Seconds between checks (default 120)
        """
        super().__init__(vault_path, check_interval, watcher_name='Gmail')
        self.credentials_path = Path(credentials_path)
        self.token_path = Path('gmail_token.pickle')
        self.service = None
        self.creds = None
        self.processed_ids = set()
        self._load_processed_ids()

    def authenticate(self) -> bool:
        """Authenticate with Gmail API using OAuth."""
        try:
            # Load token if it exists
            if self.token_path.exists():
                with open(self.token_path, 'rb') as token_file:
                    self.creds = pickle.load(token_file)
                logger.info("Loaded existing token")

            # If no valid credentials, create new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                    logger.info("Refreshed token")
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                    logger.info("Created new token via OAuth")

                # Save token for next run
                with open(self.token_path, 'wb') as token_file:
                    pickle.dump(self.creds, token_file)

            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Successfully authenticated with Gmail API")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def _load_processed_ids(self):
        """Load previously processed email IDs."""
        processed_file = Path(self.vault_path) / '.processed_emails'
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    self.processed_ids = set(json.load(f))
                logger.info(f"Loaded {len(self.processed_ids)} previously processed emails")
            except Exception as e:
                logger.warning(f"Could not load processed IDs: {e}")

    def _save_processed_ids(self):
        """Save processed email IDs to avoid duplicates."""
        processed_file = Path(self.vault_path) / '.processed_emails'
        try:
            with open(processed_file, 'w') as f:
                json.dump(list(self.processed_ids), f)
        except Exception as e:
            logger.warning(f"Could not save processed IDs: {e}")

    def check_for_updates(self) -> List[Dict]:
        """Check for new unread emails."""
        if not self.service:
            return []

        try:
            # Get unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10  # Check last 10 unread emails
            ).execute()

            messages = results.get('messages', [])
            new_emails = []

            for message in messages:
                msg_id = message['id']

                # Skip if already processed
                if msg_id in self.processed_ids:
                    continue

                # Get full message details
                try:
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=msg_id,
                        format='full'
                    ).execute()

                    new_emails.append(msg)
                    self.processed_ids.add(msg_id)

                except Exception as e:
                    logger.error(f"Could not retrieve message {msg_id}: {e}")

            if new_emails:
                logger.info(f"Found {len(new_emails)} new unread emails")
                self._save_processed_ids()

            return new_emails

        except Exception as e:
            logger.error(f"Error checking for emails: {e}")
            return []

    def _extract_email_data(self, message: Dict) -> Dict:
        """Extract relevant data from Gmail message."""
        try:
            headers = {h['name']: h['value'] for h in message['payload']['headers']}

            # Get email body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            import base64
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            else:
                if 'body' in message['payload'] and 'data' in message['payload']['body']:
                    import base64
                    body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

            return {
                'id': message['id'],
                'from': headers.get('From', 'Unknown'),
                'subject': headers.get('Subject', '(No Subject)'),
                'to': headers.get('To', ''),
                'date': headers.get('Date', ''),
                'body': body[:500] if body else '(No body)',  # First 500 chars
                'labels': message.get('labelIds', [])
            }
        except Exception as e:
            logger.error(f"Error extracting email data: {e}")
            return {}

    def create_action_file(self, message: Dict) -> Path:
        """Create markdown file for email in Needs_Action folder."""
        try:
            email_data = self._extract_email_data(message)
            if not email_data:
                return None

            msg_id = email_data['id']

            # Create filename from sender and subject
            from_name = email_data['from'].split('<')[0].strip().replace(' ', '_')
            subject_slug = email_data['subject'][:30].replace(' ', '_').replace('/', '-')
            filename = f"EMAIL_{msg_id}_{from_name}.md"

            # Create markdown content
            content = f"""---
type: email
status: pending
priority: normal
from: {email_data['from']}
to: {email_data['to']}
subject: {email_data['subject']}
date: {email_data['date']}
email_id: {msg_id}
received: {datetime.now().isoformat()}
---

# Email from {email_data['from']}

## Subject
{email_data['subject']}

## Message
{email_data['body']}

## Suggested Actions
- [ ] Read and analyze
- [ ] Draft response
- [ ] Request approval to send
- [ ] Move to Done when complete

## Notes
Add your analysis here.
"""

            filepath = self.needs_action / filename
            filepath.write_text(content)

            # Log action
            self.log_action({
                'action_type': 'email_detected',
                'email_id': msg_id,
                'from': email_data['from'],
                'subject': email_data['subject'],
                'status': 'created_action_file',
                'file': str(filepath)
            })

            logger.info(f"Created action file: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating action file: {e}")
            return None

    def list_unread(self):
        """List all unread emails (for testing/inspection)."""
        if not self.authenticate():
            logger.error("Could not authenticate")
            return

        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} unread emails:\n")

            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
                print(f"  From: {headers.get('From', 'Unknown')}")
                print(f"  Subject: {headers.get('Subject', '(No Subject)')}")
                print(f"  Date: {headers.get('Date', '')}")
                print()

        except Exception as e:
            logger.error(f"Error listing emails: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--credentials', default='./credentials.json', help='Path to credentials.json')
    parser.add_argument('--demo', action='store_true', help='Demo mode (read-only, no files created)')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--list-unread', action='store_true', help='List unread emails')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds')

    args = parser.parse_args()

    # Create watcher
    watcher = GmailWatcher(args.vault, args.credentials, args.interval)

    if not watcher.authenticate():
        logger.error("Failed to authenticate with Gmail")
        sys.exit(1)

    if args.list_unread:
        watcher.list_unread()
        return

    if args.test:
        logger.info("Testing Gmail connection...")
        items = watcher.check_for_updates()
        logger.info(f"Found {len(items)} unread emails")
        if items:
            logger.info("Sample email:")
            email_data = watcher._extract_email_data(items[0])
            logger.info(json.dumps(email_data, indent=2))
        return

    if args.demo:
        logger.info("Demo mode: checking for emails without creating files...")
        items = watcher.check_for_updates()
        logger.info(f"Would create {len(items)} action files:")
        for item in items:
            email_data = watcher._extract_email_data(item)
            logger.info(f"  - {email_data['from']}: {email_data['subject']}")
        return

    # Run continuous watcher
    logger.info(f"Starting Gmail watcher (checking every {args.interval}s)")
    logger.info(f"Vault: {args.vault}")
    logger.info("Press Ctrl+C to stop")

    try:
        watcher.run()
    except KeyboardInterrupt:
        logger.info("Gmail watcher stopped by user")
        sys.exit(0)


if __name__ == '__main__':
    main()
