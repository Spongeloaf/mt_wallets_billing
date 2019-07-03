from billing_lib import Tenant, RunTimeParams, UtilityBill
import sqlite3
from typing import List


class SqlInterface:

    def __init__(self, rtp: RunTimeParams):
        """ Setup SQL, check DB, create cursor. """
        self.logger = rtp.logger
        self.sql_conn = sqlite3.connect(rtp.sql_fname)
        self.sql_curr = self.sql_conn.cursor()

    def get_tenant_list(self):
        """ retrieve list of active tenants """
        self.sql_curr.execute("SELECT * FROM tenants WHERE is_current IS 1")
        tl = []
        for row in self.sql_curr:
            tenant = Tenant()
            tenant.id = row[0]
            tenant.name = row[1]
            tenant.email = row[2]
            tenant.charge_room = row[4]
            tl.append(tenant)
        return tl

    def get_utility_bills(self, rtp: RunTimeParams, ubl: List[UtilityBill]):
        """ return bills for month specified """
        self.sql_curr.execute("SELECT * from utility_bills WHERE (year IS ?) and (month is ?)", [rtp.year, rtp.month])
        for row in self.sql_curr:
            label = row[0]
            amount = row[1]

            tenants = []
            tenants_str: str = row[4]
            tenants_split = tenants_str.split(',')
            for t in tenants_split:
                t = int(t)
                tenants.append(t)

            ub = UtilityBill(label, amount, tenants)
            ubl.append(ub)

    def prepare_tennant_bills(self, ubl: List[UtilityBill], tl: List[Tenant]):
        for tenant in tl:
            for bill in ubl:
                for i in bill.tenants:
                    if tenant.id == i:
                        self.add_bill(bill, tenant)
            tenant.update_total()

    def add_bill(self, bill: UtilityBill, tenant: Tenant):
        count = len(bill.tenants)
        if bill.label == "electricity":
            tenant.charge_electricity = round((bill.amount / count), 2)
            return

        if bill.label == "gas":
            tenant.charge_gas = round((bill.amount / count), 2)
            return

        if bill.label == "internet":
            tenant.charge_internet = round((bill.amount / count), 2)
            return
        self.logger.critical("Bad bill label in sqlinterface.add_bill(): {}".format(vars(bill)))

    def print_cursor(self):
        for row in self.sql_curr:
            print(row)
