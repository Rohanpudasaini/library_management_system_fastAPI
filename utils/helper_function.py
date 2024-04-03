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


def token_in_header(Authorization: str = Header()):
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
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Log the request details
        log_dict = {
            'method': request.method,
            'url': str(request.url),
        }
        logger.info(f"Request: {log_dict}")
        
        start_time = time.time()

        # Get the response
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Only log response body if it's not a streaming response
        # if not isinstance(response, StreamingResponse):
        if response:
            body = b''.join([section async for section in response.body_iterator])
            response_body = body.decode('utf-8')
            logger.info(f"Response body: {response_body} Process time: {process_time}")
            # Create a new response with the logged body to ensure it's not consumed
            return Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)
        else:
            logger.info(f"Skipped logging body for streaming response. Process time: {process_time}")
            return response
