"""
Tests for output formatters
"""

import unittest
from envwarden_py.formatters import (
    ShellExportFormatter,
    DotEnvFormatter, 
    DotEnvDockerFormatter,
    GitHubActionsFormatter,
    get_formatter
)


class TestFormatters(unittest.TestCase):
    """Test output formatters."""
    
    def setUp(self):
        self.test_fields = [
            ('API_KEY', 'secret123'),
            ('DB_PASSWORD', 'password with spaces'),
            ('SPECIAL_CHARS', "value'with\"quotes"),
        ]
    
    def test_shell_export_formatter(self):
        """Test shell export formatter."""
        formatter = ShellExportFormatter()
        result = formatter.format_fields(self.test_fields)
        
        expected = [
            "export 'API_KEY'='secret123'",
            "export 'DB_PASSWORD'='password with spaces'",
            "export 'SPECIAL_CHARS'='value'\"'\"'with\"quotes'",
        ]
        
        self.assertEqual(result, expected)
    
    def test_dotenv_formatter(self):
        """Test .env formatter."""
        formatter = DotEnvFormatter()
        result = formatter.format_fields(self.test_fields)
        
        expected = [
            'API_KEY="secret123"',
            'DB_PASSWORD="password with spaces"',
            'SPECIAL_CHARS="value\'with\\"quotes"',
        ]
        
        self.assertEqual(result, expected)
    
    def test_dotenv_docker_formatter(self):
        """Test Docker .env formatter."""
        formatter = DotEnvDockerFormatter()
        result = formatter.format_fields(self.test_fields)
        
        expected = [
            'API_KEY=secret123',
            'DB_PASSWORD=password with spaces',
            'SPECIAL_CHARS=value\'with"quotes',
        ]
        
        self.assertEqual(result, expected)
    
    def test_github_actions_formatter(self):
        """Test GitHub Actions formatter."""
        formatter = GitHubActionsFormatter()
        result = formatter.format_fields(self.test_fields)
        
        expected = [
            'echo "::set-output name=API_KEY::secret123"',
            'echo "::set-output name=DB_PASSWORD::password with spaces"',
            'echo "::set-output name=SPECIAL_CHARS::value\'with\"quotes"',
        ]
        
        self.assertEqual(result, expected)
    
    def test_get_formatter(self):
        """Test formatter factory function."""
        self.assertIsInstance(get_formatter('export'), ShellExportFormatter)
        self.assertIsInstance(get_formatter('dotenv'), DotEnvFormatter)
        self.assertIsInstance(get_formatter('dotenv-docker'), DotEnvDockerFormatter)
        self.assertIsInstance(get_formatter('github'), GitHubActionsFormatter)
        
        with self.assertRaises(ValueError):
            get_formatter('invalid')
    
    def test_sanitize_value(self):
        """Test value sanitization for shell export."""
        formatter = ShellExportFormatter()
        
        # Test single quote escaping
        result = formatter.sanitize_value("value'with'quotes")
        expected = "value'\"'\"'with'\"'\"'quotes"
        self.assertEqual(result, expected)
        
        # Test no quotes
        result = formatter.sanitize_value("simple_value")
        expected = "simple_value"
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()