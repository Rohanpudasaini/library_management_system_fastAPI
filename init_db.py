import models
from database_connection import engine
models.Base.metadata.create_all(bind=engine)
