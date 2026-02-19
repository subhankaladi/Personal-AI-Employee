#!/usr/bin/env python3
"""
LinkedIn Poster - Automate posting to LinkedIn via browser automation.

This script:
1. Connects to LinkedIn Web via Playwright
2. Monitors for post drafts in AI_Employee_Vault
3. Automatically publishes approved posts
4. Tracks engagement metrics
5. Maintains browser session for continuous operation

Setup:
1. Install playwright: pip install playwright
2. Run: python3 -m playwright install
3. Create .env with LINKEDIN_EMAIL and LINKEDIN_PASSWORD
4. First run will set up session
5. Can run manually or on schedule

Usage:
python linkedin_poster.py --vault ./AI_Employee_Vault --setup  # Initial login
python linkedin_poster.py --vault ./AI_Employee_Vault --post   # Post drafted content
python linkedin_poster.py --vault ./AI_Employee_Vault --demo    # Demo mode

"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import time

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
        logging.FileHandler('linkedin_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LinkedInPoster')


class LinkedInPoster:
    """Handle LinkedIn posting via browser automation."""

    def __init__(self, vault_path: str, email: str = None, password: str = None):
        """
        Initialize LinkedIn poster.

        Args:
            vault_path: Path to Obsidian vault
            email: LinkedIn email (from .env or arg)
            password: LinkedIn password (from .env or arg)
        """
        self.vault_path = Path(vault_path)
        self.session_path = Path(os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session'))
        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')
        self.browser = None
        self.context = None
        self.page = None
        self._ensure_folders()

    def _ensure_folders(self):
        """Ensure required folders exist."""
        (self.vault_path / 'Social_Media').mkdir(exist_ok=True)
        (self.vault_path / 'Pending_Approval').mkdir(exist_ok=True)
        (self.vault_path / 'Done').mkdir(exist_ok=True)

    def setup_browser(self, headless: bool = True) -> bool:
        """Setup Playwright browser."""
        try:
            playwright = sync_playwright().start()
            self.context = playwright.chromium.launch_persistent_context(
                str(self.session_path),
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            logger.info("Browser launched successfully")
            return True
        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            return False

    def authenticate_linkedin(self) -> bool:
        """Authenticate with LinkedIn."""
        try:
            logger.info("Navigating to LinkedIn...")
            self.page.goto('https://www.linkedin.com', wait_until='networkidle', timeout=30000)

            # Check if already logged in
            try:
                self.page.wait_for_selector('[data-test-id="feed"]', timeout=5000)
                logger.info("Already logged into LinkedIn")
                return True
            except:
                logger.info("Need to log in")

            # Fill in email
            self.page.fill('input[name="session_key"]', self.email)
            time.sleep(1)

            # Fill in password
            self.page.fill('input[name="session_password"]', self.password)
            time.sleep(1)

            # Click login button
            self.page.click('button[type="submit"]')
            time.sleep(3)

            # Wait for feed to load
            self.page.wait_for_selector('[data-test-id="feed"]', timeout=30000)
            logger.info("✓ Successfully authenticated with LinkedIn")
            return True

        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {e}")
            return False

    def find_pending_posts(self) -> List[Dict]:
        """Find pending LinkedIn posts in Pending_Approval folder."""
        try:
            pending_dir = self.vault_path / 'Pending_Approval'
            posts = []

            for file in pending_dir.glob('LINKEDIN_*.md'):
                try:
                    content = file.read_text()

                    # Parse YAML frontmatter
                    parts = content.split('---')
                    if len(parts) < 3:
                        continue

                    frontmatter = parts[1]
                    body = parts[2].strip()

                    # Check if this is a LinkedIn post
                    if 'type: linkedin_post' not in frontmatter:
                        continue

                    # Extract metadata
                    post_data = {
                        'file': file,
                        'filename': file.name,
                        'content': body,
                        'created': datetime.now().isoformat()
                    }

                    # Extract hashtags if present
                    if 'hashtags:' in frontmatter:
                        hashtags_line = [l for l in frontmatter.split('\n') if l.startswith('hashtags:')]
                        if hashtags_line:
                            post_data['hashtags'] = hashtags_line[0].replace('hashtags:', '').strip()

                    posts.append(post_data)

                except Exception as e:
                    logger.warning(f"Error parsing {file.name}: {e}")
                    continue

            logger.info(f"Found {len(posts)} pending LinkedIn posts")
            return posts

        except Exception as e:
            logger.error(f"Error finding pending posts: {e}")
            return []

    def post_to_linkedin(self, post_content: str, hashtags: str = None) -> bool:
        """Post content to LinkedIn."""
        try:
            logger.info("Posting to LinkedIn...")

            # Click on post area
            self.page.click('[contenteditable][data-tab-content]')
            time.sleep(2)

            # Prepare content
            full_content = post_content
            if hashtags:
                full_content += f"\n\n{hashtags}"

            # Type content
            self.page.type('[contenteditable][data-tab-content]', full_content)
            time.sleep(2)

            # Click post button
            post_button = self.page.query_selector('button:has-text("Post")')
            if post_button:
                post_button.click()
                time.sleep(3)
                logger.info("✓ Post published successfully")
                return True
            else:
                logger.error("Could not find post button")
                return False

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            return False

    def get_engagement_metrics(self) -> Dict:
        """Get engagement metrics for recent posts."""
        try:
            logger.info("Fetching engagement metrics...")

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'posts': []
            }

            # This would require parsing the page to get actual metrics
            # For now, return template
            return metrics

        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}

    def move_post_to_done(self, filename: str, success: bool = True):
        """Move post file to Done folder."""
        try:
            source = self.vault_path / 'Pending_Approval' / filename
            dest = self.vault_path / 'Done' / f"{filename.replace('LINKEDIN_', 'LINKEDIN_POSTED_')}"

            if source.exists():
                content = source.read_text()
                # Update status in YAML
                content = content.replace('status: pending_approval', 'status: posted')
                content = content.replace('type: linkedin_post', f'type: linkedin_post\nposted_at: {datetime.now().isoformat()}\nsuccess: {success}')
                dest.write_text(content)
                source.unlink()
                logger.info(f"Moved to Done: {filename}")
        except Exception as e:
            logger.error(f"Error moving post: {e}")

    def close(self):
        """Close browser session."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            logger.info("Browser closed")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")

    def process_pending_posts(self, auto_post: bool = False):
        """Process pending posts."""
        posts = self.find_pending_posts()

        if not posts:
            logger.info("No pending posts to process")
            return

        logger.info(f"Processing {len(posts)} pending posts...")

        for post in posts:
            try:
                logger.info(f"Post: {post['filename']}")
                logger.info(f"Content preview: {post['content'][:100]}...")

                if auto_post:
                    if self.post_to_linkedin(post['content'], post.get('hashtags')):
                        self.move_post_to_done(post['filename'], success=True)
                    else:
                        logger.error(f"Failed to post: {post['filename']}")
                else:
                    logger.info(f"[DEMO] Would post: {post['filename']}")
                    self.move_post_to_done(post['filename'], success=False)

            except Exception as e:
                logger.error(f"Error processing post {post['filename']}: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--email', default=None, help='LinkedIn email')
    parser.add_argument('--password', default=None, help='LinkedIn password')
    parser.add_argument('--setup', action='store_true', help='Interactive setup mode')
    parser.add_argument('--post', action='store_true', help='Post pending content')
    parser.add_argument('--demo', action='store_true', help='Demo mode (no actual posts)')
    parser.add_argument('--metrics', action='store_true', help='Get engagement metrics')

    args = parser.parse_args()

    # Create poster
    poster = LinkedInPoster(args.vault, args.email, args.password)

    if args.setup:
        logger.info("LinkedIn Setup Mode")
        logger.info("Starting browser for manual setup...")
        if poster.setup_browser(headless=False):
            if poster.authenticate_linkedin():
                logger.info("✓ Setup complete! Session saved.")
                input("Press Enter to close browser...")
            else:
                logger.error("✗ Authentication failed")
        poster.close()
        return

    if args.metrics:
        logger.info("Getting engagement metrics...")
        if poster.setup_browser():
            if poster.authenticate_linkedin():
                metrics = poster.get_engagement_metrics()
                logger.info(json.dumps(metrics, indent=2))
        poster.close()
        return

    if args.post or args.demo:
        logger.info(f"{'DEMO' if args.demo else 'POSTING'} mode...")
        if poster.setup_browser(headless=not args.demo):
            if poster.authenticate_linkedin():
                poster.process_pending_posts(auto_post=args.post)
        poster.close()
        return

    logger.error("Please specify --setup, --post, --demo, or --metrics")


if __name__ == '__main__':
    main()
