from dbos import DBOS, get_dbos_database_url
from fastapi import FastAPI
from sqlalchemy import create_engine
import logging

from fastapi import Depends

from starlette.middleware.base import BaseHTTPMiddleware
from .security import JwtMiddleware

# https://docs.dbos.dev/python/reference/configuration
FISKALNI_IOSA = DBOS.config["application"]["fiskalni"]["iosa"]
FISKALNI_SERIAL = DBOS.config["application"]["fiskalni"]["serial"]
FISKALNI_OPERATER = DBOS.config["application"]["fiskalni"]["operater"]
FISKALNI_OPERATER_PASSWORD = DBOS.config["application"]["fiskalni"]["operater_password"]


OUT_DIR= r"c:\fiscal"
ANSWER_DIR= r"c:\fiscal\answer"

app = FastAPI(
   #dependencies=[Depends(jwtAuthMiddleware)]     
)

#jwt_middleware = JwtMiddleware()
#app.add_middleware(BaseHTTPMiddleware, dispatch=jwt_middleware)

print("fastapi=app")
DBOS(fastapi=app)

# Create a SQLAlchemy engine. Adjust this connection string for your database.
engine = create_engine(get_dbos_database_url())

logging.basicConfig(level=logging.INFO)
