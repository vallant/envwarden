"""
Output formatters for envwarden-py
"""

import re
from typing import List, Tuple


class OutputFormatter:
    """Base class for output formatters."""
    
    @staticmethod
    def sanitize_value(value: str) -> str:
        """Sanitize a value to prevent command injection."""
        # Replace single quotes with '"'"' to escape them properly
        return value.replace("'", "'\"'\"'")
    
    def format_fields(self, fields: List[Tuple[str, str]]) -> List[str]:
        """Format fields for output."""
        raise NotImplementedError


class ShellExportFormatter(OutputFormatter):
    """Format fields as shell export statements."""
    
    def format_fields(self, fields: List[Tuple[str, str]]) -> List[str]:
        """Format fields as export statements for shell eval."""
        result = []
        for key, value in fields:
            # Sanitize both key and value
            quoted_key = self.sanitize_value(key)
            quoted_value = self.sanitize_value(value)
            result.append(f"export '{quoted_key}'='{quoted_value}'")
        return result


class DotEnvFormatter(OutputFormatter):
    """Format fields as .env file format."""
    
    def format_fields(self, fields: List[Tuple[str, str]]) -> List[str]:
        """Format fields as KEY="value" for .env files."""
        result = []
        for key, value in fields:
            # Escape double quotes in value
            escaped_value = value.replace('"', '\\"')
            result.append(f'{key}="{escaped_value}"')
        return result


class DotEnvDockerFormatter(OutputFormatter):
    """Format fields as Docker-friendly .env format (no quotes)."""
    
    def format_fields(self, fields: List[Tuple[str, str]]) -> List[str]:
        """Format fields as KEY=value for Docker .env files."""
        result = []
        for key, value in fields:
            result.append(f'{key}={value}')
        return result


class GitHubActionsFormatter(OutputFormatter):
    """Format fields as GitHub Actions output."""
    
    def format_fields(self, fields: List[Tuple[str, str]]) -> List[str]:
        """Format fields as GitHub Actions set-output commands."""
        result = []
        for key, value in fields:
            result.append(f'echo "::set-output name={key}::{value}"')
        return result


def get_formatter(format_type: str) -> OutputFormatter:
    """Get the appropriate formatter for the given type."""
    formatters = {
        'export': ShellExportFormatter(),
        'dotenv': DotEnvFormatter(),
        'dotenv-docker': DotEnvDockerFormatter(),
        'github': GitHubActionsFormatter(),
    }
    
    if format_type not in formatters:
        raise ValueError(f"Unknown format type: {format_type}")
    
    return formatters[format_type]