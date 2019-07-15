# imports and init
import billing_lib as blib
import sql_interface
import pdf_compositor
import bill_mailer
import menus
from typing import List

# init
rtp = blib.RunTimeParams()
sql = sql_interface.SqlInterface(rtp)
pdf = pdf_compositor.PdfCompositor(rtp)
mail = bill_mailer.Mailer(rtp)
ubl: List[blib.UtilityBill] = []
tl: List[blib.Tenant] = []
main = menus.MenuStructure(rtp, sql, pdf, mail, tl, ubl)

# run
main()
