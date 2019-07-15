from typing import List
import datetime
from genericpath import isfile
import logging
from sys import exit
import configparser
from sys import exit



class RunTimeParams:
    def __init__(self):
        self.prepare = True
        self.compose = True
        self.send = True
        self.month = ''
        self.year = ''
        self.google_path = get_google_drive_path()
        self.config_fname = self.google_path + 'settings.ini'
        if not isfile(self.config_fname):
            self.create_config_file()
        self.config = self.load_config()
        self.rtp_log_level = self.config['rtp']['log_level']
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

    def input_bill_date(self):
        m = input("Please input month, leave blank for current:\n")
        y = input("Please input year, leave blank for current:\n")

        if m == '':
            m = datetime.date.today().month
        if m is not int:
            m = int(m)

        if y == '':
            y = datetime.date.today().year
        if y is not int:
            y = int(y)

        self.month = m
        self.year = y

    def print_bill_date(self):
        print("Year: {}, Month: {}\n".format(self.year, self.month))

    def critical_stop(self, message: str):
        self.logger.critical("Program halted for reason: {}".format(message))
        exit(1)


class Tenant:
    def __init__(self, id: int = -1, email: str = '', name: str = '', charge_room: float = 0.0, charge_internet: float = 0.0,
                 charge_gas: float = 0.0, charge_electricity: float = 0.0, charge_other: float = 0.0, charge_total: float = 0.0):
        self.id = id
        self.email_addr = email
        self.name = name
        self.charge_room = charge_room
        self.charge_internet = charge_internet
        self.charge_gas = charge_gas
        self.charge_electricity = charge_electricity
        self.charge_other = charge_other
        self.charge_total = charge_total
        self.memo_internet = ''
        self.memo_gas = ''
        self.memo_electricity = ''
        self.memo_other = ''
        self.pdf = None
        self.pdf_short_name = None
        self.docx = None
        self.email_msg = None

    def update_total(self):
        self.charge_total = round((self.charge_room + self.charge_internet + self.charge_gas + self.charge_electricity + self.charge_other), 2)


class UtilityBill:
    def __init__(self, label: str, amount: int, tenants: List[int],month: int, year: int, memo: str = ''):
        self.label = label
        self.amount = amount
        self.month = month
        self.year = year
        self.tenants = tenants
        self.memo = memo








def func_1():
    print("func 1")


def func_2():
    print("func 2")


def func_3():
    print("func 3")


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

    ch.setLevel(logging.DEBUG)                              # default log levels set to debug in case config fails
    fh.setLevel(logging.DEBUG)                              # default log levels set to debug in case config fails

    # set levels from config file
    if log_level == 'DEBUG':
        ch.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)
    elif log_level == 'INFO':
        ch.setLevel(logging.INFO)
        fh.setLevel(logging.INFO)
    elif log_level == 'WARNING':
        ch.setLevel(logging.WARNING)
        fh.setLevel(logging.WARNING)
    elif log_level == 'ERROR':
        ch.setLevel(logging.ERROR)
        fh.setLevel(logging.ERROR)
    elif log_level == 'CRITICAL':
        ch.setLevel(logging.CRITICAL)
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