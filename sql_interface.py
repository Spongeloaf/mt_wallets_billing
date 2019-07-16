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

    # execute these in order to complete the billing cycle
    def get_tenants_by_date(self):
        # TODO: Fix this so it checks months as well!
        """ retrieve list of tenants for a specific date/year """
        self.sql_curr.execute("SELECT * FROM tenants WHERE ? BETWEEN year_in AND "
                              "CASE"
                              " WHEN year_out is NULL THEN 9999"
                              " ELSE year_out "
                              "END", [self.rtp.year])
        self.__sql_tenants_to_list()

    def get_tenants_by_active(self):
        """ retrieve list of active tenants """
        self.sql_curr.execute("SELECT * FROM tenants WHERE is_current IS 1")
        self.__sql_tenants_to_list()

    def get_utility_bills(self):
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
            self.rtp.ubl.append(ub)
            self.logger.info("Utility Bill found: {} for {} split between tenants: {}".format(label, amount, tenants_str))

    def check_utility_bill_tenants(self):
        id_list = []
        for t in self.rtp.tl:
            id_list.append(t.id)

        for bill in self.rtp.ubl:
            for tenant in bill.tenants:
                if tenant not in id_list:
                    self.logger.critical("A bill is targeted for a non-active tenant in check_utility_bill_tenants: {}".format(tenant))
                    self.rtp.critical_stop("Stopped by sql.check_utility_bill_tenants for invalid tenant string")

    def prepare_tennant_bills(self):
        for tenant in self.rtp.tl:
            for bill in self.rtp.ubl:
                for i in bill.tenants:
                    if tenant.id == i:
                        self.__add_bill(bill, tenant)
            tenant.update_total()

    def insert_utility_bills(self):
        """ Insert bills in the table. Will check for duplicates first, and warn the user if found. """
        for ub in self.rtp.ubl:
            tenant_str = self.__tenants_list_to_str()
            self.sql_curr.execute("SELECT * from utility_bills WHERE (year IS ?) and (month is ?) and (label IS ?)", [ub.year, ub.month, ub.label])
            if len(self.sql_curr.fetchall()) > 0:
                print("Duplicate utility bill!")
            else:
                self.sql_curr.execute("INSERT INTO utility_bills VALUES (?,?,?,?,?,?)", [ub.label, ub.amount, ub.month, ub.year, tenant_str, ub.memo])
            self.sql_conn.commit()

    def save_tenant_bills(self):
        for t in self.rtp.tl:
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

    # Helper and printing functions
    def print_utility_bills(self):
        # Todo: Make this work!
        print("TODO: make print_utility_bills work")

    def print_cursor(self):
        for row in self.sql_curr:
            print(row)
        input("Press Enter to continue")

    def print_tenant_bills(self):
        # TODO Implement me!
        print("TODO: Implement print_tenant_bills")

    def load_tenant_bills(self):
        """ Loads tenant bills from SQL instead of generating them"""
        # TODO IMPLEMENT ME!

    # private members
    def __update_tenant_bill(self, t: Tenant):
        self.sql_curr.execute("REPLACE INTO tenant_bills VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                              [t.id, t.name, self.rtp.month, self.rtp.year, 0,
                               t.charge_room, t.charge_internet, t.charge_electricity, t.charge_gas, t.charge_other, t.charge_total,
                               t.memo_internet, t.memo_gas, t.memo_electricity, t.memo_other])

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

    def __add_bill(self, bill: UtilityBill, tenant: Tenant):
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

            self.logger.critical("Bad bill label in sql.__add_bill(): {}".format(vars(bill)))
            self.rtp.critical_stop("Stopped by bad bill label in sql.__add_bill()")
        except TypeError:
            self.logger.critical("TypeError in sql.__add_bill(): {}".format(vars(bill)))
            self.rtp.critical_stop("Stopped by TypeError in sql.__add_bill()")

    def __tenants_list_to_str(self):
        """ Converts a list of integers into an SQL friendly tenant string """
        t_str = ''
        first = True
        for t in self.rtp.tl:
            if first:
                t_str = t_str + str(t)
                first = False
            else:
                t_str = t_str + ',' + str(t)
        return t_str
