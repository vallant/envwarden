# envwarden-py

Python implementation of [envwarden](https://github.com/envwarden/envwarden) - manage your server secrets with [Bitwarden](https://bitwarden.com/).

## Overview

`envwarden-py` is a Python re-implementation of the original bash-based `envwarden` tool. It provides the same functionality with improved error handling, better testing, and more maintainable code structure.

## Features

- **Bitwarden Integration**: Authenticates with Bitwarden and searches your vault for items
- **Multiple Output Formats**: 
  - Shell export format (for `eval`)
  - `.env` file format
  - Docker-friendly `.env` format (no quotes)
  - GitHub Actions output format
- **Attachment Support**: Download and copy attachments with glob pattern matching
- **Flexible Authentication**: Support for credentials file, environment variables, or interactive login
- **Security**: Proper quote escaping to prevent command injection

## Installation

### Prerequisites

1. Install the [Bitwarden CLI](https://github.com/bitwarden/cli):
   ```bash
   npm install -g @bitwarden/cli
   ```

2. Install envwarden-py:
   ```bash
   pip install -e .
   ```

### With Docker

A Docker image can be built using the existing Dockerfile, but replacing the bash script with the Python implementation.

## Usage

### Basic Usage

```bash
# Export environment variables
eval $(envwarden-py)

# Create a .env file
envwarden-py --dotenv > .env

# Search for specific items
envwarden-py --search production

# Copy attachments matching pattern
envwarden-py --copy "*.cert" /etc/ssl/certs/

# Skip vault synchronization
envwarden-py --skip-sync

# GitHub Actions output format
envwarden-py --github
```

### Command Line Options

```
Usage: envwarden-py [OPTIONS]

Options:
  -s, --search TEXT       Search term for Bitwarden items (default: 'envwarden')
  -d, --dotenv           Output in .env format
  -k, --dotenv-docker    Output in Docker .env format (no quotes)
  -g, --github           Output in GitHub Actions format
  -c, --copy GLOB PATH   Copy attachments matching GLOB to PATH
  -ss, --skip-sync       Skip vault synchronization
  -h, --help             Show help message
```

### Authentication

`envwarden-py` supports multiple authentication methods:

1. **Environment Variables**: Set `BW_USER` and `BW_PASSWORD`
2. **Credentials File**: Create `~/.envwarden` with format:
   ```
   email:password:client_secret
   ```
3. **Interactive**: The tool will prompt for credentials if none are found

## Setting up Secrets in Bitwarden

1. Create an item in Bitwarden (e.g., named "production secrets")
2. Add custom fields for each environment variable you need:
   - Field name becomes the environment variable name
   - Field value becomes the environment variable value
3. Ensure the item name or other searchable content matches your search term

## Output Formats

### Shell Export (Default)
```bash
export 'API_KEY'='secret123'
export 'DB_PASSWORD'='mypassword'
```

### .env Format
```bash
API_KEY="secret123"
DB_PASSWORD="mypassword"
```

### Docker .env Format
```bash
API_KEY=secret123
DB_PASSWORD=mypassword
```

### GitHub Actions Format
```bash
echo "::set-output name=API_KEY::secret123"
echo "::set-output name=DB_PASSWORD::mypassword"
```

## Development

### Running Tests

```bash
python -m unittest discover tests/ -v
```

### Project Structure

```
envwarden_py/
├── __init__.py          # Package initialization
├── cli.py              # Command-line interface
├── main.py             # Main application logic
├── bitwarden.py        # Bitwarden CLI interface
└── formatters.py       # Output format handlers

tests/
├── test_bitwarden.py   # Bitwarden client tests
└── test_formatters.py  # Output formatter tests
```

## Comparison with Original

| Feature | Bash Version | Python Version |
|---------|-------------|----------------|
| Core functionality | ✅ | ✅ |
| Output formats | ✅ | ✅ |
| Attachment copying | ✅ | ✅ |
| Error handling | Basic | Enhanced |
| Testing | None | Comprehensive |
| Code organization | Single script | Modular |
| Dependencies | bash, jq, bw | Python 3.7+, click, bw |

## Security

- Proper quote sanitization prevents command injection
- Secure handling of sensitive environment variables
- No secrets are logged or exposed in error messages

## License

MIT License - same as the original envwarden project.