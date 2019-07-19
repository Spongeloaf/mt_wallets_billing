import menu_prompts as mp
import billing_lib as blib
import sql_interface
import pdf_compositor
import bill_mailer
from os import system
from sys import exit
import datetime
from colorama import Fore



class Menu:
    def __init__(self):
        """ Creates a cmd prompt menu
        The first selection is always the default if nothing is entered. """
        # init
        self.rtp = blib.RunTimeParams()
        self.sql = sql_interface.SqlInterface(self.rtp)
        self.pdf = pdf_compositor.PdfCompositor(self.rtp)
        self.mail = bill_mailer.Mailer(self.rtp)

    def __call__(self):
        self.run()

    def run(self):
        while True:
            # prevents lists from being re-used when finished with a task
            self.rtp.tl.clear()
            self.rtp.ubl.clear()
            self.rtp.tbl.clear()

            self.prompt(mp.main_loop_begin)
            selection = self.get_int(0, 3)

            if selection == 0:
                exit(0)

            if selection == 1:
                self.tenant_bill_recievables()

            if selection == 2:
                self.add_utiility_bill()

            if selection == 3:
                self.prepare_tenant_bills()

    def tenant_bill_recievables(self):
        # get unpaid bills
        self.sql.fetch_unpaid_tenant_bills()
        self.print_tenant_bills()
        print(mp.please_review_list)
        selection = self.get_int(0, 1)
        if selection == 0:
            return

        # for bill in bill list, mark as paid
        changes = False
        for tb in self.rtp.tbl:
            self.prompt(mp.is_tenant_bill_paid_1)
            tb.print()
            print(mp.is_tenant_bill_paid_2)
            selection = self.get_int(0, 2)
            if selection == 0:
                return
            if selection == 1:
                continue
            if selection == 2:
                tb.paid = 1
                changes = True
        if changes:
            self.sql.tenant_bills_sql_update()
        self.prompt(mp.tenant_bills_updated)
        input()

    def add_utiility_bill(self):
        while True:
            if not self.input_billing_dates():
                return

            ub = blib.UtilityBill()

            # get tenant_id list, so we don't have to write tenant_id list strings ourselves.
            self.sql.get_tenants_by_date()
            system('cls')
            self.print_tenant_list()
            self.prompt(mp.please_review_list)
            selection = self.get_int(0, 1)
            if selection == 0:
                return

            ub.year = self.rtp.year
            ub.month = self.rtp.month_int

            # Prevents typos by providing int options instead of user typing their own labels
            self.prompt(mp.utility_bill_type.format(self.rtp.month_int, self.rtp.year))
            selection = self.get_int(0, 4)
            if selection == 0:
                return
            if selection == 1:
                ub.label = 'electricity'
            if selection == 2:
                ub.label = 'gas'
            if selection == 3:
                ub.label = 'internet'
            if selection == 4:
                ub.label = 'other'

            self.prompt(mp.utility_bill_amount)
            ub.amount = self.get_float()

            self.prompt(mp.utility_bill_memo)
            ub.memo = input("")

            self.rtp.ubl.append(ub)
            self.rtp.ub_tenant_list_from_tl()
            self.prompt(mp.check_utility_bill_list)
            self.print_utility_bills()
            selection = self.get_int(0, 1)
            if selection == 0:
                return

            # commit
            if not self.sql.utility_bills_sql_insert():
                self.prompt(mp.sql_ub_insert_failure)
                selection = self.get_int(0, 1)
                if selection == 0:
                    return
                self.sql.utility_bills_sql_update()

            self.prompt(mp.utility_bill_end)
            selection = self.get_int(0, 1)
            if selection == 0:
                return

    def prepare_tenant_bills(self):
        while True:
            if not self.input_billing_dates():
                return
            self.prompt(mp.prepare_tenant_bills)
            selection = self.get_int(0, 2)
            if selection == 0:
                return
            if selection == 1:

                # prepare tenant_id list
                self.sql.get_tenants_by_date()
                self.print_tenant_list()
                print(mp.please_review_list)
                selection = self.get_int(0, 1)
                if selection == 0:
                    return

                # prepare utility bills
                self.prompt("")
                self.sql.get_utility_bills()
                self.sql.check_utility_bill_tenants()
                self.print_utility_bills()
                self.sql.prepare_tennant_bills()
                self.prompt("")
                self.print_tenant_bills()

                # confirm tenant bills
                selection = self.get_int(0, 1)
                if selection == 0:
                    return

                # save bills
                if not self.sql.tenant_bills_sql_insert():
                    self.prompt(mp.sql_tb_insert_failure)
                    selection = self.get_int(0, 1)
                    if selection == 0:
                        return
                    self.sql.tenant_bills_sql_update()
            else:
                print("!!!!!!!NOT IMPLEMENTED YET!!!!!!!!")
                # prepare tenant_id list
                self.sql.get_tenants_by_date()
                self.sql.fetch_unpaid_tenant_bills()


            # shall we compose docs?
            self.prompt(mp.prepare_pdf)
            selection = self.get_int(0, 3)
            if selection == 0:
                return
            if selection == 1:
                print("Generating PDFs. This may take some time...")
                self.pdf.tenant_bills_to_docx()
                self.pdf.docx_to_pdf()
            if selection == 2:
                print("Generating DOCXs. This may take some time...")
                self.pdf.tenant_bills_to_docx()

            # shall we email?
            self.prompt(mp.prepare_email)
            selection = self.get_int(0, 2)
            if selection == 0:
                return
            if selection == 1:
                print("Sending emails. This may take some time...")
                self.mail.compose_email()
                self.mail.send_email()
                return
            if selection == 2:
                print("Generating emails to landlord. This may take some time...")
                self.mail.compose_email()
                self.mail.email_to_landord()
                self.mail.send_email()
                return

    @staticmethod
    def prompt(prompt):
        system('cls')
        if prompt != "":
            print(prompt)

    def input_billing_dates(self):
        # get year
        self.prompt(mp.get_billing_year)
        proceed = self.__get_year()
        if not proceed:
            return False

        # get month
        self.prompt(mp.get_billing_month)
        proceed = self.__get_month()
        if not proceed:
            return False
        return True

    def __get_year(self):
        while True:
            selection = input("")
            if selection == '':
                selection = datetime.date.today().year
            try:
                # selection is int. Subtract one for slicing func list.
                selection = int(selection)
                if self.selection_is_valid(0, 9999, selection):
                    if selection == 0:
                        return False
                    else:
                        self.rtp.year = selection
                        return True
            except ValueError:
                if selection == '*':
                    return False
                if selection == 'q':
                    return False
                if selection == '0':
                    return False
            print("\nInvalid selection. Please try again.\n")

    def __get_month(self):
        while True:
            selection = input("")
            if selection == '':
                selection = datetime.date.today().month

            try:
                # selection is int. Subtract one for slicing func list.
                selection = int(selection)
                if self.selection_is_valid(0, 12, selection):
                    if selection == 0:
                        return False
                    else:
                        # selection must be between 1 and 12 if we get here
                        self.rtp.set_month(selection)
                        return True
            except ValueError:
                if selection == '*':
                    return False
                if selection == 'q':
                    return False
                if selection == '0':
                    return False
            print("\nInvalid selection. Please try again.\n")

    def get_int(self, lower: int, upper: int):
        """ Gets an input from cmd prompt """
        while True:
            selection = input("")
            if selection == '':
                selection = 1

            try:
                # selection is int. Subtract one for slicing func list.
                selection = int(selection)
                if self.selection_is_valid(lower, upper, selection):
                    return selection
            except ValueError:
                if selection == '*':
                    return 0
                if selection == 'q':
                    return 0
                if selection == '0':
                    return 0
            print("\nInvalid selection. Please try again.\n")

    @staticmethod
    def get_float():
        """ Gets an input from cmd prompt """
        while True:
            selection = input("")
            try:
                # selection is int. Subtract one for slicing func list.
                selection = float(selection)
                return selection
            except ValueError:
                print("\nInvalid selection. Please try again.\n")

    @staticmethod
    def selection_is_valid(lower: int, upper: int, selection):
        """ Returns True if a selection is invalid """
        if selection < lower:
            return False
        if selection > upper:
            return False
        return True

    def print_tenant_list(self):
        self.prompt("\nTenant list for {} {}:".format(self.rtp.month_str, self.rtp.year))
        for t in self.rtp.tl:
            t.print()

    def print_utility_bills(self):
        self.prompt("\nUtility bill list for {} {}:".format(self.rtp.month_str, self.rtp.year))
        print("\n" + Fore.BLUE + "{:12} | {:8} |{}".format("Label", "Amount", "Tenants") + Fore.RESET)
        for ub in self.rtp.ubl:
            ub.print()

    def print_tenant_bills(self):
        self.prompt("\nTenant list for {} {}:".format(self.rtp.month_str, self.rtp.year))
        print("\n" + Fore.BLUE + "{:32} | {:4} | {:11} | {:11} | {:11} | {:11} | {:11} | {:11}".format("Name", "Paid", "Room", "Internet", "Electricity", "Gas", "Other", "Total") + Fore.RESET)
        for t in self.rtp.tbl:
            t.print()