import argparse

parser = argparse.ArgumentParser(
    "use Bitwarden to manage server secrets",
    description="Get your secure environment variables from Bitwarden onto your server."
    "envwarden searches your Bitwarden vault for items matching"
    "a search criteria (defaults to 'envwarden')."
    "Then it goes through all custom fields on every item found"
    "and make them available as environment variables."
    "You can use ~/.envwarden to store your credentials (email, email:password, or email:password:client_secret)"
    "See https://bitwarden.com/help/article/cli-auth-challenges/#get-your-personal-api-key",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument("-s", "--search", help="define the search term for bitwarden items", default="envwarden")
parser.add_argument("-d", "--dotenv", action="store_true", help="outputs secrets to stdout in .env format")
parser.add_argument("-k", "--dotenv-docker", action="store_true", help="outputs secrets to stdout in a 'docker-friendly' .env format (no quotes)")
parser.add_argument("-c", "--copy", nargs=2, metavar=("glob", "dest"), help="copies attachments matching glob pattern to a folder")
parser.add_argument("-g", "--github", help="envs to github actions", action="store_true")
parser.add_argument("-ss", "--skip-sync", action="store_true", help="skip the vault sync (default will sync on every invocation)")

args = parser.parse_args()
