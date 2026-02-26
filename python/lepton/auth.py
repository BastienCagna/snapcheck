"""
Provides authentication functionalities for the SnapServe application.

See FastAPI documentation for more details:
https://fastapi.tiangolo.com/tutorial/security
"""

from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone

DEFAULT_TIME_DELTA_MINUTES = 60 * 24 * 30  # 30 days
DEFAULT_ALGORITHM = "HS256"

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
    expire: datetime | None = None
    sid: str | None = None


class Authenticator(BaseModel):
    secret: str
    token_expire_minutes: int = DEFAULT_TIME_DELTA_MINUTES
    algorithm: str = DEFAULT_ALGORITHM

    def create_access_token(self, data: TokenData):
        to_encode = data.model_dump().copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.token_expire_minutes)
        to_encode.update({"expire": expire.timestamp()})

        encoded_jwt = jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
        return encoded_jwt

    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
        """
        Verify JWT token signature.
        Raises HTTPException if token is invalid or expired.
        """
        try:
            if credentials is None or not credentials.scheme.lower() == "bearer":
                raise CREDENTIALS_EXCEPTION

            token = credentials.credentials
            if not self.secret:
                raise CREDENTIALS_EXCEPTION

            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            expire_timestamp: float = payload.get("expire")
            sid: str | None = payload.get("sid")

            if sid is None or expire_timestamp is None:
                raise CREDENTIALS_EXCEPTION

            # Check if token is expired
            if datetime.now(timezone.utc).timestamp() > expire_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return TokenData(
                expire=datetime.fromtimestamp(expire_timestamp, tz=timezone.utc),
                sid=sid,
            )

        except jwt.InvalidTokenError:
            raise CREDENTIALS_EXCEPTION
