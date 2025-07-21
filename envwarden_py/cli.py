#!/usr/bin/env python3
"""
Command line interface for envwarden-py
"""

import click
import sys

from .main import EnvwardenApp


@click.command()
@click.option(
    '-s', '--search',
    default='envwarden',
    help='Define the search term for bitwarden items (defaults to "envwarden")'
)
@click.option(
    '-d', '--dotenv',
    'output_format',
    flag_value='dotenv',
    help='Output secrets to stdout in .env format'
)
@click.option(
    '-k', '--dotenv-docker',
    'output_format',
    flag_value='dotenv-docker',
    help='Output secrets to stdout in a "docker-friendly" .env format (no quotes)'
)
@click.option(
    '-g', '--github',
    'output_format',
    flag_value='github',
    help='Output envs in GitHub Actions compliance format'
)
@click.option(
    '-c', '--copy',
    nargs=2,
    type=click.Tuple([str, str]),
    help='Copy attachments matching glob pattern to destination folder'
)
@click.option(
    '-ss', '--skip-sync',
    is_flag=True,
    help='Skip the vault sync (default will sync on every invocation)'
)
@click.option(
    '-h', '--help',
    is_flag=True,
    expose_value=False,
    is_eager=True,
    help='Show this message and exit'
)
def main(search, output_format, copy, skip_sync):
    """
    envwarden-py: Use Bitwarden to manage server secrets
    
    Get your secure environment variables from Bitwarden onto your server.
    envwarden searches your Bitwarden vault for items matching a search criteria
    (defaults to 'envwarden'). Then it goes through all custom fields on every
    item found and makes them available as environment variables.
    
    \b
    Usage Examples:
      To export environment variables: eval $(envwarden-py)
      To create an .env file: envwarden-py --dotenv > .env
      To copy attachments: envwarden-py --copy "*.txt" /path/to/dest
    
    \b
    You can use ~/.envwarden to store your credentials in the format:
      email:password:client_secret
    Or set BW_USER and BW_PASSWORD environment variables.
    """
    
    # Set default output format if none specified
    if not output_format:
        output_format = 'export'
    
    # Create app only when we need it (not for help)
    try:
        app = EnvwardenApp()
        
        if copy:
            copy_glob, copy_to = copy
            app.run(
                search_term=search,
                skip_sync=skip_sync,
                copy_glob=copy_glob,
                copy_to=copy_to
            )
        else:
            app.run(
                search_term=search,
                output_format=output_format,
                skip_sync=skip_sync
            )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()