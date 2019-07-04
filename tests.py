import billing_lib as bl
import datetime
import sqlinterface
from typing import List
import time


rtp = bl.RunTimeParams()
rtp.get_bill_date()
sql = sqlinterface.SqlInterface(rtp)
tl = sql.get_active_tenants()
ubl: List[bl.UtilityBill] = []


sql.get_utility_bills(ubl)
sql.check_utility_bill_tenants(ubl, tl)
sql.prepare_tennant_bills(ubl, tl)
time.sleep(0.2)
bl.print_bills(tl)
sql.create_tenant_bills(tl)
pass
