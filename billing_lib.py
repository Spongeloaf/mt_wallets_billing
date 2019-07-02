from typing import List


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

    def get_billing_month(self):
        """ Get a string from the cmd line indicating which month to bill
        Assume current year, unless otherwise specified. """

    def init_sql(self):
        """ Setup SQL cursor """
        pass

    def get_tenant_info(self):
        """ retrieve list of active tenants for month specified """
        pass

    def get_bills(self):
        """ Pass tenant list to SQL, return bills for month specified """
        pass


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

    full_path = path + '\\software_dev\\mtWallets_billing\\'

    return full_path


def format_values(value):
    """ takes a value and ensures it gets rounded if needed and converted to a string. """

    if value is float:
        value = round(value, 2)

    return str(value)
