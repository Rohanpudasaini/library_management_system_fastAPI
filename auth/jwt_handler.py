import time
import jwt
from decouple import config

JWT_SECRET = config('secret')
JWT_ALGORITHM = config('algorithm')

# def token_response(token:str):
    # return {
    #     'access token': token
    # }
    
def encodeJWT(userID: str):
    payload ={
        'userID': userID,
        'expiry': time.time() + 3600
    }
    
    token = jwt.encode(payload, JWT_SECRET,JWT_ALGORITHM)
    return {
        'access token': token
    }
    
def decodJWT(token:str):
    try:
        decode_token = jwt.decode(token,JWT_SECRET,JWT_ALGORITHM)
        return decode_token if decode_token['expiry'] >= time.time() else None
    except jwt.InvalidTokenError:
        return {}