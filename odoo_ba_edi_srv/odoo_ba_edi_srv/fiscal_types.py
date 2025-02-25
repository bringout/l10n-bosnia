from pydantic import BaseModel
from typing import List


class TaxRate(BaseModel):
    label: str
    rate: int

class TaxCategory(BaseModel):
    categoryType: int
    name: str
    orderId: int
    taxRates: list[TaxRate] = []
     

class TaxRates(BaseModel):
   groupId: str
   taxCategories: list[TaxCategory] = []
   validFrom: str
    
class Status(BaseModel):
   allTaxRates:  list[TaxRates] = [] 
   currentTaxRates: list[TaxRates] = []
   deviceSerialNumber: str
   gsc: list[str] = []
   hardwareVersion: str
   lastInvoiceNumber: str
   make: str 
   model: str
   mssc:  list[str] = []
   protocolVersion: str
   sdcDateTime: str
   softwareVersion: str
   supportedLanguages: list[str] = []


class PaymentLine(BaseModel):
    amount: float
    paymentType: str


class ItemLine(BaseModel):
    name: str
    labels: list[str] = []
    totalAmount: float | None = None
    unitPrice: float | None = None
    baseAmount: float | None = None
    taxAmount: float | None = None
    quantity: float
    discount: float | None = None
    discountAmount: float | None = None


#   invoiceType:
#   1. Normal
#   2. Copy

class CustomerData(BaseModel):
    idBroj: str
    naziv: str
    adresa: str
    grad: str
    ptt: str

#   Ako je copy, salje:
#   1. referentDocumentNumber
#   2. referentDocumentDT 
class InvoiceRequest(BaseModel):
    referentDocumentNumber: str | None = None
    referentDocumentDT: str | None = None
    erpDocument: str | None = None
    invoiceType: str
    transactionType: str
    payment: list[PaymentLine] = []
    items: list[ItemLine] = []
    cashier: str | None = None
    customer: CustomerData | None = None 

class InvoiceData(BaseModel):
    invoiceRequest: InvoiceRequest

class TaxItems(BaseModel):
    amount: float
    categoryName: str
    categoryType: int = 0
    label: str = "E"
    rate: int = 17
    
class InvoiceResponse(BaseModel):
    address: str
    businessName: str
    district: str
    encryptedInternalData: str
    invoiceCounter: str
    invoiceCounterExtension: str
    invoiceImageHtml: str | None = None
    invoiceImagePdfBase64: str | None = None
    invoiceImagePngBase64: str | None = None
    invoiceNumber: str
    journal: str
    locationName: str
    messages: str
    mrc: str
    requestedBy: str
    sdcDateTime: str
    signature: str
    signedBy: str
    taxGroupRevision: int
    taxItems: list[TaxItems] = []    
    tin: str
    totalAmount: float
    totalCounter: int
    transactionTypeCounter: int
    verificationQRCode: str 
    verificationUrl: str 

class PingData(BaseModel):
    msg: str  