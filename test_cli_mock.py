#!/usr/bin/env python3
"""
Test CLI functionality by mocking the Bitwarden CLI
"""

import json
import tempfile
from unittest.mock import patch, MagicMock
import sys
import os

# Add the envwarden_py to path
sys.path.insert(0, '/home/runner/work/envwarden/envwarden')

from envwarden_py.main import EnvwardenApp


def mock_bw_response():
    """Mock response from Bitwarden CLI."""
    return [
        {
            "id": "item1",
            "name": "Test Item 1", 
            "fields": [
                {"name": "API_KEY", "value": "secret123"},
                {"name": "DATABASE_URL", "value": "postgresql://localhost/myapp"},
                {"name": "DEBUG", "value": "true"}
            ]
        },
        {
            "id": "item2", 
            "name": "Test Item 2",
            "fields": [
                {"name": "REDIS_URL", "value": "redis://localhost:6379"},
                {"name": "EMAIL_PASSWORD", "value": "email_pass_123"}
            ]
        }
    ]


def test_app_formats():
    """Test different app output formats."""
    
    print("=== Testing envwarden-py Application ===\n")
    
    # Mock the Bitwarden CLI at the app level
    with patch('envwarden_py.bitwarden.BitwardenClient._check_bw_cli'):
        with patch('envwarden_py.bitwarden.BitwardenClient.authenticate'):
            with patch('envwarden_py.bitwarden.BitwardenClient.sync'):
                with patch('envwarden_py.bitwarden.BitwardenClient.search_items') as mock_search:
                    mock_search.return_value = mock_bw_response()
                    
                    # Test different formats
                    formats = [
                        ('export', 'Shell Export Format'),
                        ('dotenv', '.env Format'), 
                        ('dotenv-docker', 'Docker .env Format'),
                        ('github', 'GitHub Actions Format')
                    ]
                    
                    for format_type, description in formats:
                        print(f"--- {description} ---")
                        
                        app = EnvwardenApp()
                        app.run(
                            search_term='envwarden',
                            output_format=format_type,
                            skip_sync=False
                        )
                        
                        print()


if __name__ == '__main__':
    test_app_formats()