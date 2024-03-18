from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import decodAccessJWT
import error_constant 

class JwtBearer(HTTPBearer):
    """
    Simple Class that extends HTTPBearer class of fastapi
    The HTTPBearer class is used to locate the token in the request header
    Also check if the token scheme is Bearer and validate it.
    """
    
    def __init__(self, auto_error: bool = False):
        """
        Initilize the parent class so it can take the token from the request header
        
        auto_error: If true any exception will be handeled by parents already defined
        exceptions and message, i.e if auto error is true,
        and no token given while sending request, it will give 
        'Authentication required' as error message.
        On other hand if auto_error is false same problem will 
        have 'No token available!' error message.
        """
        super(JwtBearer, self).__init__(auto_error=auto_error) 

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        """
        Await for parents to parse the request and get the token,
        and check if token is 'Bearer' or not, also verify the
        authenticity of the token.
        
        """
        credentials: HTTPAuthorizationCredentials = await super(JwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code= 403,
                    detail= error_constant.INVALID_TOKEN_SCHEME
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=400,
                    detail= error_constant.TOKEN_VERIFICATION_FAILED
,
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code= 403,
                detail= error_constant.NO_TOKEN_IN_HEADER
            )
    
    def verify_jwt(self, jwtoken:str):
        """
        Function to validate the token and return true if valid
        """
        isTokenValid:bool = False
        payload = decodAccessJWT(jwtoken)
        if payload:
            isTokenValid = True
        return isTokenValid