"""
Main application logic for envwarden-py
"""

import fnmatch
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from .bitwarden import BitwardenClient, BitwardenError
from .formatters import get_formatter


class EnvwardenApp:
    """Main application class for envwarden-py."""
    
    def __init__(self):
        self.bw_client = BitwardenClient()
    
    def run(self, search_term: str = 'envwarden',
            output_format: str = 'export',
            skip_sync: bool = False,
            copy_glob: Optional[str] = None,
            copy_to: Optional[str] = None) -> None:
        """Run the envwarden application."""
        
        try:
            # Authenticate
            self._authenticate()
            
            # Sync vault unless skipped
            if not skip_sync:
                self.bw_client.sync()
            
            # Search for items
            items = self.bw_client.search_items(search_term)
            
            if not items:
                print(f"No items found matching search term: {search_term}", file=sys.stderr)
                return
            
            # Handle file copying if requested
            if copy_glob and copy_to:
                self._copy_attachments(items, copy_glob, copy_to)
                return
            
            # Extract and format custom fields
            fields = self.bw_client.get_custom_fields(items)
            
            if not fields:
                print(f"No custom fields found in items matching: {search_term}", file=sys.stderr)
                return
            
            # Format and output
            formatter = get_formatter(output_format)
            formatted_lines = formatter.format_fields(fields)
            
            for line in formatted_lines:
                print(line)
                
        except BitwardenError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _authenticate(self) -> None:
        """Handle authentication with Bitwarden."""
        # Try environment variables first
        bw_user = os.getenv('BW_USER')
        bw_password = os.getenv('BW_PASSWORD')
        
        if bw_user:
            self.bw_client.authenticate(email=bw_user, password=bw_password)
        else:
            # This will try ~/.envwarden file or prompt for credentials
            self.bw_client.authenticate()
    
    def _copy_attachments(self, items: List, copy_glob: str, copy_to: str) -> None:
        """Copy attachments matching the glob pattern to the destination folder."""
        # Ensure destination directory exists
        dest_path = Path(copy_to)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Get all attachments
        attachments = self.bw_client.get_attachments(items)
        
        if not attachments:
            print("No attachments found", file=sys.stderr)
            return
        
        # Create a temporary directory for glob matching
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            for item_id, attachment_id, filename in attachments:
                # Create temporary file for glob testing
                temp_file = tmp_path / filename
                temp_file.touch()
                
                # Test if filename matches glob pattern
                if fnmatch.fnmatch(filename, copy_glob):
                    output_file = dest_path / filename
                    try:
                        self.bw_client.download_attachment(
                            attachment_id, item_id, str(output_file)
                        )
                        print(f"Downloaded: {filename}", file=sys.stderr)
                    except BitwardenError as e:
                        print(f"Failed to download {filename}: {e}", file=sys.stderr)
                else:
                    print(f"Skipping {filename}", file=sys.stderr)