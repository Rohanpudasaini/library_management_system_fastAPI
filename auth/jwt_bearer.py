from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import decodJWT
class JwtBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JwtBearer, self).__init__(auto_error=auto_error) 

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials = await super(JwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code= 403,
                    detail= "Invalid or expired Token!"
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403,
                    detail="Invalid or expired token"
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code= 403,
                detail= "Invalid or expired Token!"
            )
    
    def verify_jwt(self, jwtoken:str):
        isTokenValid:bool = False
        payload = decodJWT(jwtoken)
        
        if payload:
            isTokenValid = True
        return isTokenValid