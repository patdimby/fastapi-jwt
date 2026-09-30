from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from .jwt_handler import decode_JWT

class JWTBearer(HTTPBearer):
    def __init__(self, auto_Error: bool = True):
        super().__init__(auto_error=False)

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)
        if credentials is None or not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=401, detail="Invalid or missing bearer token", headers={"WWW-Authenticate": "Bearer"})
        return credentials.credentials

    def verify_jwt(self, jwtoken: str):
        payload = decode_JWT(jwtoken)
        return isinstance(payload, dict) and isinstance(payload.get("userID"), str) and bool(payload["userID"])
