from dbos import DBOS
import requests
from .app import logging, engine
from .schema import dbos_hello, table_2

# Sign the guestbook using an HTTP POST request
@DBOS.step()
def sign_guestbook(name: str):
    requests.post(
        "https://demo-guestbook.cloud.dbos.dev/record_greeting",
        headers={"Content-Type": "application/json"},
        json={"name": name},
    )
    logging.info(f">>> STEP 1: Signed the guestbook for {name}")



# Record the greeting in the database using SQLAlchemy
@DBOS.step()
def insert_greeting(name: str) -> str:
    with engine.begin() as sql_session:
        query = dbos_hello.insert().values(name=name)
        sql_session.execute(query)
        query_2 = table_2.insert().values(naz=name)
        sql_session.execute(query_2)
    logging.info(f">>> STEP 2: Greeting to {name} recorded in the database tables dbos_hello and table_2!")

