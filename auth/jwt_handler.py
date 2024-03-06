import time
import jwt
from decouple import config

JWT_SECRET = config('secret')
JWT_ALGORITHM = config('algorithm')
JWT_SECRET_REFRESH = config('secret_refresh')


    
def encodeAccessJWT(userID: str):
    payload ={
        'userID': userID,
        'expiry': time.time() + 1200
    }
    
    return jwt.encode(payload, JWT_SECRET,JWT_ALGORITHM)
    
    

def encodeRefreshJWT(userID: str):
    payload ={
        'userID': userID,
        'expiry': time.time() + 604800
    }
    
    return jwt.encode(payload, JWT_SECRET_REFRESH,JWT_ALGORITHM)

    

def generateToken(userID:str):
    return{
        'access_token': encodeAccessJWT(userID),
        'refresh_token': encodeRefreshJWT(userID)
    } 


def decodJWT(token:str):
    try:
        decode_token = jwt.decode(token,JWT_SECRET,JWT_ALGORITHM)
        return decode_token if decode_token['expiry'] >= time.time() else None
    except jwt.InvalidTokenError:
        print("Error")
        return {}
    
def decodRefreshJWT(token:str):
    try:
        decode_token = jwt.decode(token,JWT_SECRET_REFRESH,JWT_ALGORITHM)
        return decode_token if decode_token['expiry'] >= time.time() else None
    except jwt.InvalidTokenError:
        print("Error")
        return {}