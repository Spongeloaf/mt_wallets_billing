from billing_lib import *
import pdfcompositor
import sqlinterface
from typing import List
import time


rtp = RunTimeParams()
rtp.get_bill_date()
sql = sqlinterface.SqlInterface(rtp)
tl = sql.get_active_tenants()
ubl: List[UtilityBill] = []
pdf = pdfcompositor.PdfCompositor(rtp)

sql.get_utility_bills(ubl)
sql.check_utility_bill_tenants(ubl, tl)
sql.prepare_tennant_bills(ubl, tl)
time.sleep(0.2)
print_bills(tl)
sql.create_tenant_bills(tl)
pdf.compose_bills(tl)
pdf.docx_to_pdf(tl)
pass
