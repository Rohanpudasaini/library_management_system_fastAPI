import time

from fastapi.responses import StreamingResponse
from auth import auth
from starlette.middleware.base import BaseHTTPMiddleware 
from utils.logger import logger
import json
from fastapi import HTTPException, Header, Response


async def log_request(request):
    log_dict = {
        'url_host': request.url.hostname,
        'url_path': request.url.path,
        'url_query': request.url.query,
        'method': request.method,
    }
    logger.info(log_dict, extra=log_dict)


async def log_response(response):
    body = b''.join([section async for section in response.body_iterator])
    logger.info(json.loads(body.decode()))
    return Response(content=body, status_code=response.status_code, headers=dict(response.headers))


def token_in_header(Authorization: str = Header(None)):
    if Authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing"
        )
    token_splitted = Authorization.split(" ", 1)
    if token_splitted[0].lower() == 'bearer':
        return auth.decodAccessJWT(token_splitted[1])
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid token Scheme"
        )

class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths=None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []

    async def dispatch(self, request, call_next):

        # Log the request details
        log_dict = {
            'method': request.method,
            'url': str(request.url),
            'url_host': request.url.hostname,
            'url_path': request.url.path,
            'url_query': request.url.query,
        }
        logger.info(f"Request: {log_dict}", extra=log_dict)

        if request.url.path in self.exclude_paths:
            return await call_next(request)
        start_time = time.time()

        # Get the response
        response = await call_next(request)
        
        process_time = time.time() - start_time

        if response:
            print(type(response))
            body = b''.join([section async for section in response.body_iterator])
            response_body = body.decode('utf-8')
            print(response.status_code)
            if response.status_code >=400 and response.status_code <600:
                logger.warning(f"Response body: {response_body} Process time: {process_time}")
            else:
                logger.info(f"Response body: {response_body} Process time: {process_time}")
            # Create a new response with the logged body to ensure it's not consumed
            response.headers['X-Process-Time'] = str(process_time)
            return Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
        else:
            return response
