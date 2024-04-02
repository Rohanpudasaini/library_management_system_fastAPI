from .. import models
from database.database_connection import engine
models.Base.metadata.create_all(bind=engine)
