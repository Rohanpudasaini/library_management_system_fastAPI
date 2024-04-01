import logging
import sys
from decouple import config
from logtail import LogtailHandler

token = config('logging_token')

logger = logging.getLogger("FastAPI Log")

formater = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s"
)

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('app.log')
online_handler = LogtailHandler(source_token=token)

stream_handler.setFormatter(formater)
file_handler.setFormatter(formater)

logger.handlers = [stream_handler, file_handler, online_handler]

logger.setLevel(logging.INFO)
