from dbos import DBOS

from .app import app, logging
from .steps import sign_guestbook, insert_greeting
from .non_fiscal_text import fprint_non_fiscal, fprint_non_fiscal_response
from .dnevni_izvjestaj import fprint_dnevni_izvjestaj, fprint_dnevni_izvjestaj_response
from .duplikat import fprint_duplikat, fprint_duplikat_response
from .periodicni_izvjestaj import fprint_periodicni_izvjestaj, fprint_periodicni_izvjestaj_response
from .racun import fprint_racun, fprint_racun_response, find_fiscal_number_by_broj_rn, get_fprint_payment_type, find_time_by_fiscal_number
#from .nasilno_zatvori_racun import fprint_nasilno_zatvori_racun, fprint_nasilno_zatvori_racun_response
from .nuliraj import fprint_nuliraj_racun, fprint_nuliraj_racun_response
from .polog import fprint_polog, fprint_polog_response
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta

#@app.get("/greeting/{name}", )

from fastapi import HTTPException, status, Request
from .fiscal_types import InvoiceData, InvoiceResponse, TaxItems, PingData


BUSINESS_NAME = "bring.out doo Sarajevo"
BUSINESS_ADDRESS = "Juraja Najtharta 3"

FISKALNI_SERIAL = DBOS.config["application"]["fiskalni"]["serial"]

#@app.post("/ping")
#def ping(ping_data: PingData):
#    print ("msg: ", ping_data.msg)

APP_PIN = DBOS.config["application"]["pin"]
API_KEY = DBOS.config["application"]["api_key"]

@app.get("/{pin}/ping")
@DBOS.workflow()
def ping(pin: str):
    if pin != APP_PIN:
        return RedirectResponse('https://www.bring-out-ba.uk')
    return { "msg": "pong" }

def check_api_key(req: Request):

    token = req.headers["Authorization"].replace("Bearer ", "").strip()

    if token != API_KEY:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, detail = "Unauthorized API-KEY %s" % (token)
        )
        return False

    return True

@app.post("/api/invoices")
@DBOS.workflow()
def invoices(req: Request, invoice_data: InvoiceData):

    if not check_api_key(req):
        return {

            "status": "FAILED",
            "message": "API KEY ERROR"
        }
    
    
    # https://github.com/fastapi/fastapi/discussions/9601

    # Normal, Copy
    type = invoice_data.invoiceRequest.invoiceType

    cashier = invoice_data.invoiceRequest.cashier

    #items_length = len(invoice_data.invoiceRequest.items)
    referentDocumentNumber = invoice_data.invoiceRequest.referentDocumentNumber
    referentDocumentDT = invoice_data.invoiceRequest.referentDocumentDT

    
    # Sale, Refund
    transactionType = invoice_data.invoiceRequest.transactionType

    erpDocument = invoice_data.invoiceRequest.erpDocument

    print()
    print("========== invoice request ===========")
    print("cahiser:", cashier)
    print("invoice request type:", type)
    print("transaction type:", transactionType)
    print("erpDocument", erpDocument)

    paymentType = "Cash"
    paymentAmount = 0
    for payment in invoice_data.invoiceRequest.payment:
        if payment.amount > paymentAmount:
            # najveci iznos odredjuje vrstu placanja, ako je proslijedjeno vise
            paymentAmount = payment.amount
            paymentType =  payment.paymentType
        print("paymentType:", payment.paymentType, " ; paymentAmount:", payment.amount )
    
    if type == "Copy":
        if (not referentDocumentNumber) or (not referentDocumentDT):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST, detail = "Copy ne sadrzi referentDocumentNumber and DT"
            )  
        else:
            print("referentni fiskalni dokument:", referentDocumentNumber, referentDocumentDT )  
         
    if transactionType == "Refund":
        print("refund referentni fiskalni dokument broj:", referentDocumentNumber, "datum:", referentDocumentDT )  
         
    totalValue = 0
    cStavke = ""
    fprint_stavke = []
    for item in invoice_data.invoiceRequest.items:
        totalValue += item.totalAmount
        nDiscount = item.discount or 0.0
        nDiscountAmount = item.discountAmount or 0.00
        label = item.labels[0]
        cStavka = "%s quantity: %.2f unitPrice: %.2f discount: %.2f discountAmount: %.2f  totalAmount: %.2f label: %s\r\n" % (item.name, item.quantity, item.unitPrice, nDiscount, nDiscountAmount, item.totalAmount, label)
        cStavke += cStavka
        print(cStavka)
        fprint_stavka = {
            "naziv": item.name,
            "cijena": item.unitPrice,
            "popust": item.discount,
            "kolicina": item.quantity,
            "pdv": label, # PDV stopa E, K, A
            "nacin_placanja": get_fprint_payment_type(paymentType)
        }
        fprint_stavke.append(fprint_stavka)


    print("totalValue:", totalValue)

    #payments_length = len(invoice_data.invoiceRequest.payment)

    #cInvoiceNumber = str(randint(1,999)).zfill(3)

    #cFullInvoiceNumber = "AX4F7Y5L-BX4F7Y5L-" + cInvoiceNumber

    cDTNow = datetime.now().isoformat()
    #>>> '2024-08-01T14:38:32.499588'

    print("fprint_stavke", fprint_stavke)
    #return { "invoiceNumber": "12345" }

    customer = None
    if invoice_data.invoiceRequest.customer:
        print("customer", invoice_data.invoiceRequest.customer.idBroj, invoice_data.invoiceRequest.customer.naziv)
        customer = {
            "id_broj": invoice_data.invoiceRequest.customer.idBroj,
            "naziv": invoice_data.invoiceRequest.customer.naziv,
            "adresa": invoice_data.invoiceRequest.customer.adresa,
            "ptt": invoice_data.invoiceRequest.customer.ptt,
            "grad": invoice_data.invoiceRequest.customer.grad
        }

    stornirati = None
    if transactionType=="Refund":
        stornirati = referentDocumentNumber

    id = fprint_racun(racun_stavke = fprint_stavke, kupac=customer, broj_rn=erpDocument, stornirati=stornirati)
    fprint_resp = fprint_racun_response(id)


    #if check_api_key(req):
    if fprint_resp["status"] == "OK":

        response = InvoiceResponse(
            address = BUSINESS_ADDRESS,
            businessName = BUSINESS_NAME,
            district = "SA",
            encryptedInternalData = "000",
            invoiceCounter = "DUMMYCOUNTER", 
            invoiceCounterExtension = "SA",
            invoiceImageHtml = None,
            invoiceImagePdfBase64 = None,
            invoiceImagePngBase64 = None,
            invoiceNumber = fprint_resp["fiscal_number"], # jedini bitan podatak 
            journal = "\r\n POČETAK   \r\n" +
                       "\r\n======== KRAJ =======\r\n",
            locationName = "bring.out doo Sarajevo",
            messages = "Uspješno",
            mrc = "01-0001-WPYB002248000772",
            requestedBy = "HERNAD",
            sdcDateTime = cDTNow,  #"2024-09-15T07:47:09.548+01:00",
            signature = "SGN",
            signedBy = "HERNAD",
            taxGroupRevision = 2,
            taxItems = [ TaxItems(amount=0, categoryName="ECAL", categoryType = 0, label = "E", rate = 17) ],
            tin = "9999999999999999",
            totalAmount = totalValue,
            totalCounter = 1,
            transactionTypeCounter = 1,
            verificationQRCode = "DUMMY",
            verificationUrl = "https://www.bring.out.ba"
        )

        return response
    else:
        return {
            "status": "FAILED",
            "message": "ERROR: " + fprint_resp["err_msg"]
        }
 


#@app.get("/greeting/{name}")
#@DBOS.workflow()
#@DBOS.required_roles(["default-roles-bringout"])
#def greeting_endpoint(name: str):
#    print("start greeting", name)
#    sign_guestbook(name)
#    for _ in range(5):
#        logging.info("Press Control + C to stop the app...")
#        DBOS.sleep(1)
#    insert_greeting(name)
#    return f"Thank you for being awesome, {name}!"


@app.get("/{pin}/non_fiscal_text/{txt}")
@DBOS.workflow()
#@DBOS.required_roles(["default-roles-bringout"])
def non_fiscal(pin: str, txt: str):
    if pin != APP_PIN:
        return RedirectResponse('https://www.bring-out-ba.uk')
    id = fprint_non_fiscal(txt)
    resp = fprint_non_fiscal_response(id)
    
    return resp


@app.get("/{pin}/dnevni_izvjestaj")
@DBOS.workflow()
def dnevni_izvjestaj(pin: str):
    if pin != APP_PIN:
        return RedirectResponse('https://www.bring-out-ba.uk')
    id = fprint_dnevni_izvjestaj()
    resp = fprint_dnevni_izvjestaj_response(id)
    return resp

@app.get("/{pin}/periodicni_izvjestaj/{od}/{do}")
@DBOS.workflow()
def periodicni_izvjestaj(pin: str, od: str, do: str):
    if pin != APP_PIN:
        return RedirectResponse('https://www.bring-out-ba.uk')
    d_od = datetime.strptime(od, '%d.%m.%y')
    d_do = datetime.strptime(do, '%d.%m.%y')
    id = fprint_periodicni_izvjestaj(d_od, d_do)
    resp = fprint_periodicni_izvjestaj_response(id)
    return resp

@app.get("/{pin}/duplikat/{tip}/{dat}/{h_od}/{h_do}")
@DBOS.workflow()
def duplikat(pin: str, tip: str, dat: str, h_od: str, h_do: str):
    if pin != APP_PIN:
        return RedirectResponse('https://www.bring-out-ba.uk')
    dt_od = datetime.strptime(f"{dat} {h_od}", '%d.%m.%y %H:%M')
    dt_do = datetime.strptime(f"{dat} {h_do}", '%d.%m.%y %H:%M')
    id = fprint_duplikat(tip, dt_od, dt_do)
    resp = fprint_duplikat_response(id)
    return resp


@app.get("/{pin}/duplikat/{tip}/{broj}")
@DBOS.workflow()
def duplikat_broj(pin: str, tip: str, broj: str):
    if pin != APP_PIN:
        return RedirectResponse('https://www.bring-out-ba.uk')
    
    fisk_date_time_rn_created = find_time_by_fiscal_number(broj)
    print(f"fiskalni rn {broj} kreiran po satu fiskalnog uredjaja {fisk_date_time_rn_created}")

    dat = fisk_date_time_rn_created.date().strftime("%d.%m.%y")
    h_od = (fisk_date_time_rn_created + timedelta(minutes=-1)).strftime("%H:%M")
    h_do = (fisk_date_time_rn_created + timedelta(minutes=+2)).strftime("%H:%M")

    dt_od = datetime.strptime(f"{dat} {h_od}", '%d.%m.%y %H:%M')
    dt_do = datetime.strptime(f"{dat} {h_do}", '%d.%m.%y %H:%M')
    
    id = fprint_duplikat(tip, dt_od, dt_do)
    resp = fprint_duplikat_response(id)
    
    return resp

#@app.get("/nasilno_zatvori_racun")
#@DBOS.workflow()
#def nasilno_zatvori_racun():
#    id = fprint_nasilno_zatvori_racun()
#    fprint_nasilno_zatvori_racun_response(id)
#    
#    return f"nasilno zatvaranje izvrseno!"

@app.get("/{pin}/nuliraj_racun")
@DBOS.workflow()
def nuliraj_racun(pin: str):
    if pin != APP_PIN:
        return RedirectResponse('https://www.bring-out-ba.uk')
    id = fprint_nuliraj_racun()
    resp = fprint_nuliraj_racun_response(id)
    print(resp)
    return resp

@app.get("/{pin}/polog/{iznos}")
@DBOS.workflow()
def polog(pin: str, iznos: float = 100):
    id = fprint_polog(iznos)
    resp = fprint_polog_response(id)
    print(resp)
    return resp

#@app.get("/test_rn")
#@DBOS.workflow()
#def test_rn():
#    id = fprint_racun(broj_rn="00002/T", stornirati=None)
#    fprint_racun_response(id)
#    
#    return f"racun 00001/T napravljen!"


#@app.get("/test_rn_storno")
#@DBOS.workflow()
#def test_rn_storno():
#    stornirati=find_fiscal_number_by_broj_rn("00002/T")
#    if stornirati:
#        id = fprint_racun(broj_rn="00002/T/S", stornirati=stornirati)
#        fprint_racun_response(id)
#        return f"storno racun 00002/T/S napravljen!"
#    else:
#        return "broj_rn 00002/T ne postoji?!"