from billing_lib import *
import pdfcompositor
import sqlinterface
from typing import List
import time
import mailer


# rtp = RunTimeParams()
# rtp.get_bill_date()
# sql = sqlinterface.SqlInterface(rtp)
# tl = sql.get_active_tenants()
# ubl: List[UtilityBill] = []
# sql.get_utility_bills(ubl)
# sql.insert_utility_bills(ubl)



# init
rtp = RunTimeParams()
sql = sqlinterface.SqlInterface(rtp)
pdf = pdfcompositor.PdfCompositor(rtp)
mail = mailer.Mailer(rtp)
ubl: List[UtilityBill] = []

rtp.get_bill_date()
tl = sql.get_active_tenants()
sql.get_utility_bills(ubl)
sql.check_utility_bill_tenants(ubl, tl)
sql.prepare_tennant_bills(ubl, tl)
time.sleep(0.2)
sql.save_tenant_bills(tl)
print_bills(tl)

pdf.compose_bills(tl)
pdf.docx_to_pdf(tl)
mail.compose_email(tl)
mail.send_email(tl)
pass
