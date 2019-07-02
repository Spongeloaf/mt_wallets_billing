from typing import List
import datetime, calendar
from genericpath import isfile
import logging
from sys import exit


class RunTimeProperties:
    def __init__(self):
        # TODO: Replace this with a proper get_mode function to grab user input. Should allow for dry-runs, send only, compose only, etc.
        self.prepare = True
        self.compose = True
        self.send = True
        self.month = ''
        self.year = ''
        self.google_path = get_google_drive_path()
        self.logger_fname = self.google_path + 'log.txt'
        self.sql_fname = self.google_path + 'billing.sqlite'
        self.logger = create_logger(self.logger_fname, 'DEBUG')
        if not isfile(self.sql_fname):
            self.logger.info("db file doesn't exist!")
            input("Something has gone very wrong! db file doesn't exist! Press enter to exit")
            exit(1)

        self.logger.info("Run Time Properties are initialized")


class Tenant:
    def __init__(self, email: str = '', name: str = '', charge_room: str = '', charge_internet: str = '',
                 charge_gas: str = '', charge_electricity: str = '', charge_other: str = '', charge_total: str = ''):
        self.email = email
        self.name = name
        self.charge_room = charge_room
        self.charge_internet = charge_internet
        self.charge_gas = charge_gas
        self.charge_electricity = charge_electricity
        self.charge_other = charge_other
        self.charge_total = charge_total
        self.pdf = ''
        self.email = None


class TenantList:
    def __init__(self):
        self.tennant_list: List[Tenant] = []


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


def get_bill_date():
    m = input("Please input month, leave blank for current:\n")
    y = input("Please input year, leave blank for current:\n")
    if m == '':
        m = calendar.month_name[datetime.date.today().month]
        m = m.lower()

    if y == '':
        y = datetime.date.today().year

    return y, m
