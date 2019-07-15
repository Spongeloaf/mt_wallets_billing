from billing_lib import *
import pdf_compositor
import sql_interface
from typing import List
import time
import bill_mailer


# rtp = RunTimeParams()
# rtp.input_bill_date()
# sql = sqlinterface.SqlInterface(rtp)
# tl = sql.get_active_tenants()
# ubl: List[UtilityBill] = []
# sql.get_utility_bills(ubl)
# sql.insert_utility_bills(ubl)



# init
rtp = RunTimeParams()
sql = sql_interface.SqlInterface(rtp)
pdf = pdf_compositor.PdfCompositor(rtp)
mail = bill_mailer.Mailer(rtp)
ubl: List[UtilityBill] = []

rtp.input_bill_date()
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
