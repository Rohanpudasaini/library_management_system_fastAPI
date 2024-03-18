import time
# import jwt
from fastapi import HTTPException
from jose import JWTError, jwt
from decouple import config
import error_constant 

# Load information from .env file
JWT_SECRET = config('secret')
JWT_ALGORITHM = config('algorithm')
JWT_SECRET_REFRESH = config('secret_refresh')



# Create access token with userid, i.e email in this case
def encodeAccessJWT(userID: str):
    payload ={
        'userID': userID,
        'expiry': time.time() + 1200
    }
    
    return jwt.encode(payload, JWT_SECRET,JWT_ALGORITHM)
    
    
# Create refresh token with userid, i.e email in this case
def encodeRefreshJWT(userID: str):
    payload ={
        'userID': userID,
        'expiry': time.time() + 604800
    }
    
    return jwt.encode(payload, JWT_SECRET_REFRESH,JWT_ALGORITHM)

    
# Generate tokens, both access and refresh
def generateToken(userID:str):
    return{
        'access_token': encodeAccessJWT(userID),
        'refresh_token': encodeRefreshJWT(userID)
    } 


# Check if the Access JWT is valid
def decodAccessJWT(token:str):
    try:
        decode_token = jwt.decode(token,JWT_SECRET,JWT_ALGORITHM)
        return decode_token if decode_token['expiry'] >= time.time() else None
    except JWTError:
        raise HTTPException(
                    status_code=400,
                    detail=error_constant.TOKEN_VERIFICATION_FAILED
                )
    
    
# Check if the Refresh JWT is valid
def decodRefreshJWT(token:str):
    try:
        decode_token = jwt.decode(token,JWT_SECRET_REFRESH,JWT_ALGORITHM)
        return decode_token if decode_token['expiry'] >= time.time() else None
    except JWTError:
        raise HTTPException(
                    status_code=400,
                    detail=error_constant.TOKEN_VERIFICATION_FAILED
                )