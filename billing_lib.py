from typing import List
import datetime
from genericpath import isfile
import logging
from sys import exit
import configparser
from sys import exit
from colorama import Fore
from colorama import init as color_init


class RunTimeParams:
    def __init__(self):
        color_init()
        self.prepare = False
        self.compose = False
        self.send = False
        self.month = ''
        self.year = ''
        self.duplicates_found = False
        self.google_path = get_google_drive_path()
        self.config_fname = self.google_path + 'settings.ini'
        if not isfile(self.config_fname):
            self.create_config_file()
        self.config = self.load_config()
        self.rtp_log_level = self.config['rtp']['log_level']
        self.allow_duplicate_bills = bool(self.config['rtp']['allow_duplicate_bills'])
        self.bill_tenant_0 = bool(self.config['rtp']['bill_tenant_0'])
        self.rtp_allow_dupes = bool(self.config['rtp']['allow_duplicate_bills'])
        self.sql_log_level = self.config['sql']['log_level']
        self.sql_db_fname = self.google_path + self.config['sql']['db_file_name']
        self.pdf_log_level = self.config['pdf']['log_level']
        self.pdf_docx_template = self.google_path + self.config['pdf']['docx_template']

        self.mail_log_level = self.config['email']['log_level']
        self.mail_user = self.config['email']['user']
        self.mail_pswd = self.config['email']['pswd']
        self.mail_server = self.config['email']['server']
        self.mail_port = self.config['email']['port']
        self.mail_msg = self.config['email']['msg_body']

        self.logger_fname = self.google_path + 'rtp_log.txt'
        self.logger = create_logger(self.logger_fname, self.rtp_log_level, "rtp_log")
        if not isfile(self.sql_db_fname):
            self.critical_stop("Something has gone very wrong! db file doesn't exist!")
        self.logger.debug("Run Time Properties are initialized")

        self.ubl: List[UtilityBill] = []
        self.tl: List[Tenant] = []

    def create_config_file(self):
        """ Creates a new, default, server config file. """
        config = configparser.ConfigParser()

        # default values:
        config['rtp'] = {'log_level': 'DEBUG'}
        config['sql'] = {'log_level': 'DEBUG',  'db_file_name': 'billing.sqlite'}
        config['pdf'] = {'log_level': 'DEBUG', 'docx_template': 'billing_template.docx'}
        config['email_addr'] = {'log_level': 'DEBUG', 'email_user': 'MTWallets@outlook.com',
                           'email_pswd': 'MTnoreply430', 'server': 'smtp-mail.outlook.com',
                           'port': '587', 'msg_body': 'Please see the attached rent bill. E-transfers or questions may be sent to peter.v@live.ca'}

        config_file = open(self.config_fname, 'x')
        config.write(config_file)

    def load_config(self):
        """loads a config file """
        try:
            config = configparser.ConfigParser()
            config.read(self.config_fname)
            return config
        except KeyError:
            self.critical_stop('Config file KeyError. Check config file for missing values!')

    def billing_date_use_current(self):
        self.month = datetime.date.today().month
        self.year = datetime.date.today().year

    def ub_tenant_list_from_tl(self):
        for ub in self.ubl:
            ub.tenants = []
            for t in self.tl:
                i = t.id
                ub.tenants.append(i)

    def print_bill_date(self):
        print("Year: {}, Month: {}\n".format(self.year, self.month))

    def critical_stop(self, message: str):
        self.logger.critical("Program halted for reason: {}".format(message))
        exit(1)

    def print_tenant_list(self):
        print("\nTenant list for {} {}:".format(self.month, self.year))
        for t in self.tl:
            t.print()

    def print_utility_bills(self):
        print("\nUtility bill list for {} {}:".format(self.month, self.year))
        print("\n" + Fore.BLUE + "{:12} | {:8} |{}".format("Label", "Amount", "Tenants") + Fore.RESET)
        for ub in self.ubl:
            ub.print()

    def print_tenant_bills(self):
        print("\nTenant list for {} {}:".format(self.month, self.year))
        print("\n" + Fore.BLUE + "{:32} | {:11} | {:11} | {:11} | {:11} | {:11} | {:11}".format("Name", "Room", "Internet", "Electricity", "Gas", "Other", "Total") + Fore.RESET)
        for t in self.tl:
            print("{:32} | {:11} | {:11} | {:11} | {:11} | {:11} | {:11}".format(t.name, t.charge_room, t.charge_internet, t.charge_electricity, t.charge_gas, t.charge_other, t.charge_total))

    @staticmethod
    def print_error(s):
        print(Fore.RED + s + Fore.RESET)


class Tenant:
    def __init__(self):
        self.id = 0
        self.email_addr = ''
        self.name = ''
        self.year_in = -1
        self.year_out = -1
        self.month_in = -1
        self.month_out = -1
        self.charge_room = 0.0
        self.charge_internet = 0.0
        self.charge_gas = 0.0
        self.charge_electricity = 0.0
        self.charge_other = 0.0
        self.charge_total = 0.0
        self.memo_internet = 0.0
        self.memo_gas = ''
        self.memo_electricity = ''
        self.memo_other = ''
        self.pdf = None
        self.pdf_short_name = None
        self.docx = None
        self.email_msg = None

    def update_total(self):
        self.charge_total = round((self.charge_room + self.charge_internet + self.charge_gas + self.charge_electricity + self.charge_other), 2)

    def print(self):
        print('{} | {:32} | {:24}'.format(self.id, self.name, self.email_addr))


class UtilityBill:
    def __init__(self, label: str='', amount: float=0.0, tenants: List[int]=None, month: int=0, year: int=0, memo: str = ''):
        self.label = label
        self.amount = amount
        self.month = month
        self.year = year
        self.tenants = tenants
        self.memo = memo

    def print(self):
        string = ''
        for t in self.tenants:
            string += ' ' + str(t)
        print('{:12} | {:8} |{}'.format(self.label, self.amount, string))


def func_1():
    print("func 1")
    input("Press enter to continue")


def func_2():
    print("func 2")
    input("Press enter to continue")


def func_3():
    print("func 3")
    input("Press enter to continue")


def remove_tenant_0(tl: List[Tenant]):
    """ Removes tenant 0 from the list. Used to prevent house owner from being emailed a bill. """
    for t in tl:
        if t.id == 0:
            tl.remove(t)


def get_google_drive_path():
    """ Get Google Drive path on windows machines.
    :return: str
    """
    # this code written by /u/Vassilis Papanikolaou from this post:
    # https://stackoverflow.com/a/53430229/10236951

    import sqlite3
    import os

    db_path = (os.getenv('LOCALAPPDATA') + '\\Google\\Drive\\user_default\\sync_config.db')
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT * from data where entry_key = 'local_sync_root_path'")
    res = cursor.fetchone()
    path = res[2][4:]
    db.close()
    return path + '\\software_dev\\mt_wallets_billing\\'


def format_values(value):
    """ takes a value and ensures it gets rounded if needed and converted to a string. """

    if value is float:
        value = round(value, 2)

    return str(value)


def create_logger(log_file_const, log_level='DEBUG', log_name='a_logger_has_no_name'):
    """Creates a logger fro the server. Depends on logging module.
    Logger is created with default level set to 'debug'.
    level may be changed later by config files."""

    # Create logger
    log = logging.getLogger(log_name)
    log.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file_const, mode='w')      # file handler object for logger
    ch = logging.StreamHandler()                            # create console handler

    ch.setLevel(logging.ERROR)                              # default log levels set to debug in case config fails
    fh.setLevel(logging.DEBUG)                              # default log levels set to debug in case config fails

    # set levels from config file
    if log_level == 'DEBUG':
        fh.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        fh.setLevel(logging.INFO)
    elif log_level == 'WARNING':
        fh.setLevel(logging.WARNING)
    elif log_level == 'ERROR':
        fh.setLevel(logging.ERROR)
    elif log_level == 'CRITICAL':
        fh.setLevel(logging.CRITICAL)
    else:
        log.critical('Bad logger level argument. reverting to "debug" logger')
        log.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)

    return log


def print_bills(tl: List[Tenant]):
    for t in tl:
        print(vars(t))



