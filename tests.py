from billing_lib import *
import pdf_compositor
import sql_interface
from typing import List
import time
import bill_mailer
import menus


#rtp = RunTimeParams()
# sql = sql_interface.SqlInterface(rtp)
# rtp.billing_date_user_input()
# sql.get_tenants_by_date()
# sql.get_utility_bills()
# sql.prepare_tennant_bills()
# rtp.print_tenant_bills()
# pass

menu = menus.Menu
f = menu.get_float()
print(f)
