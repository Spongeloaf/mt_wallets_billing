import billing_lib
import datetime
import sqlinterface

rtp = billing_lib.RunTimeProperties()
tl = billing_lib.TenantList()
sql = sqlinterface.SqlInterface(rtp)

sql.get_tenant_info(tl)
sql.print_debug()
