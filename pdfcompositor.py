from billing_lib import *
from mailmerge import MailMerge
from billing_lib import RunTimeParams, Tenant
from typing import List
import calendar
import datetime
import comtypes.client


class PdfCompositor:
    def __init__(self, rtp: RunTimeParams):
        self.rtp = rtp
        self.logger_fname = rtp.google_path + 'pdf_log.txt'
        self.logger = create_logger(self.logger_fname, self.rtp.pdf_log_level, "pdf_log")

    def format_docx_name(self, t: Tenant, extension: str):
        return "{}s rent for {} {}.{}".format(t.name, calendar.month_name[self.rtp.month], self.rtp.year, extension)

    def compose_bills(self, tl: List[Tenant]):
        """ Compose a single bill for a tenant, save it to disk.
        returns a string containing the path to the saved file. """
        for t in tl:
            t_bill = MailMerge(self.rtp.pdf_docx_template)
            t_bill.merge(name=format_values(t.name),
                         month_year=format_values("{} {}".format(calendar.month_name[self.rtp.month], self.rtp.year)),
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

            docx = self.rtp.google_path + self.format_docx_name(t, "docx")
            t_bill.write(docx)
            t.docx = docx
            self.logger.debug("Created docx file: {}".format(docx))

    def docx_to_pdf(self, tl: List[Tenant]):
        """ Converts the docx files in a tenant list to pdf """
        wdFormatPDF = 17
        word = comtypes.client.CreateObject('Word.Application')
        for t in tl:
            docx = t.docx
            pdf = self.rtp.google_path + self.format_docx_name(t, "pdf")
            doc = word.Documents.Open(docx)
            doc.SaveAs(pdf, FileFormat=wdFormatPDF)
            doc.Close()
            self.logger.debug("Created pdf file: {}".format(pdf))
        word.Quit()
