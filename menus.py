import menu_prompts as mp
import billing_lib as blib
import sql_interface
import pdf_compositor
import bill_mailer
from os import system
from sys import exit
import datetime


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
            self.prompt(mp.main_loop_begin)
            selection = self.get_input(0, 3)

            if selection == 0:
                exit(0)

            if selection == 1:
                self.tenant_bill_recievables()

            if selection == 2:
                self.add_utiility_bill()

            if selection == 3:
                self.prepare_tenant_bills()

    def tenant_bill_recievables(self):
        pass

    def add_utiility_bill(self):
        pass

    def prepare_tenant_bills(self):
        while True:
            self.prompt(mp.prepare_tenant_bills)
            selection = self.get_input(0, 1)
            if selection == 0:
                return
            if selection == 1:
                # get year
                self.prompt(mp.get_billing_year)
                selection = self.get_year()
                if selection == 0:
                    return
                else:
                    self.rtp.year = selection

                # get month
                self.prompt(mp.get_billing_month)
                selection = self.get_month()
                if selection == 0:
                    return
                else:
                    self.rtp.month = selection

                # prepare tenant list
                self.sql.get_tenants_by_date()
                self.rtp.print_tenant_list()
                print(mp.check_tenant_bill_list)
                selection = self.get_input(0, 1)
                if selection == 0:
                    return

                # prepare utility bills
                self.prompt("")
                self.sql.get_utility_bills()
                self.sql.check_utility_bill_tenants()
                self.sql.print_utility_bills()
                self.sql.prepare_tennant_bills()
                self.prompt("")
                self.sql.print_tenant_bills()

                # confirm tenant bills
                selection = self.get_input(0, 1)
                if selection == 0:
                    return

                # save bills
                self.sql.save_tenant_bills()

            # shall we compose docs?
            self.prompt(mp.prepare_pdf)
            selection = self.get_input(0, 3)
            if selection == 0:
                return
            if selection == 1:
                self.pdf.tenant_bills_to_docx()
                self.pdf.docx_to_pdf()
            if selection == 2:
                self.pdf.tenant_bills_to_docx()

            # shall we email?
            self.prompt(mp.prepare_email)
            selection = self.get_input(0, 2)
            if selection == 0:
                return
            if selection == 1:
                print("Generating PDFs. This may take some time...")
                self.mail.compose_email()
                self.mail.send_email()
            if selection == 2:
                print("Generating PDFs. This may take some time...")
                self.mail.compose_email()
                self.mail.send_email_to_landord()


    @staticmethod
    def prompt(prompt):
        system('cls')
        if prompt != "":
            print(prompt)

    def get_year(self):
        while True:
            selection = input("")
            if selection == '':
                selection = datetime.date.today().year

            try:
                # selection is int. Subtract one for slicing func list.
                selection = int(selection)
                if self.selection_is_valid(0, 9999, selection):
                    return selection
            except ValueError:
                if selection == '*':
                    return 0
                if selection == 'q':
                    return 0
                if selection == '0':
                    return 0
            print("\nInvalid selection. Please try again.\n")

    def get_month(self):
        while True:
            selection = input("")
            if selection == '':
                selection = datetime.date.today().month

            try:
                # selection is int. Subtract one for slicing func list.
                selection = int(selection)
                if self.selection_is_valid(0, 12, selection):
                    return selection
            except ValueError:
                if selection == '*':
                    return 0
                if selection == 'q':
                    return 0
                if selection == '0':
                    return 0
            print("\nInvalid selection. Please try again.\n")

    def get_input(self, lower: int, upper: int):
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
    def selection_is_valid(lower: int, upper: int, selection):
        """ Returns True if a selection is invalid """
        if selection < lower:
            return False
        if selection > upper:
            return False
        return True



menu = Menu()
menu()
