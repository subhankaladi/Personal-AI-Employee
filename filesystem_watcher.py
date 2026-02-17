#!/usr/bin/env python3
"""
FileSystem Watcher
==================

Monitors a specified "drop folder" for new files and creates action items
in the Obsidian vault. This is useful for:
- Automatically capturing screenshots or exports
- Processing downloaded files
- Monitoring project folders

Installation:
    pip install watchdog

Usage:
    python filesystem_watcher.py --vault /path/to/vault --watch /path/to/watch
    python filesystem_watcher.py --vault ./AI_Employee_Vault --watch ~/Downloads
"""

import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import base watcher
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class FileDropHandler(BaseWatcher, FileSystemEventHandler):
    """
    Monitor a folder for new files and create action items.

    Inherits from both BaseWatcher (for vault management) and
    FileSystemEventHandler (for watchdog integration).
    """

    def __init__(self, vault_path: str, watch_folder: str, exclude_patterns: list = None):
        """
        Initialize the file drop watcher.

        Args:
            vault_path: Path to Obsidian vault
            watch_folder: Folder to monitor for new files
            exclude_patterns: List of filename patterns to ignore
        """
        BaseWatcher.__init__(self, vault_path, watcher_name='FileSystemWatcher')

        self.watch_folder = Path(watch_folder)
        self.exclude_patterns = exclude_patterns or ['.DS_Store', 'thumbs.db', '~$']

        if not self.watch_folder.exists():
            raise ValueError(f'Watch folder does not exist: {watch_folder}')

        self.logger.info(f'FileSystem Watcher initialized')
        self.logger.info(f'  Watch folder: {self.watch_folder}')
        self.logger.info(f'  Exclude patterns: {self.exclude_patterns}')

    def _should_ignore(self, filename: str) -> bool:
        """Check if file should be ignored based on patterns."""
        for pattern in self.exclude_patterns:
            if pattern in filename:
                return True
        return False

    def check_for_updates(self) -> list:
        """
        Scan watch folder for existing files (initial load).

        Returns:
            List of files in watch folder
        """
        files = []
        if self.watch_folder.exists():
            for file in self.watch_folder.iterdir():
                if file.is_file() and not self._should_ignore(file.name):
                    files.append(file)
        return files

    def create_action_file(self, file_path: Path) -> Path:
        """
        Create a markdown metadata file for a dropped file.

        Args:
            file_path: Path to the dropped file

        Returns:
            Path to created metadata file
        """
        filename = file_path.name
        file_size = file_path.stat().st_size
        file_type = file_path.suffix.lower()

        # Create metadata
        frontmatter = {
            'type': 'file_drop',
            'original_name': filename,
            'size_bytes': file_size,
            'file_type': file_type,
            'detected': datetime.utcnow().isoformat() + 'Z',
            'status': 'pending'
        }

        # Categorize file type
        content = f'''## File Detected: {filename}

### Details
- **Size:** {self._format_size(file_size)}
- **Type:** {file_type if file_type else 'No extension'}
- **Detected:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

### Actions
- [ ] Review file
- [ ] Move to appropriate folder
- [ ] Process/Archive

### File Location
File stored temporarily in: `{file_path}`

### Next Steps
1. Review the file content
2. Move to appropriate project folder
3. Create detailed task if processing needed

---
*Automatically detected by FileSystem Watcher*
'''

        # Create action file
        safe_filename = filename.replace(' ', '_').replace('/', '_')
        metadata_filename = f'FILE_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}_{safe_filename}'

        action_file = self.create_markdown_file(metadata_filename, frontmatter, content)

        # Copy the actual file to vault for reference
        try:
            vault_file = self.needs_action / filename
            if not vault_file.exists():
                shutil.copy2(file_path, vault_file)
                self.logger.info(f'Copied file to vault: {vault_file}')
        except Exception as e:
            self.logger.error(f'Failed to copy file: {e}')

        # Log the action
        self.log_action(
            'file_detected',
            f'New file: {filename}',
            'pending',
            {'size': file_size, 'type': file_type}
        )

        return action_file

    def on_created(self, event):
        """Watchdog event: File created."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if self._should_ignore(file_path.name):
            return

        self.logger.info(f'File created: {file_path.name}')

        # Add small delay to ensure file is fully written
        import time
        time.sleep(0.5)

        if file_path.exists():
            self.create_action_file(file_path)

    def on_modified(self, event):
        """Watchdog event: File modified."""
        # Usually we don't want to act on modifications
        pass

    def on_deleted(self, event):
        """Watchdog event: File deleted."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            self.logger.warning(f'File deleted from watch folder: {file_path.name}')

    def run_watchdog(self):
        """
        Run the watchdog observer (blocking).

        This is the recommended way to run the file watcher continuously.
        """
        observer = Observer()
        observer.schedule(self, str(self.watch_folder), recursive=False)

        self.logger.info(f'Starting FileSystem Watcher (watchdog mode)')
        observer.start()

        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.logger.info('FileSystem Watcher stopped')
        observer.join()

    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f'{bytes_size:.1f} {unit}'
            bytes_size /= 1024
        return f'{bytes_size:.1f} TB'


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Monitor a folder and create action items in Obsidian vault'
    )
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--watch', required=True, help='Folder to monitor')
    parser.add_argument('--exclude', nargs='+', default=['.DS_Store', 'thumbs.db'],
                        help='File patterns to ignore')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode (no watching)')

    args = parser.parse_args()

    try:
        watcher = FileDropHandler(args.vault, args.watch, args.exclude)

        if args.demo:
            print('✅ FileSystem Watcher initialized (demo mode)')
            print(f'   Vault: {args.vault}')
            print(f'   Watch: {args.watch}')
            print(f'   Exclude: {args.exclude}')
            print('\nExisting files would be processed:')

            files = watcher.check_for_updates()
            if files:
                for f in files[:5]:  # Show first 5
                    print(f'   - {f.name}')
                if len(files) > 5:
                    print(f'   ... and {len(files) - 5} more')
            else:
                print('   (none found)')
        else:
            print(f'🚀 Starting FileSystem Watcher')
            print(f'   Vault: {args.vault}')
            print(f'   Watch: {args.watch}')
            print(f'   Press Ctrl+C to stop')
            watcher.run_watchdog()

    except Exception as e:
        print(f'❌ Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
