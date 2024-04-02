from auth import auth
from logger import logger
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

