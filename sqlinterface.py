from billing_lib import TenantList, Tenant, RunTimeProperties
import sqlite3


class SqlInterface:
    def __init__(self, rtp: RunTimeProperties):
        """ Setup SQL, check DB, create cursor. """
        self.sql_conn = sqlite3.connect(rtp.sql_fname)
        self.sql_curr = self.sql_conn.cursor()

    def get_tenant_info(self, tl: TenantList):
        """ retrieve list of active tenants for month specified """
        self.sql_curr.execute("SELECT * FROM tenants WHERE is_current IS 1")

    def get_bill(self, tenant: Tenant):
        """ Pass tenant list to SQL, return bills for month specified """
        pass

    def print_debug(self):
        print(self.sql_curr.fetchall())