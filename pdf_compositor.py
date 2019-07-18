from billing_lib import *
from mailmerge import MailMerge
from billing_lib import RunTimeParams, Tenant
from typing import List
import calendar
import datetime
import comtypes.client

from genericpath import isfile
from os import remove


class PdfCompositor:
    def __init__(self, rtp: RunTimeParams):
        self.rtp = rtp
        self.logger_fname = rtp.google_path + 'pdf_log.txt'
        self.logger = create_logger(self.logger_fname, self.rtp.pdf_log_level, "pdf_log")

    def __format_file_name(self, t: TenantBill, extension: str):
        return "{}s rent for {} {}.{}".format(t.tenant_name, self.rtp.month_str, self.rtp.year, extension)

    def tenant_bills_to_docx(self):
        """ Compose a single bill for a tenant_id, save it to disk.
        returns a string containing the path to the saved file. """
        for t in self.rtp.tbl:
            if not self.rtp.bill_tenant_0:
                if t.tenant_id == 0:
                    continue
            t_bill = MailMerge(self.rtp.pdf_docx_template)
            t_bill.merge(name=format_values(t.tenant_name),
                         month_year=format_values("{} {}".format(self.rtp.month_str, self.rtp.year)),
                         total=format_values(t.charge_total),
                         date=format_values(datetime.datetime.now().strftime('%Y %B %d')),
                         room_rate=format_values(t.charge_room),
                         gas=format_values(t.charge_gas),
                         internet=format_values(t.charge_internet),
                         electricity=format_values(t.charge_electricity),
                         other=format_values(t.charge_other),
                         memo_gas=format_values(t.memo_gas),
                         memo_internet=format_values(t.memo_internet),
                         memo_electricity=format_values(t.memo_electricity),
                         memo_other=format_values(t.memo_other),
                         )
            docx = self.rtp.google_path + "bills\\" + self.__format_file_name(t, "docx")
            if isfile(docx):
                remove(docx)
            t_bill.write(docx)
            t.docx_long_name = docx
            self.logger.debug("Created docx_long_name file: {}".format(docx))

    def docx_to_pdf(self,):
        """ Converts the docx_long_name files in a tenant_id list to pdf_long_name """
        wd_format_pdf = 17
        word = comtypes.client.CreateObject('Word.Application')
        for tb in self.rtp.tbl:
            if not self.rtp.bill_tenant_0:
                if tb.tenant_id == 0:
                    continue
            docx = tb.docx_long_name
            tb.pdf_long_name = self.rtp.google_path + "bills\\" + self.__format_file_name(tb, "pdf")
            tb.pdf_short_name = self.__format_file_name(tb, "pdf")
            doc = word.Documents.Open(docx)
            doc.SaveAs(tb.pdf_long_name, FileFormat=wd_format_pdf)
            doc.Close()
            self.logger.debug("Created pdf_long_name file: {}".format(tb.pdf_short_name))
        word.Quit()
