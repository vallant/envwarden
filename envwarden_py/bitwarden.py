"""
Bitwarden CLI interface for envwarden-py
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BitwardenError(Exception):
    """Exception raised for Bitwarden-related errors."""
    pass


class BitwardenClient:
    """Interface to Bitwarden CLI."""
    
    def __init__(self):
        self.session_token: Optional[str] = None
        self._check_bw_cli()
    
    def _check_bw_cli(self) -> None:
        """Check if Bitwarden CLI is available."""
        try:
            subprocess.run(['bw', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise BitwardenError(
                "Bitwarden CLI (bw) not found. Please install it from "
                "https://github.com/bitwarden/cli"
            )
    
    def _run_bw_command(self, args: List[str], check_session: bool = True) -> str:
        """Run a Bitwarden CLI command."""
        env = os.environ.copy()
        if check_session and self.session_token:
            env['BW_SESSION'] = self.session_token
        
        try:
            result = subprocess.run(
                ['bw'] + args,
                capture_output=True,
                text=True,
                env=env,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else ""
            raise BitwardenError(f"Bitwarden command failed: {stderr}")
    
    def authenticate(self, email: Optional[str] = None, password: Optional[str] = None, 
                    client_secret: Optional[str] = None) -> None:
        """Authenticate with Bitwarden."""
        # Check if already authenticated via BW_SESSION environment variable
        if os.getenv('BW_SESSION'):
            self.session_token = os.getenv('BW_SESSION')
            return
        
        # Try to load credentials from ~/.envwarden file
        if not email and not password:
            email, password, client_secret = self._load_credentials()
        
        # Logout first to ensure clean state
        try:
            self._run_bw_command(['logout'], check_session=False)
        except BitwardenError:
            pass  # Ignore logout errors
        
        # Set client secret if provided
        env = os.environ.copy()
        if client_secret:
            env['BW_CLIENTSECRET'] = client_secret
        
        # Login and get session token
        login_args = ['login']
        if email:
            login_args.append(email)
        if password:
            login_args.append(password)
        login_args.append('--raw')
        
        try:
            result = subprocess.run(
                ['bw'] + login_args,
                capture_output=True,
                text=True,
                env=env,
                check=True
            )
            self.session_token = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else ""
            raise BitwardenError(f"Authentication failed: {stderr}")
    
    def _load_credentials(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Load credentials from ~/.envwarden file."""
        envwarden_file = Path.home() / '.envwarden'
        if not envwarden_file.exists():
            return None, None, None
        
        try:
            with open(envwarden_file, 'r') as f:
                content = f.read().strip()
            
            parts = content.split(':')
            if len(parts) == 1:
                return parts[0], None, None
            elif len(parts) == 2:
                return parts[0], parts[1], None
            elif len(parts) >= 3:
                return parts[0], parts[1], parts[2]
            else:
                return None, None, None
        except Exception:
            return None, None, None
    
    def sync(self) -> None:
        """Sync the Bitwarden vault."""
        try:
            self._run_bw_command(['sync'])
        except BitwardenError as e:
            raise BitwardenError(f"Unable to sync with Bitwarden: {e}")
    
    def search_items(self, search_term: str) -> List[Dict]:
        """Search for items in the vault."""
        try:
            output = self._run_bw_command(['list', 'items', '--search', search_term])
            return json.loads(output)
        except json.JSONDecodeError as e:
            raise BitwardenError(f"Failed to parse Bitwarden response: {e}")
    
    def get_custom_fields(self, items: List[Dict]) -> List[Tuple[str, str]]:
        """Extract custom fields from items."""
        fields = []
        for item in items:
            if 'fields' in item and item['fields']:
                for field in item['fields']:
                    if field.get('name') and field.get('value'):
                        fields.append((field['name'], field['value']))
        return fields
    
    def get_attachments(self, items: List[Dict]) -> List[Tuple[str, str, str]]:
        """Get attachments from items. Returns list of (item_id, attachment_id, filename)."""
        attachments = []
        for item in items:
            if 'attachments' in item and item['attachments']:
                for attachment in item['attachments']:
                    if 'id' in attachment and 'fileName' in attachment:
                        attachments.append((
                            item['id'],
                            attachment['id'],
                            attachment['fileName']
                        ))
        return attachments
    
    def download_attachment(self, attachment_id: str, item_id: str, output_path: str) -> None:
        """Download an attachment to the specified path."""
        try:
            self._run_bw_command([
                'get', 'attachment', attachment_id,
                '--itemid', item_id,
                '--output', output_path
            ])
        except BitwardenError as e:
            raise BitwardenError(f"Failed to download attachment: {e}")