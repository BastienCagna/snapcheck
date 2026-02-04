"""
Provides authentication functionalities for the SnapServe application.

See FastAPI documentation for more details:
https://fastapi.tiangolo.com/tutorial/security
"""
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from os import getenv

DEFAULT_TIME_DELTA_MINUTES = 60 * 24 * 30  # 30 days
DEFAULT_ALGORITHM = "HS256"
SECRET_KEY_NAME = "SNAP_SECRET"

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# HTTP Bearer scheme (expects an Authorization: Bearer <JWT>)
bearer_scheme = HTTPBearer(auto_error=False)


class Token(BaseModel):
    access_token: str
    token_type: str | None = None


class TokenData(BaseModel):
    username: str | None = None
    expire: datetime | None = None


def create_access_token(data: TokenData, expires_delta: timedelta | None = None, algorithm: str = DEFAULT_ALGORITHM, secret: str = None):
    to_encode = data.dict().copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=DEFAULT_TIME_DELTA_MINUTES)
    to_encode.update({"expire": expire.timestamp()})
    if not secret:
        secret = getenv(SECRET_KEY_NAME, None)
        if not secret:
            raise ValueError(f"Not secret phrase. Either give à secret phrase to the function or set the environment variable {SECRET_KEY_NAME}.")
    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded_jwt


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """
    Verify JWT token signature.
    Raises HTTPException if token is invalid or expired.
    """
    try:
        if credentials is None or not credentials.scheme.lower() == "bearer":
            raise CREDENTIALS_EXCEPTION

        token = credentials.credentials
        secret = getenv(SECRET_KEY_NAME, None)
        if not secret:
            raise CREDENTIALS_EXCEPTION
        
        payload = jwt.decode(token, secret, algorithms=[DEFAULT_ALGORITHM])
        username: str = payload.get("username")
        expire_timestamp: float = payload.get("expire")
        
        if username is None or expire_timestamp is None:
            raise CREDENTIALS_EXCEPTION
        
        # Check if token is expired
        if datetime.now(timezone.utc).timestamp() > expire_timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(username=username, expire=datetime.fromtimestamp(expire_timestamp, tz=timezone.utc))
    
    except jwt.InvalidTokenError:
        raise CREDENTIALS_EXCEPTION


