#!/usr/bin/env python3
"""
WhatsApp Watcher - Monitor WhatsApp Web for urgent messages.

This script:
1. Connects to WhatsApp Web via Playwright browser automation
2. Monitors for new unread messages
3. Filters by keywords (urgent, asap, invoice, payment, help)
4. Creates markdown files in Needs_Action/ for each message
5. Maintains browser session for continuous monitoring

Setup:
1. Install playwright: pip install playwright
2. Run: python3 -m playwright install
3. Create .env with WHATSAPP_SESSION_PATH
4. First run will open browser for manual QR code scan
5. Session saved for future automated runs

Usage:
python whatsapp_watcher.py --vault ./AI_Employee_Vault --demo
python whatsapp_watcher.py --vault ./AI_Employee_Vault  # Run continuously

"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("ERROR: Playwright not installed.")
    print("Install with: pip install playwright")
    print("Then run: python3 -m playwright install")
    sys.exit(1)

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WhatsAppWatcher')


class WhatsAppWatcher(BaseWatcher):
    """Monitor WhatsApp Web for urgent messages."""

    # Keywords that trigger action items
    URGENT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 'critical']

    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 30):
        """
        Initialize WhatsApp watcher.

        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session (default: ./whatsapp_session)
            check_interval: Seconds between checks (default 30)
        """
        super().__init__(vault_path, check_interval, watcher_name='WhatsApp')
        self.session_path = Path(session_path or os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session'))
        self.browser = None
        self.context = None
        self.page = None
        self.processed_messages = set()
        self._load_processed_messages()

    def _load_processed_messages(self):
        """Load previously processed message IDs."""
        processed_file = Path(self.vault_path) / '.processed_whatsapp'
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    self.processed_messages = set(json.load(f))
                logger.info(f"Loaded {len(self.processed_messages)} previously processed messages")
            except Exception as e:
                logger.warning(f"Could not load processed messages: {e}")

    def _save_processed_messages(self):
        """Save processed message IDs."""
        processed_file = Path(self.vault_path) / '.processed_whatsapp'
        try:
            with open(processed_file, 'w') as f:
                json.dump(list(self.processed_messages), f)
        except Exception as e:
            logger.warning(f"Could not save processed messages: {e}")

    def setup_browser(self) -> bool:
        """Setup Playwright browser with WhatsApp Web."""
        try:
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )

            self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()

            logger.info("Browser launched successfully")
            return True

        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            return False

    def authenticate_whatsapp(self) -> bool:
        """Open WhatsApp Web for manual QR code scan."""
        try:
            logger.info("Opening WhatsApp Web...")
            self.page.goto('https://web.whatsapp.com', wait_until='networkidle', timeout=30000)

            # Wait for WhatsApp to load
            logger.info("Waiting for WhatsApp to load...")
            self.page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)

            logger.info("WhatsApp loaded successfully")
            return True

        except PlaywrightTimeoutError:
            logger.error("Timeout waiting for WhatsApp to load - You may need to scan QR code manually")
            return False
        except Exception as e:
            logger.error(f"WhatsApp authentication failed: {e}")
            return False

    def check_for_updates(self) -> List[Dict]:
        """Check for new unread messages."""
        if not self.page:
            return []

        try:
            # Find unread chat badges
            unread_chats = self.page.query_selector_all('[data-testid="unread-badge"]')
            logger.info(f"Found {len(unread_chats)} unread chats")

            messages = []

            for chat_element in unread_chats:
                try:
                    # Get chat name
                    chat_item = chat_element.evaluate_handle('el => el.closest("[data-testid=chat-list-item-container]")')
                    chat_name_element = chat_item.query_selector('[data-testid="chat-name"]')

                    if not chat_name_element:
                        continue

                    chat_name = chat_name_element.text_content().strip()
                    message_id = f"whatsapp_{chat_name}_{datetime.now().timestamp()}"

                    # Skip if already processed
                    if message_id in self.processed_messages:
                        continue

                    # Get last message preview
                    message_element = chat_item.query_selector('[data-testid="conversation-message-preview"]')
                    message_text = message_element.text_content() if message_element else "(message preview unavailable)"

                    # Check if message contains urgent keywords
                    is_urgent = any(kw in message_text.lower() for kw in self.URGENT_KEYWORDS)

                    if is_urgent or len(self.processed_messages) < 5:  # Always get first few
                        messages.append({
                            'id': message_id,
                            'from': chat_name,
                            'preview': message_text[:200],
                            'is_urgent': is_urgent,
                            'timestamp': datetime.now().isoformat()
                        })
                        self.processed_messages.add(message_id)

                except Exception as e:
                    logger.warning(f"Error processing chat: {e}")
                    continue

            if messages:
                logger.info(f"Found {len(messages)} new unread messages")
                self._save_processed_messages()

            return messages

        except Exception as e:
            logger.error(f"Error checking for messages: {e}")
            return []

    def create_action_file(self, message: Dict) -> Path:
        """Create markdown file for message in Needs_Action folder."""
        try:
            from_name = message['from'].replace(' ', '_').replace('/', '_')
            filename = f"WHATSAPP_{from_name}_{message['id'].split('_')[-1]}.md"

            priority = 'high' if message['is_urgent'] else 'normal'

            content = f"""---
type: whatsapp_message
status: pending
priority: {priority}
from: {message['from']}
received: {message['timestamp']}
urgent: {message['is_urgent']}
message_id: {message['id']}
---

# WhatsApp from {message['from']}

## Message Preview
{message['preview']}

## Urgent: {"YES ⚠️" if message['is_urgent'] else "No"}

## Suggested Actions
- [ ] Read full message
- [ ] Analyze request
- [ ] Draft response
- [ ] Request approval
- [ ] Send reply
- [ ] Mark as done

## Response
Write your response here before moving to approval.

## Notes
Add context or follow-up items here.
"""

            filepath = self.needs_action / filename
            filepath.write_text(content)

            # Log action
            self.log_action({
                'action_type': 'whatsapp_message_detected',
                'message_id': message['id'],
                'from': message['from'],
                'urgent': message['is_urgent'],
                'status': 'created_action_file',
                'file': str(filepath)
            })

            logger.info(f"Created action file: {filename}")
            return filepath

        except Exception as e:
            logger.error(f"Error creating action file: {e}")
            return None

    def close(self):
        """Close browser session."""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            logger.info("Browser closed")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")

    def run_interactive(self):
        """Run in interactive mode for session setup."""
        logger.info("Starting WhatsApp Web in interactive mode...")
        logger.info("Please scan the QR code with your WhatsApp mobile device")
        logger.info("Session will be saved for future automated runs")

        if not self.setup_browser():
            logger.error("Failed to setup browser")
            return

        if not self.authenticate_whatsapp():
            logger.error("Failed to authenticate with WhatsApp")
            self.close()
            return

        logger.info("WhatsApp authenticated! Session saved.")
        logger.info("You can now run in automated mode without manual scanning.")

        try:
            # Keep browser open for user to verify
            input("Press Enter to close browser...")
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--session', default=None, help='Path to WhatsApp session')
    parser.add_argument('--demo', action='store_true', help='Demo mode (read-only)')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--setup', action='store_true', help='Interactive setup mode')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')

    args = parser.parse_args()

    # Create watcher
    watcher = WhatsAppWatcher(args.vault, args.session, args.interval)

    if args.setup:
        watcher.run_interactive()
        return

    if args.test:
        logger.info("Testing WhatsApp connection...")
        if watcher.setup_browser() and watcher.authenticate_whatsapp():
            logger.info("✓ WhatsApp Web accessible")
            items = watcher.check_for_updates()
            logger.info(f"Found {len(items)} unread messages")
        else:
            logger.error("✗ WhatsApp Web not accessible")
        watcher.close()
        return

    if args.demo:
        logger.info("Demo mode: Starting browser...")
        if watcher.setup_browser() and watcher.authenticate_whatsapp():
            logger.info("Checking for messages...")
            items = watcher.check_for_updates()
            logger.info(f"Would create {len(items)} action files:")
            for item in items:
                logger.info(f"  - {item['from']}: {item['preview'][:50]}...")
        watcher.close()
        return

    # Run continuous watcher
    logger.info(f"Starting WhatsApp watcher (checking every {args.interval}s)")
    logger.info(f"Vault: {args.vault}")
    logger.info("Press Ctrl+C to stop")

    if not watcher.setup_browser():
        logger.error("Failed to setup browser")
        sys.exit(1)

    if not watcher.authenticate_whatsapp():
        logger.error("Failed to authenticate with WhatsApp")
        sys.exit(1)

    try:
        watcher.run()
    except KeyboardInterrupt:
        logger.info("WhatsApp watcher stopped by user")
    finally:
        watcher.close()
        sys.exit(0)


if __name__ == '__main__':
    main()
