"""Issue and verify signed access tokens; invalid tokens never yield truthy errors."""
import time
import jwt
from decouple import config

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm", default="HS256")
if JWT_ALGORITHM != "HS256" or len(JWT_SECRET.encode()) < 32:
    raise ValueError("Use HS256 with a secret of at least 32 UTF-8 bytes")

def token_response(token: str):
    # Preserve the original response field for existing clients.
    return {"access token": token}

def signJWT(userID: str):
    payload = {"userID": userID, "exp": int(time.time()) + 3600}
    return token_response(jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM))

def decode_JWT(token: str):
    try:
        # PyJWT enforces exp; require the identity and expiry claims to be present.
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"require": ["exp", "userID"]})
    except jwt.InvalidTokenError:
        return None
