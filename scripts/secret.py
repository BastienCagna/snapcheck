
import secrets
import sys

DEFAULT_LENGTH = 32

length = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LENGTH
print(secrets.token_urlsafe(length))
