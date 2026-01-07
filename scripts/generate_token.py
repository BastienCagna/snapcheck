import sys
import os
from snapserve.auth import TokenData, create_access_token



username = os.getlogin()

token = create_access_token(TokenData(username=username), secret=sys.argv[1])

print(token)