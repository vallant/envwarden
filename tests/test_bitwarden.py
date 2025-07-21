"""
Tests for Bitwarden client (mocked)
"""

import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from envwarden_py.bitwarden import BitwardenClient, BitwardenError


class TestBitwardenClient(unittest.TestCase):
    """Test Bitwarden client functionality."""
    
    def setUp(self):
        # Mock the CLI check so we can test without having bw installed
        with patch('envwarden_py.bitwarden.BitwardenClient._check_bw_cli'):
            self.client = BitwardenClient()
    
    @patch('subprocess.run')
    def test_check_bw_cli_success(self, mock_run):
        """Test successful CLI check."""
        mock_run.return_value = MagicMock(returncode=0)
        # Should not raise exception
        BitwardenClient()
    
    @patch('subprocess.run')
    def test_check_bw_cli_failure(self, mock_run):
        """Test CLI check failure."""
        mock_run.side_effect = FileNotFoundError()
        with self.assertRaises(BitwardenError):
            BitwardenClient()
    
    @patch('subprocess.run')
    def test_run_bw_command_success(self, mock_run):
        """Test successful command execution."""
        mock_run.return_value = MagicMock(stdout='test output\n', returncode=0)
        result = self.client._run_bw_command(['status'], check_session=False)
        self.assertEqual(result, 'test output')
    
    @patch('subprocess.run')
    def test_run_bw_command_failure(self, mock_run):
        """Test failed command execution."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'bw', stderr='error message')
        with self.assertRaises(BitwardenError):
            self.client._run_bw_command(['status'], check_session=False)
    
    def test_load_credentials_from_file(self):
        """Test loading credentials from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.envwarden') as f:
            f.write('user@example.com:password:secret')
            temp_file = f.name
        
        try:
            # Mock the Path.home() and file operations
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(temp_file).parent
                with patch('pathlib.Path.exists') as mock_exists:
                    mock_exists.return_value = True
                    with patch('builtins.open', create=True) as mock_open:
                        mock_open.return_value.__enter__.return_value.read.return_value = 'user@example.com:password:secret'
                        email, password, client_secret = self.client._load_credentials()
                        
            self.assertEqual(email, 'user@example.com')
            self.assertEqual(password, 'password')
            self.assertEqual(client_secret, 'secret')
        finally:
            os.unlink(temp_file)
    
    def test_load_credentials_no_file(self):
        """Test loading credentials when file doesn't exist."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            email, password, client_secret = self.client._load_credentials()
            
        self.assertIsNone(email)
        self.assertIsNone(password)
        self.assertIsNone(client_secret)
    
    def test_get_custom_fields(self):
        """Test extracting custom fields from items."""
        items = [
            {
                'id': '1',
                'fields': [
                    {'name': 'API_KEY', 'value': 'secret123'},
                    {'name': 'DB_PASSWORD', 'value': 'dbpass'},
                    {'name': None, 'value': 'should_be_ignored'},
                    {'name': 'EMPTY_VALUE', 'value': None},
                ]
            },
            {
                'id': '2',
                'fields': [
                    {'name': 'ANOTHER_KEY', 'value': 'another_value'},
                ]
            }
        ]
        
        fields = self.client.get_custom_fields(items)
        expected = [
            ('API_KEY', 'secret123'),
            ('DB_PASSWORD', 'dbpass'),
            ('ANOTHER_KEY', 'another_value'),
        ]
        
        self.assertEqual(fields, expected)
    
    def test_get_attachments(self):
        """Test extracting attachments from items."""
        items = [
            {
                'id': 'item1',
                'attachments': [
                    {'id': 'attach1', 'fileName': 'file1.txt'},
                    {'id': 'attach2', 'fileName': 'file2.pdf'},
                ]
            },
            {
                'id': 'item2',
                'attachments': [
                    {'id': 'attach3', 'fileName': 'file3.zip'},
                ]
            }
        ]
        
        attachments = self.client.get_attachments(items)
        expected = [
            ('item1', 'attach1', 'file1.txt'),
            ('item1', 'attach2', 'file2.pdf'),
            ('item2', 'attach3', 'file3.zip'),
        ]
        
        self.assertEqual(attachments, expected)
    
    @patch('envwarden_py.bitwarden.BitwardenClient._run_bw_command')
    def test_search_items(self, mock_run):
        """Test searching for items."""
        mock_response = [
            {'id': '1', 'name': 'Test Item'},
            {'id': '2', 'name': 'Another Item'}
        ]
        mock_run.return_value = json.dumps(mock_response)
        
        result = self.client.search_items('test')
        self.assertEqual(result, mock_response)
        mock_run.assert_called_once_with(['list', 'items', '--search', 'test'])


if __name__ == '__main__':
    unittest.main()