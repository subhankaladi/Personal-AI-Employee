#!/usr/bin/env python3
"""
Base Watcher Template
=====================

All Watcher scripts inherit from this base class to provide consistent
monitoring, error handling, and file creation patterns.

Usage:
    class MyWatcher(BaseWatcher):
        def check_for_updates(self) -> list:
            # Return list of new items to process
            pass

        def create_action_file(self, item) -> Path:
            # Create markdown file in Needs_Action
            pass
"""

import time
import logging
import json
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watcher.log'),
        logging.StreamHandler()
    ]
)


class BaseWatcher(ABC):
    """
    Abstract base class for all Watcher implementations.

    Provides:
    - Consistent folder structure access
    - Error handling and retry logic
    - Logging infrastructure
    - File creation utilities
    """

    def __init__(self, vault_path: str, check_interval: int = 60, watcher_name: str = None):
        """
        Initialize the watcher.

        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks (default: 60)
            watcher_name: Name for logging (defaults to class name)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.watcher_name = watcher_name or self.__class__.__name__

        # Standard vault folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.logs = self.vault_path / 'Logs'

        # Ensure folders exist
        self._ensure_folders()

        # Logger setup
        self.logger = logging.getLogger(self.watcher_name)
        self.logger.info(f'Initializing {self.watcher_name} (Check interval: {check_interval}s)')

        # Track processed items to avoid duplicates
        self.processed_ids = set()

    def _ensure_folders(self):
        """Ensure all required vault folders exist."""
        for folder in [self.needs_action, self.plans, self.done,
                       self.pending_approval, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.

        Returns:
            List of new items (format depends on implementation)
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a markdown action file for an item.

        Args:
            item: The item to create a file for

        Returns:
            Path to the created file
        """
        pass

    def create_markdown_file(self, filename: str, frontmatter: dict, content: str) -> Path:
        """
        Helper to create a markdown file with frontmatter and content.

        Args:
            filename: Name of file to create (without .md)
            frontmatter: Dictionary of YAML frontmatter
            content: Markdown content body

        Returns:
            Path to created file
        """
        file_path = self.needs_action / f'{filename}.md'

        # Build YAML frontmatter
        yaml_content = '---\n'
        for key, value in frontmatter.items():
            if isinstance(value, str):
                yaml_content += f'{key}: {value}\n'
            elif isinstance(value, bool):
                yaml_content += f'{key}: {str(value).lower()}\n'
            else:
                yaml_content += f'{key}: {value}\n'
        yaml_content += '---\n\n'

        # Combine and write
        full_content = yaml_content + content
        file_path.write_text(full_content, encoding='utf-8')

        self.logger.info(f'Created action file: {file_path}')
        return file_path

    def log_action(self, action_type: str, description: str, status: str = 'pending',
                   details: dict = None):
        """
        Log an action to the audit log.

        Args:
            action_type: Type of action (e.g., 'email_received')
            description: Human-readable description
            status: Status of action (pending, approved, completed, failed)
            details: Additional details as dict
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'watcher': self.watcher_name,
            'action_type': action_type,
            'description': description,
            'status': status,
            'details': details or {}
        }

        # Append to daily log file
        today = datetime.utcnow().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        try:
            # Read existing logs
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            # Append new log
            logs.append(log_entry)

            # Write back
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            self.logger.error(f'Failed to write log: {e}')

    def run(self):
        """
        Main loop - continuously check for updates.

        This is the core operation that runs indefinitely.
        """
        self.logger.info(f'Starting {self.watcher_name}')

        while True:
            try:
                items = self.check_for_updates()

                if items:
                    self.logger.info(f'Found {len(items)} new items')

                    for item in items:
                        try:
                            self.create_action_file(item)
                        except Exception as e:
                            self.logger.error(f'Failed to create action file: {e}')

            except Exception as e:
                self.logger.error(f'Error in main loop: {e}')
                self.log_action('watcher_error', f'Error: {str(e)}', 'failed')

            # Wait before next check
            time.sleep(self.check_interval)


# Example implementation (for testing)
if __name__ == '__main__':
    import sys

    class DummyWatcher(BaseWatcher):
        """Dummy watcher for testing base class."""

        def check_for_updates(self) -> list:
            # Return empty list (no updates in demo)
            return []

        def create_action_file(self, item) -> Path:
            # Dummy implementation
            return Path()

    # Test
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
        watcher = DummyWatcher(vault_path, check_interval=5)
        print(f'✅ Base watcher initialized successfully')
        print(f'   Vault path: {vault_path}')
        print(f'   Check interval: 5 seconds')
        print(f'   Ready for subclass implementation')
    else:
        print('Usage: python base_watcher.py <vault_path>')
        print('Example: python base_watcher.py ./AI_Employee_Vault')
