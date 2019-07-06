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

    def get_tenants_by_date(self, month: int, year: int):
        # TODO: MAKE THIS WORK!
        # """ retrieve list of tenants for a specific date/year """
        # self.sql_curr.execute("SELECT * FROM tenants WHERE is_current IS 1")  <------- MODIFY THIS STATEMENT, THE REST SHOULD BE GOOD
        # return self.sql_tenant_to_obj()
        pass

    def get_active_tenants(self):
        """ retrieve list of active tenants """
        self.sql_curr.execute("SELECT * FROM tenants WHERE is_current IS 1")
        return self.sql_tenant_to_obj()

    def sql_tenant_to_obj(self):
        tl = []
        for row in self.sql_curr:
            tenant = Tenant()
            tenant.id = row[0]
            tenant.name = row[1]
            tenant.email_addr = row[2]
            tenant.charge_room = row[4]
            tl.append(tenant)
            self.logger.info("Tenant found: {}, ID: {}, email_addr: {}".format(tenant.name, tenant.id, tenant.email_addr))
        return tl

    def get_utility_bills(self, ubl: List[UtilityBill]):
        """ return bills for month specified """
        self.sql_curr.execute("SELECT * from utility_bills WHERE (year IS ?) and (month is ?)", [self.rtp.year, self.rtp.month])
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
                    self.logger.critical("Value error in get_utility_bills, bad tenant string: {}".format(tenants_str))
                    self.rtp.critical_stop("Stopped by sql.get_utility_bills() for ValueError")

            ub = UtilityBill(label, amount, tenants, month, year, memo)
            ubl.append(ub)
            self.logger.info("Utility Bill found: {} for {} split between tenants: {}".format(label, amount, tenants_str))

    def check_utility_bill_tenants(self, ubl: List[UtilityBill], tl: List[Tenant]):
        id_list = []
        for t in tl:
            id_list.append(t.id)

        for bill in ubl:
            for tenant in bill.tenants:
                if tenant not in id_list:
                    self.logger.critical("A bill is targeted for a non-active tenant in check_utility_bill_tenants: {}".format(tenant))
                    self.rtp.critical_stop("Stopped by sql.check_utility_bill_tenants for invalid tenant string")

    def prepare_tennant_bills(self, ubl: List[UtilityBill], tl: List[Tenant]):
        for tenant in tl:
            for bill in ubl:
                for i in bill.tenants:
                    if tenant.id == i:
                        self.add_bill(bill, tenant)
            tenant.update_total()

    def add_bill(self, bill: UtilityBill, tenant: Tenant):
        # TODO: Add support for multiple bills of the same type in a month! Should be cumulative!
        try:
            count = len(bill.tenants)
            if bill.label == "electricity":
                tenant.charge_electricity = round((bill.amount / count), 2)
                tenant.memo_electricity = bill.memo
                return

            if bill.label == "gas":
                tenant.charge_gas = round((bill.amount / count), 2)
                tenant.memo_gas = bill.memo
                return

            if bill.label == "internet":
                tenant.charge_internet = round((bill.amount / count), 2)
                tenant.memo_internet = bill.memo
                return

            if bill.label == "other":
                tenant.charge_other = round((bill.amount / count), 2)
                tenant.memo_other = bill.memo
                return

            self.logger.critical("Bad bill label in sql.add_bill(): {}".format(vars(bill)))
            self.rtp.critical_stop("Stopped by bad bill label in sql.add_bill()")
        except TypeError:
            self.logger.critical("TypeError in sql.add_bill(): {}".format(vars(bill)))
            self.rtp.critical_stop("Stopped by TypeError in sql.add_bill()")

    def save_tenant_bills(self, tl: List[Tenant]):
        for t in tl:
            # The 0 in the argument list is for "paid = false"
            try:
                self.sql_curr.execute("INSERT INTO tenant_bills VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                      [t.id, t.name, self.rtp.month, self.rtp.year, 0,
                                       t.charge_room, t.charge_internet, t.charge_electricity, t.charge_gas, t.charge_other, t.charge_total,
                                       t.memo_internet, t.memo_gas, t.memo_electricity, t.memo_other])
            except sqlite3.IntegrityError:
                self.logger.critical("Duplicate bills in save_tenant_bills(): {}".format(vars(t)))
                self.rtp.critical_stop("Stopped by sql.save_tenant_bills()")

            self.sql_conn.commit()

    def print_cursor(self):
        for row in self.sql_curr:
            print(row)

    def update_tenant_bill(self, t: Tenant):
        self.sql_curr.execute("REPLACE INTO tenant_bills VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                              [t.id, t.name, self.rtp.month, self.rtp.year, 0,
                               t.charge_room, t.charge_internet, t.charge_electricity, t.charge_gas, t.charge_other, t.charge_total,
                               t.memo_internet, t.memo_gas, t.memo_electricity, t.memo_other])

    def insert_utility_bills(self, ubl: List[UtilityBill]):
        """ Insert bills in the table. Will check for duplicates first, and warn the user if found. """
        for ub in ubl:
            tenant_str = self.tenants_list_to_str(ub.tenants)
            self.sql_curr.execute("SELECT * from utility_bills WHERE (year IS ?) and (month is ?) and (label IS ?)", [ub.year, ub.month, ub.label])
            if len(self.sql_curr.fetchall()) > 0:
                print("Duplicate utility bill!")
            else:
                self.sql_curr.execute("INSERT INTO utility_bills VALUES (?,?,?,?,?,?)", [ub.label, ub.amount, ub.month, ub.year, tenant_str, ub.memo])
            self.sql_conn.commit()

    @staticmethod
    def tenants_list_to_str(t_list: List[int]):
        """ Converts a list of integers into an SQL friendly tenant string """
        t_str = ''
        first = True
        for t in t_list:
            if first:
                t_str = t_str + str(t)
                first = False
            else:
                t_str = t_str + ',' + str(t)
        return t_str
