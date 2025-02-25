from dbos import DBOS
import tempfile
from .app import OUT_DIR, ANSWER_DIR, FISKALNI_IOSA, FISKALNI_OPERATER, FISKALNI_OPERATER_PASSWORD, logging, engine
from .schema import fiscal_log, fiscal_plu
from .nuliraj import fprint_nuliraj_racun, fprint_nuliraj_racun_response
import re
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
import sqlalchemy as sa
import datetime
import os, time
from .nuliraj import fprint_nuliraj_racun, fprint_nuliraj_racun_response
from datetime import timedelta

FISKALNI_DELTA_HOURS=DBOS.config["application"]["fiskalni"]["timedelta"]["hours"]
FISKALNI_DELTA_MINUTES=DBOS.config["application"]["fiskalni"]["timedelta"]["minutes"]
FISKALNI_DELTA_DAYS=DBOS.config["application"]["fiskalni"]["timedelta"]["days"]

COUNT_FAIL=60

TEST_RN=[
  {
    "naziv": "ROBA TEST 0.1",
    "cijena": 0.15,
    "popust": 30.00,
    "kolicina": 3.000,
    "pdv": "PDV17",
    "nacin_placanja": "0" # keš
  }
]


#  nacin placanja
#    value '0' means payment in cash;
#    value '1' means payment via card;
#    value '2' means payment via cheque;
#    value '3' means payment type "Virman";

def get_fprint_payment_type(paymentType: str):
   #{ "Cash", "Card", "WireTransfer", "Other" }

   if paymentType == "Cash":
       return "0"
   elif paymentType == "WireTransfer":
       return "3"
   elif paymentType == "Card":
       return "1"
   else:
       return "3" # other = WireTranfer
   
def get_fprint_fiskalni_tarifa( id_tarifa: str, pdv_obveznik: bool = True):
  
    if id_tarifa in ("PDV17", "PDV1", "PDV7", "E") and pdv_obveznik:
      return "2"
    elif id_tarifa in ("PDV0", "K") and pdv_obveznik:
      return "4"
    #elif id_tarifa == "PDVM":
    #  return "5"
    elif not pdv_obveznik:
      # A 
      return "1"
 


def next_plu():
  with engine.begin() as sql_session:
      # https://www.atlassian.com/data/notebook/how-to-execute-raw-sql-in-sqlalchemy
      stmt = text("select max(id) from fiscal_plu")
      result = sql_session.execute(stmt)
      max_id = (result.first())[0]
      if max_id is None:
        max_id = 9
      return max_id + 1
  
  
def get_plu(naziv: str, cijena: sa.Numeric, pdv: str):

    with engine.begin() as sql_session:
      stmt = fiscal_plu.select().where(fiscal_plu.c.naziv == naziv)
      stmt = stmt.where(fiscal_plu.c.cijena == cijena)
      stmt = stmt.where(fiscal_plu.c.tarifa == pdv)
      result = sql_session.execute(stmt)
      results = result.all()

      if result is None or len(results)==0:
        plu_id = next_plu()
        query = fiscal_plu.insert().values(id=plu_id, naziv=naziv, cijena=cijena, tarifa=pdv)
        sql_session.execute(query)
      else:  
        plu_id = results[0]._mapping["id"]
     
      return plu_id
    
    return None

def find_fiscal_number_by_broj_rn(broj_rn: str):

  with engine.begin() as sql_session:
      stmt = fiscal_log.select().where(fiscal_log.c.input_number == broj_rn.strip())
      # samo racuni koji su uspjesno obradjeni su fiskalizirani
      stmt = stmt.where(fiscal_log.c.status == 'OK')
      result = sql_session.execute(stmt)
      results = result.all()
      if result is None or len(results)==0:
        return None
      else:
        return results[0]._mapping["fiscal_number"]

def find_time_by_fiscal_number(broj_fiskalni: str):

  with engine.begin() as sql_session:
      stmt = fiscal_log.select().where(fiscal_log.c.fiscal_number == broj_fiskalni.strip())
      # samo racuni koji su uspjesno obradjeni su fiskalizirani
      stmt = stmt.where(fiscal_log.c.status == 'OK')
      result = sql_session.execute(stmt)
      results = result.all()
      if result is None or len(results)==0:
        return None
      else:
        # fiskalni vrijeme odstupa od tacnog vremena 
        return results[0]._mapping["created"] + timedelta(
            hours=FISKALNI_DELTA_HOURS, 
            minutes=FISKALNI_DELTA_MINUTES,
            days=FISKALNI_DELTA_DAYS)

def fprint_kupac(kupac):

    s_naziv = kupac["naziv"]
    s_naziv = s_naziv[:36]

    s_adresa = kupac["adresa"]
    s_adresa = s_adresa[:36]
    
    s_grad = kupac["ptt"] + " " + kupac["grad"]
    s_grad = s_grad[:36]

    content = f"55,1,______,_,__;{kupac["id_broj"]};{s_naziv};{s_adresa};{s_grad};"

    return content


@DBOS.step()
def fprint_racun(racun_stavke=TEST_RN, kupac=None, broj_rn="00001/25", stornirati: str = None):
  
  content = ""
  for stavka in racun_stavke:
    plu_id = get_plu(stavka["naziv"], stavka["cijena"], stavka["pdv"])
    pdv = get_fprint_fiskalni_tarifa(stavka["pdv"])
    s_cijena = "{:10.2f}".format(stavka["cijena"]).strip()
    s_naziv = stavka["naziv"].strip()
    s_naziv = s_naziv[:32]  # max 32 znaka
    # 107,1,______,_,__;2;2;12;1.00;ROBA TEST 01;      << 2-dodaj, poreznastopa=2, PLU=12; cijena=1, naziv=ROBA TEST 01                                           
    content = content + f"107,1,______,_,__;2;{pdv};{plu_id};{s_cijena};{s_naziv};" + os.linesep
    # 107,1,______,_,__;4;12;1.00;                     << 4-promjena cijene=setovanje cijena, 12; 1.00 
    content = content + f"107,1,______,_,__;4;{plu_id};{s_cijena};" + os.linesep

  # 48,1,______,_,__;1234567890123456;1;000000;;
  s_storno = ""
  if stornirati:
    stornirati = stornirati.strip()
    s_storno = f"{stornirati};"
  content = content + f"48,1,______,_,__;{FISKALNI_IOSA};{FISKALNI_OPERATER};{FISKALNI_OPERATER_PASSWORD};;{s_storno}" + os.linesep

  ukupno_racun = 0
  s_nacin_placanja = "0"
  for stavka in racun_stavke:
    s_nacin_placanja = stavka["nacin_placanja"]
    plu_id = get_plu(stavka["naziv"], stavka["cijena"], stavka["pdv"])
    s_kolicina = "{:10.3f}".format(stavka["kolicina"]).strip()
    s_procenat = "{:10.3f}".format(stavka["popust"]).strip()
    ukupno_racun = ukupno_racun + round(stavka["kolicina"]*stavka["cijena"]*(1 - stavka["popust"]/100.00), 2)
    if stavka["popust"] > 0:
      s_procenat = "-" + s_procenat
    # 52,1,______,_,__;12;2.000;-8.00;   <<stavka,  12 = plu, 2 = kolicina na 3 decimale, popust sa "-" predznakom                                                               
    content = content + f"52,1,______,_,__;{plu_id};{s_kolicina};{s_procenat};" + os.linesep

  ukupno_racun = round(ukupno_racun, 2)
  s_ukupno_racun = "{:10.2f}".format(ukupno_racun).strip()
  # 51,1,______,_,__;   
  content = content + "51,1,______,_,__;" + os.linesep                                                                            
  # 53,1,______,_,__;0;1.84;  <<<  ukupno racun 0 - cash
  #   53,1,009120,6,0;0;31.16;
  #
  #   ''53'' – payment
  #   53,1,______,_,__;[flag];[amount];
  #    ➢ [flag] – parameter that determines the type of the payment:
  #    value '0' means payment in cash;
  #    value '1' means payment via card;
  #    value '2' means payment via cheque;
  #    value '3' means payment type "Virman";
  #    ➢ [amount] – the sum of the payment
  #    The parameters [flag] and [amount] are optional and if you skip them, the command will execute
  #    payment in cash with the whole sum of the current receipt.
  #    The command cannot be executed if :
  #    – there is no opened receipt
  #    – the accumulated sum is negative
  #    – the sum for a tax group is negative
  #
  content = content + f"53,1,______,_,__;{s_nacin_placanja};{s_ukupno_racun};" + os.linesep

  if kupac:
    content = content + fprint_kupac(kupac) + os.linesep

  # 106,1,______,_,__;
  content = content + "106,1,______,_,__;" + os.linesep
  # 56,1,______,_,__;
  content = content + "56,1,______,_,__;" + os.linesep

  file_name = ""
  with tempfile.NamedTemporaryFile(dir=OUT_DIR, suffix=".txt", delete=False) as f:
    file_name = f.name
    logging.info(f"file: {file_name}")
  
    # https://docs.python.org/3.12/library/codecs.html#standard-encodings
    f.write(content.encode(encoding='cp1250'))
    f.flush()

    with engine.begin() as sql_session:
      query = fiscal_log.insert().values(
        input=content, 
        input_file=file_name, 
        type='FISCAL', 
        input_number=broj_rn,
        fiscal_number_2=stornirati, # ako je storno racun ovdje se upisuje broj racuna koji se stornira; u suprotnom null
      )
      sql_session.execute(query)
     
      stmt = fiscal_log.select().where(fiscal_log.c.input_file == file_name)
      stmt = stmt.where(sa.cast(fiscal_log.c.created, sa.Date) == datetime.date.today())
      stmt = stmt.where(fiscal_log.c.input_number == broj_rn)
      result = sql_session.execute(stmt)

      return (result.first())._mapping["id"]



# == response fiskalni racun (6367) ===========
# C:\fiscal\answer>type tmp1y8fj4s6.txt
# 107,1,000200,1,Ok;2;2;10;0.10;ROBA TEST 0.1;
# 107,1,000200,2,Ok;4;10;0.10;
# 48,1,000200,3,Ok;0000,6366,0131;
# 52,1,000200,4,Ok;10;2.000;-8.000;
# 51,1,000200,5,Ok;
# 53,1,000200,6,Ok;0;0.18;
# 106,1,000200,7,Ok;
# 56,1,000200,8,Ok;0001,6367,0131;

# == response storno fiskalni racun (orig racun 6367, RF: 132) =================
# C:\fiscal\answer>type tmpgpdms55m.txt
# 107,1,000200,1,Ok;2;2;10;0.10;ROBA TEST 0.1;
# 107,1,000200,2,Ok;4;10;0.10;
# 48,1,000200,3,Ok;0001,6367,0131;
# 52,1,000200,4,Ok;10;2.000;-8.000;
# 51,1,000200,5,Ok;
# 53,1,000200,6,Ok;0;0.18;
# 106,1,000200,7,Ok;
# 56,1,000200,8,Ok;0002,6367,0132; <<< reklamirani fisk racun 0132

#  neki error 48
#107,1,000200,1,Ok;2;2;51;0.06;Stavke po RN INV/2025/00059/T;
#107,1,000200,2,Ok;4;51;0.06;
#48,1,000200,3,Er;;


@DBOS.step()
def fprint_racun_response(id: UUID):
  

  with engine.begin() as sql_session:
    stmt = fiscal_log.select().where(fiscal_log.c.id == id)
    result = sql_session.execute(stmt)
    res = (result.first())._mapping
    input_file = res["input_file"]
    fiscal_number_2 = res["fiscal_number_2"]

    logging.info(f"id: {id} input_file: {input_file}")
    answer_file = input_file.replace(OUT_DIR, ANSWER_DIR)

    count = 0
    while not os.path.exists(answer_file) and count < COUNT_FAIL:
      logging.info(f"answer_file jos nije napravljen {count} {answer_file}")
      time.sleep(1)
      count += 1

    fiscal_number=""
    content = ""
    status = "OK"
    error_line = ""
    if count >= COUNT_FAIL:
      status = "FAILED"
    else:  
      with open(answer_file) as af:
        content = ""
        lOk = True
        for line in af:
            #https://docs.python.org/3/library/re.html
            content = content + line
            m = re.match(r"\d+,1,\d{6},\d+,(\w+);.*", line)
            if lOk and m and m.group(1) == "Ok":
              lOk = True
            else:
              lOk = False
              error_line = line
            # 56,1,000200,8,Ok;0001,6367,0131; <<< 6367 je fisk racun, 0131 je zadnji reklamirani fisk racun
            m = re.match(r"56,1,\d{6},\d+,Ok;\d+,(\d+),(\d+);", line)
            if m:
              if fiscal_number_2:
                # ako postoji fiscal_number_2, radi se o stornu
                fiscal_number=m.group(2)
              else:
                fiscal_number=m.group(1)
            
        if lOk:
          status = "OK"
        else:
          status = "FAILED"

    if os.path.isfile(input_file):
      os.remove(input_file)



    with engine.begin() as sql_session:
      query = fiscal_log.update().where(fiscal_log.c.id == id).values(
        output=content, 
        status=status,
        resolved=datetime.datetime.now(),
        fiscal_number=fiscal_number
      )
      sql_session.execute(query)

      # nije mogao zavrsiti racun na liniji 53 na kojoj se navodi uplata novca
      if status == "FAILED" and error_line[:2] == "53":
        print("neuspjesno: mora se nulirati racun")
        idn = fprint_nuliraj_racun()
        resp = fprint_nuliraj_racun_response(idn)
        if resp["status"] == "OK":
          error_line += " / račun NULIRAN!"
        print(resp)

      return  {
        "status": status,
        "err_msg": error_line,
        "fiscal_number": fiscal_number
      }



#2 KOM "ROBA TEST 01", CIJENA 1.00, POPUST 8%

# 107,1,______,_,__;2;2;12;1.00;ROBA TEST 01;      << 2-dodaj, poreznastopa=2, PLU=12; cijena=1, naziv=ROBA TEST 01                                           
# 107,1,______,_,__;4;12;1.00;                     << 4-promjena cijene=setovanje cijena, 12; 1.00                                                    
# 48,1,______,_,__;1234567890123456;1;000000;;
#                                                       
# 52,1,______,_,__;12;2.000;-8.00;   <<stavka,  12 = plu, 2 = kolicina na 3 decimale, popust sa "-" predznakom                                                               
#
# 51,1,______,_,__;                                                                                   
# 53,1,______,_,__;0;1.84;  <<<  ukupno racun 1.84 KM, 0 - kesh placanje                                                                     
# 106,1,______,_,__;                                                                                  
# 56,1,______,_,__;  


