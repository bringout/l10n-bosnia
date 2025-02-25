from dbos import DBOS
import tempfile
from .app import OUT_DIR, ANSWER_DIR, logging, engine
from .schema import fiscal_log
import re
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa
import datetime
import os, time

COUNT_FAIL=60
@DBOS.step()

def fprint_duplikat(tip: str, od: datetime.datetime, do: datetime.datetime):

  # Z - dnevni
  # R - refund
  # F - racun

  #109,1,______,_,__;R;210225123000;210225123100;0;

  s_od = od.strftime("%d%m%y%H%M%S")
  s_do = do.strftime("%d%m%y%H%M%S")
  
  content=f"109,1,______,_,__;{tip};{s_od};{s_do};0;"
  file_name = ""
  # https://stackoverflow.com/questions/3924117/how-to-use-tempfile-namedtemporaryfile-in-python
  with tempfile.NamedTemporaryFile(dir=OUT_DIR, suffix=".txt", delete=False) as f:
    file_name = f.name
    logging.info(f"file: {file_name}")
  
    # https://docs.python.org/3.12/library/codecs.html#standard-encodings
    f.write(content.encode(encoding='cp1250'))
    f.flush()

    with engine.begin() as sql_session:
      query = fiscal_log.insert().values(input=content, input_file=file_name, type='REPORT', input_number='DUPLIKAT')
      sql_session.execute(query)
     
      stmt = fiscal_log.select().where(fiscal_log.c.input_file == file_name)
      stmt = stmt.where(sa.cast(fiscal_log.c.created, sa.Date) == datetime.date.today())
      stmt = stmt.where(fiscal_log.c.input_number == 'DUPLIKAT')
      result = sql_session.execute(stmt)


      return (result.first())._mapping["id"]



@DBOS.step()
def fprint_duplikat_response(id: UUID):
  
  # input = c:\\fiscal\\tmp1.txt => answer = c:\\fiscal\\answer\\tmp1.txt

  with engine.begin() as sql_session:
    stmt = fiscal_log.select().where(fiscal_log.c.id == id)
    result = sql_session.execute(stmt)
    input_file = (result.first())._mapping["input_file"]

    logging.info(f"id: {id} input_file: {input_file}")
    answer_file = input_file.replace(OUT_DIR, ANSWER_DIR)

    count = 0
    while not os.path.exists(answer_file) and count < COUNT_FAIL:
      logging.info(f"answer_file jos nije napravljen {count} {answer_file}")
      time.sleep(1)
      count += 1

    error_line = ""
    status = "OK"
    content = ""
    if count >= COUNT_FAIL:
      status = "FAILED"
    else:  
      with open(answer_file) as af:
        content = ""
        lOk = True
        for line in af:
            #https://docs.python.org/3/library/re.html
            content = content + line
            m = re.match(r"109,1,\d{6},\d+,(\w+);.*", line)
            if lOk and m and m.group(1) == "Ok":
              lOk = True
            else:
              lOk = False
              error_line = line
        if lOk:
          status = "OK"
        else:
          status = "FAILED"

    # ako ima problem u komunikaciji brisi request fajl
    if os.path.isfile(input_file):
      os.remove(input_file)

    with engine.begin() as sql_session:
      query = fiscal_log.update().where(fiscal_log.c.id == id).values(
         output=content, 
         status=status,
         resolved=datetime.datetime.now()
      )
      sql_session.execute(query)
      return  {
        "status": status,
        "err_msg": error_line,
      }

