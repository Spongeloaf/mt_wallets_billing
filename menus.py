
# imports and init
from typing import List
import billing_lib as blib
import sql_interface
import pdf_compositor
import bill_mailer
import menu_prompts as mp
from os import system


class Menu:
    def __init__(self, prompt: str, funcs: List, prompt_2=''):
        """ Creates a cmd prompt menu
        The first selection is always the default if nothing is entered. """
        self.prompt = prompt
        self.prompt_2 = prompt_2
        self.funcs = funcs
        self.max_choice = len(funcs) - 1
        self.selection = 0
        self.exit = False

    def __call__(self):
        self.run()

    def run(self):
        """ Gets a selection and runs the the function by slicing the func list """
        system('cls')
        print(self.prompt)
        self.get_input(0, self.max_choice)
        if self.selection == '*':
            return
        self.funcs[self.selection]()

    def get_input(self, lower: int, upper: int):
        """ Gets an input from cmd prompt """
        while True:
            self.selection = input("")
            if self.selection == '':
                self.selection = 1
            try:
                # selection is int. Subtract one for slicing func list.
                self.selection = int(self.selection) - 1
                if self.selection_is_valid(lower, upper):
                    break
            except ValueError:
                if self.selection == '*':
                    self.exit = True
                    return
            print("\nInvalid selection. Please try again.\n")
            print(self.prompt)

    def selection_is_valid(self, lower: int, upper: int):
        """ Returns True if a selection is invalid """
        if self.selection < lower:
            return False
        if self.selection > upper:
            return False
        return True


class MenuMain(Menu):
    def run(self):
        """ Gets a selection and runs the the function by slicing the func list """
        while True:
            system('cls')
            print(self.prompt)
            self.get_input(0, self.max_choice)

            if self.selection == '*':
                exit()

            self.funcs[self.selection]()


class MenuInput(Menu):
    """ Executes the func list in order """
    def run(self):
        system('cls')
        print(self.prompt)
        for func in self.funcs:
            func()


class MenuLoop(Menu):
    def run(self):
        while True:
            system('cls')
            print(self.prompt)
            for func in self.funcs:
                func()
            print(self.prompt_2)
            self.get_input(0, 1)
            if self.selection == 1:
                return


class MenuWithFunc(Menu):
    def __init__(self, prompt: str, funcs: List, prompt_2=''):
        """ Creates a cmd prompt menu
        The first selection is always the default if nothing is entered. """
        self.prompt = prompt
        self.prompt_2 = prompt_2
        self.funcs = funcs
        self.max_choice = len(funcs) - 1
        self.selection = 0
        self.exit = False
        self.start_func = self.funcs.pop(0)

    def run(self):
        """ executes a function before getting user input """
        system('cls')
        print(self.prompt)
        self.start_func()
        self.get_input(0, self.max_choice)
        if self.selection == '*':
            return
        self.funcs[self.selection]()


class MenuStructure:
    def __init__(self,
                 rtp: blib.RunTimeParams,
                 sql: sql_interface.SqlInterface,
                 pdf: pdf_compositor.PdfCompositor,
                 mail: bill_mailer.Mailer,):
        self.rtp = rtp
        self.sql = sql
        self.pdf = pdf
        self.mail = mail

        # menus
        self.check_tenant_bill_list = MenuWithFunc(prompt=mp.check_tenant_bill_list,
                                                   funcs=[rtp.print_tenant_list,
                                                          blib.func_1,
                                                          blib.func_2])
                                #################################################################

        self.prepare_tenant_bills = MenuLoop(prompt=mp.prepare_tenant_bills,
                                             prompt_2=mp.prepare_tenant_bills_2,
                                             funcs=[rtp.billing_date_user_input,
                                                    sql.get_tenants_by_date,
                                                    self.check_tenant_bill_list])

        self.main = MenuMain(prompt=mp.main,
                             funcs=[blib.func_1,
                                    blib.func_2,
                                    self.prepare_tenant_bills])

    def __call__(self):
        self.main()


