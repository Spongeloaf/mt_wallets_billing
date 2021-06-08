from src.billing_lib import *
import sqlite3
from typing import List


class SqlInterface:

    def __init__(self, rtp: RunTimeParams):
        """ Setup SQL, check DB, create cursor. """
        self.rtp = rtp
        self.logger_fname = rtp.google_path + 'sql_log.txt'
        self.logger = create_logger(self.logger_fname, self.rtp.sql_log_level, "sql_log")
        self.sql_conn = sqlite3.connect(self.rtp.sql_db_fname)
        self.sql_curr = self.sql_conn.cursor()

    # Main functions - you need most of these to execute a full billing cycle
    def get_tenants_by_date(self):
        """ retrieve list of tenants for a specific date/year """
        self.sql_curr.execute("SELECT * FROM tenants WHERE ((? < year_out) or ((? == year_out) AND (? <= month_out))) AND ? >= year_in",
                              [self.rtp.year, self.rtp.year, self.rtp.month_int, self.rtp.year])
        self.__sql_tenants_to_list()
        if len(self.rtp.tenantList) == 0:
            self.rtp.print_error("No tenants found for query!")

    def get_recurring_bills(self):
        """
        retrieve bills for tenants that represent fixed monthly charges
        row[0] = label
        row[1] = amount
        row[2] = tenant
        row[3] = memo
        """
        self.sql_curr.execute("SELECT * FROM recurring_charges")
        self.rtp.recurringChargeList = []
        for row in self.sql_curr:
            recurring = RecurringCharges(row[0], row[1], int(row[2]), row[3])
            self.rtp.recurringChargeList.append(recurring)

    def get_tenants_by_active(self):
        """ retrieve list of active tenants """
        self.sql_curr.execute("SELECT * FROM tenants WHERE is_current IS 1")
        self.__sql_tenants_to_list()
        if len(self.rtp.tenantList) == 0:
            self.rtp.print_error("No tenants found for query!")

    def get_utility_bills(self):
        """ return bills for month specified """
        self.rtp.utilityBillList.clear()
        self.sql_curr.execute("SELECT * from utility_bills WHERE (year IS ?) and (month is ?)", [self.rtp.year, self.rtp.month_int])
        for row in self.sql_curr:
            label = row[0]
            amount = row[1]
            month = row[2]
            year = row[3]
            memo = row[5]
            if memo is None:
                memo = ''
            tenants = []
            tenants_str: str = row[4]
            tenants_split = tenants_str.split(',')
            for t in tenants_split:
                try:
                    t = int(t)
                    tenants.append(t)
                except ValueError:
                    self.logger.critical("Value error in get_utility_bills, bad tenant_id string: {}".format(tenants_str))
                    self.rtp.critical_stop("Stopped by sql.get_utility_bills() for ValueError")

            ub = UtilityBill(label, amount, tenants, month, year, memo)
            self.rtp.utilityBillList.append(ub)
            self.logger.info("Utility Bill found: {} for {} split between tenants: {}".format(label, amount, tenants_str))

    def check_utility_bill_tenants(self):
        id_list = []
        for t in self.rtp.tenantList:
            id_list.append(t.id)

        for bill in self.rtp.utilityBillList:
            for tenant in bill.tenants:
                if tenant not in id_list:
                    self.logger.critical("A bill is targeted for a non-active tenant_id in check_utility_bill_tenants: {}".format(tenant))
                    self.rtp.critical_stop("Stopped by sql.check_utility_bill_tenants for invalid tenant_id string")

    def prepare_tennant_bills(self):
        """ Create tenant bills """
        for tenant in self.rtp.tenantList:
            tb = TenantBill()
            tb.tenant_id = tenant.id
            tb.tenant_name = tenant.name
            tb.email_addr = tenant.email_addr
            tb.month = self.rtp.month_int
            tb.year = self.rtp.year
            tb.charge_room = tenant.room_rate
            tb.memo_recurring, tb.charge_recurring = self.rtp.get_recurring_by_tenant(tenant.id)
            for bill in self.rtp.utilityBillList:
                if tenant.id in bill.tenants:
                    self.__add_bill(bill, tb)
            self.rtp.tenantBillList.append(tb)

    def utility_bills_sql_insert(self):
        """ Insert bills in the table. Will check for duplicates first, and warn the user if found. """
        for ub in self.rtp.utilityBillList:
            tenant_str = self.__tenants_list_to_str(ub)
            self.sql_curr.execute("SELECT * from utility_bills WHERE (year IS ?) and (month is ?) and (label IS ?)", [ub.year, ub.month, ub.label])
            fetch = self.sql_curr.fetchall()
            if len(fetch) > 0:
                self.sql_curr.execute("UPDATE utility_bills SET amount = ?, tenants = ? WHERE (year IS ?) and (month is ?) and (label IS ?)",
                                      [ub.amount, tenant_str, ub.year, ub.month, ub.label])
            else:
                self.sql_curr.execute("INSERT INTO utility_bills VALUES (?,?,?,?,?,?)", [ub.label, ub.amount, ub.month, ub.year, tenant_str, ub.memo])
        self.sql_conn.commit()
        self.rtp.utilityBillList.clear()
        return

    def utility_bills_sql_update(self):
        """ Insert bills in the table. Will check for duplicates first, and warn the user if found. """
        for ub in self.rtp.utilityBillList:
            tenant_str = self.__tenants_list_to_str(ub)
            self.sql_curr.execute("UPDATE utility_bills SET amount = ?, tenants = ? WHERE (year IS ?) and (month is ?) and (label IS ?)", [ub.amount, tenant_str, ub.year, ub.month, ub.label])
        self.sql_conn.commit()

    def tenant_bills_sql_insert(self):
        for t in self.rtp.tenantBillList:
            self.sql_curr.execute("INSERT OR REPLACE INTO tenant_bills VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                  [t.tenant_id, t.tenant_name, t.month, t.year, t.paid,
                                  t.charge_room, t.charge_internet, t.charge_electricity, t.charge_gas, t.charge_other, t.charge_total,
                                  t.memo_internet, t.memo_gas, t.memo_electricity, t.memo_other])
        self.sql_conn.commit()
        return True

    def tenant_bills_sql_update(self):
        for t in self.rtp.tenantBillList:
            print("update....")
            self.sql_curr.execute("""UPDATE tenant_bills 
                                      SET paid = ?, charge_room = ?, charge_internet = ?, charge_electricity = ?, charge_gas = ?, charge_other = ?,
                                          charge_total = ?, memo_internet = ?, memo_gas = ?, memo_electricity = ?, memo_other = ? 
                                      WHERE (tenant_id IS ?) AND (year IS ?) AND (month is ?)""",
                                  [t.paid, t.charge_room, t.charge_internet, t.charge_electricity, t.charge_gas, t.charge_other, t.charge_total,
                                   t.memo_internet, t.memo_gas, t.memo_electricity, t.memo_other, t.tenant_id, t.year, t.month])
        self.sql_conn.commit()

    # Other functions
    def print_cursor(self):
        for row in self.sql_curr:
            print(row)
        input("Press Enter to continue")

    def fetch_unpaid_tenant_bills(self):
        self.sql_curr.execute("SELECT * FROM tenant_bills WHERE paid is 0")
        for row in self.sql_curr.fetchall():
            self.__sql_tenant_bill_to_obj(row)

    # private member functions
    def __sql_tenant_bill_to_obj(self, row: List):
        tb = TenantBill()
        tb.tenant_id = row[0]
        tb.tenant_name = row[1]
        tb.month = row[2]
        tb.year = row[3]
        tb.paid = row[4]
        tb.charge_room = row[5]
        tb.charge_internet = row[6]
        tb.charge_electricity = row[7]
        tb.charge_gas = row[8]
        tb.charge_other = row[9]
        tb.charge_total = row[10]
        tb.memo_internet = row[11]
        tb.memo_gas = row[12]
        tb.memo_electricity = row[13]
        tb.memo_other = row[14]
        self.rtp.tenantBillList.append(tb)

    def __sql_tenants_to_list(self):
        self.rtp.tenantList = []
        for row in self.sql_curr:
            tenant = Tenant()
            tenant.id = row[0]
            tenant.name = row[1]
            tenant.email_addr = row[2]
            tenant.room_rate = row[4]
            self.rtp.tenantList.append(tenant)
            self.logger.info("Tenant found: {}, ID: {}, email_addr: {}".format(tenant.name, tenant.id, tenant.email_addr))

        if len(self.rtp.tenantList) == 0:
            self.rtp.print_error("No tenants retrieved by query!")

    def __add_bill(self, bill: UtilityBill, tb: TenantBill):
        # TODO: Add support for multiple bills of the same type in a month! Should be cumulative!
        try:
            count = len(bill.tenants)
            if bill.label == "electricity":
                tb.charge_electricity = round((bill.amount / count), 2)
                tb.memo_electricity = bill.memo

            if bill.label == "gas":
                tb.charge_gas = round((bill.amount / count), 2)
                tb.memo_gas = bill.memo

            if bill.label == "internet":
                tb.charge_internet = round((bill.amount / count), 2)
                tb.memo_internet = bill.memo

            if bill.label == "other":
                tb.charge_other = round((bill.amount / count), 2)
                tb.memo_other = bill.memo

        except TypeError:
            self.logger.critical("TypeError in sql.__add_bill(): {}".format(vars(bill)))
            self.rtp.critical_stop("Stopped by TypeError in sql.__add_bill()")

    @staticmethod
    def __tenants_list_to_str(ub: UtilityBill):
        """ Converts a list of integers into an SQL friendly tenant_id string """
        t_str = ''
        first = True
        for t in ub.tenants:
            if first:
                t_str = t_str + str(t)
                first = False
            else:
                t_str = t_str + ',' + str(t)
        return t_str
