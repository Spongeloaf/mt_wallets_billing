from billing_lib import *
import pdf_compositor
import sql_interface
from typing import List
import time
import bill_mailer

rtp = RunTimeParams()
sql = sql_interface.SqlInterface(rtp)
rtp.billing_date_use_current()
sql.get_tenants_by_date()

pass
