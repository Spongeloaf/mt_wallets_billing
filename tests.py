import billing_lib
import datetime
import sqlinterface
from typing import List


rtp = billing_lib.RunTimeParams()
rtp.get_bill_date()
sql = sqlinterface.SqlInterface(rtp)
tl = sql.get_tenant_list()
ubl: List[billing_lib.UtilityBill] = []


sql.get_utility_bills(rtp, ubl)
sql.prepare_tennant_bills(ubl, tl)

for t in tl:
    print(vars(t))