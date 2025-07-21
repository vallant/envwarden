#!/usr/bin/env python3
"""
Demo script to show envwarden-py functionality
"""

import sys
import os
from envwarden_py.formatters import get_formatter

def demo_formatters():
    """Demonstrate different output formatters."""
    print("=== envwarden-py Demo ===\n")
    
    # Sample data that would come from Bitwarden
    sample_fields = [
        ('API_KEY', 'secret_api_key_123'),
        ('DATABASE_URL', 'postgresql://user:pass@localhost/db'),
        ('DEBUG_MODE', 'true'),
        ('SPECIAL_CHARS', "value with 'quotes' and \"double quotes\""),
    ]
    
    # Test all formatters
    formats = {
        'export': 'Shell Export (for eval)',
        'dotenv': '.env format',
        'dotenv-docker': 'Docker .env format (no quotes)',
        'github': 'GitHub Actions format'
    }
    
    for format_type, description in formats.items():
        print(f"--- {description} ---")
        formatter = get_formatter(format_type)
        output = formatter.format_fields(sample_fields)
        for line in output:
            print(line)
        print()

if __name__ == '__main__':
    demo_formatters()
    
    print("=== CLI Usage Examples ===")
    print("To use envwarden-py (requires Bitwarden CLI 'bw' to be installed):")
    print()
    print("# Basic usage - export environment variables")
    print("eval $(envwarden-py)")
    print()
    print("# Create .env file")
    print("envwarden-py --dotenv > .env")
    print()
    print("# Search for specific items")
    print("envwarden-py --search production")
    print()
    print("# Copy attachments")
    print("envwarden-py --copy '*.cert' /etc/ssl/certs/")
    print()
    print("# Skip vault sync")
    print("envwarden-py --skip-sync")
    print()
    print("# GitHub Actions format")
    print("envwarden-py --github")
    print()
    print("# Get help")
    print("envwarden-py --help")