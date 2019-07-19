from billing_lib import *
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
        if len(self.rtp.tl) == 0:
            self.rtp.print_error("No tenants found for query!")

    def get_tenants_by_active(self):
        """ retrieve list of active tenants """
        self.sql_curr.execute("SELECT * FROM tenants WHERE is_current IS 1")
        self.__sql_tenants_to_list()
        if len(self.rtp.tl) == 0:
            self.rtp.print_error("No tenants found for query!")

    def get_utility_bills(self):
        """ return bills for month specified """
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
            self.rtp.ubl.append(ub)
            self.logger.info("Utility Bill found: {} for {} split between tenants: {}".format(label, amount, tenants_str))
        if len(self.rtp.ubl) == 0:
            self.rtp.print_error("No utility bills found for query!")

    def check_utility_bill_tenants(self):
        id_list = []
        for t in self.rtp.tl:
            id_list.append(t.id)

        for bill in self.rtp.ubl:
            for tenant in bill.tenants:
                if tenant not in id_list:
                    self.logger.critical("A bill is targeted for a non-active tenant_id in check_utility_bill_tenants: {}".format(tenant))
                    self.rtp.critical_stop("Stopped by sql.check_utility_bill_tenants for invalid tenant_id string")

    def prepare_tennant_bills(self):
        """ Create tenant bills """
        for t in self.rtp.tl:
            tb = TenantBill()
            tb.tenant_id = t.id
            tb.tenant_name = t.name
            tb.email_addr = t.email_addr
            tb.month = self.rtp.month_int
            tb.year = self.rtp.year
            for bill in self.rtp.ubl:
                if t.id in bill.tenants:
                    self.__add_bill(bill, tb)
            tb.update_total()
            self.rtp.tbl.append(tb)

    def utility_bills_sql_insert(self):
        """ Insert bills in the table. Will check for duplicates first, and warn the user if found. """
        for ub in self.rtp.ubl:
            tenant_str = self.__tenants_list_to_str(ub)
            self.sql_curr.execute("SELECT * from utility_bills WHERE (year IS ?) and (month is ?) and (label IS ?)", [ub.year, ub.month, ub.label])
            if len(self.sql_curr.fetchall()) > 0:
                self.rtp.print_error("Duplicate utility bill!")
                return False
            else:
                self.sql_curr.execute("INSERT INTO utility_bills VALUES (?,?,?,?,?,?)", [ub.label, ub.amount, ub.month, ub.year, tenant_str, ub.memo])
        self.sql_conn.commit()
        return True

    def utility_bills_sql_update(self):
        """ Insert bills in the table. Will check for duplicates first, and warn the user if found. """
        for ub in self.rtp.ubl:
            tenant_str = self.__tenants_list_to_str(ub)
            self.sql_curr.execute("UPDATE utility_bills SET amount = ?, tenants = ? WHERE (year IS ?) and (month is ?) and (label IS ?)", [ub.amount, tenant_str, ub.year, ub.month, ub.label])
        self.sql_conn.commit()

    def tenant_bills_sql_insert(self):
        for t in self.rtp.tbl:
            self.sql_curr.execute("SELECT * from tenant_bills WHERE (year IS ?) and (month is ?) and (tenant_id IS ?)", [self.rtp.year, self.rtp.month_int, t.tenant_id])
            if len(self.sql_curr.fetchall()) > 0:
                self.rtp.print_error("Duplicate bills in tenant_bills_sql_insert(): {}".format(vars(t)))
                return False
            else:
                self.sql_curr.execute("INSERT INTO tenant_bills VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                      [t.tenant_id, t.tenant_name, t.month, t.year, t.paid,
                                       t.charge_room, t.charge_internet, t.charge_electricity, t.charge_gas, t.charge_other, t.charge_total,
                                       t.memo_internet, t.memo_gas, t.memo_electricity, t.memo_other])
        self.sql_conn.commit()
        return True

    def tenant_bills_sql_update(self):
        for t in self.rtp.tbl:
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
    def __update_tenant_bill(self, t: TenantBill):
        self.sql_curr.execute("REPLACE INTO tenant_bills VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                              [t.tenant_id, t.tenant_name, self.rtp.month_int, self.rtp.year, 0,
                               t.charge_room, t.charge_internet, t.charge_electricity, t.charge_gas, t.charge_other, t.charge_total,
                               t.memo_internet, t.memo_gas, t.memo_electricity, t.memo_other])

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
        self.rtp.tbl.append(tb)

    def __sql_tenants_to_list(self):
        self.rtp.tl = []
        for row in self.sql_curr:
            tenant = Tenant()
            tenant.id = row[0]
            tenant.name = row[1]
            tenant.email_addr = row[2]
            tenant.charge_room = row[4]
            self.rtp.tl.append(tenant)
            self.logger.info("Tenant found: {}, ID: {}, email_addr: {}".format(tenant.name, tenant.id, tenant.email_addr))

        if len(self.rtp.tl) == 0:
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
