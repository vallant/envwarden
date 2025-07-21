#!/usr/bin/env python3
"""
Test the help functionality of envwarden-py CLI
"""

import sys
from unittest.mock import patch

# Add the envwarden_py to path
sys.path.insert(0, '/home/runner/work/envwarden/envwarden')

# Patch the CLI check before importing
with patch('envwarden_py.bitwarden.BitwardenClient._check_bw_cli'):
    from envwarden_py.cli import main
    
    # Test help
    print("=== envwarden-py Help Output ===\n")
    
    with patch('sys.argv', ['envwarden-py', '--help']):
        try:
            main()
        except SystemExit:
            pass  # Expected when Click shows help