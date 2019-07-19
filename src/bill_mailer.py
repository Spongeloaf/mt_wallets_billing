from src.billing_lib import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time

class Mailer:
    def __init__(self, rtp: RunTimeParams):
        self.rtp = rtp
        self.logger_fname = rtp.google_path + 'mail_log.txt'
        self.logger = create_logger(self.logger_fname, "DEBUG", "mail_log")

        # init mail server
        self.mail_server = smtplib.SMTP(self.rtp.mail_server, self.rtp.mail_port)
        self.mail_server.starttls()

    def compose_email(self):
        """ Composes an email_addr for each tenant_id """
        for tb in self.rtp.tbl:
            if not self.rtp.bill_tenant_0:
                if tb.tenant_id == 0:
                    continue
            tb.email_msg = MIMEMultipart()
            # Do we need this?
            tb.email_msg['From'] = self.rtp.mail_user
            tb.email_msg['To'] = tb.email_addr
            tb.email_msg['Subject'] = "Rent for {} {}".format(self.rtp.month_str, self.rtp.year)
            tb.email_msg.attach(MIMEText(self.rtp.mail_msg, 'plain'))
            try:
                attachment = open(tb.pdf_long_name, "rb")
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', "attachment; filename= %s" % tb.pdf_short_name)
                tb.email_msg.attach(part)
            except TypeError:
                self.logger.critical("Invalid path to attachment in mail.compose_mail: {}".format(tb.pdf_short_name))
                self.rtp.critical_stop("stopped by TypeError in mail.compose_mail")
            except ValueError:
                self.logger.critical("ValueError in mail.compose_mail: {}".format(tb.pdf_short_name))
                self.rtp.critical_stop("stopped by ValueError in mail.compose_mail")

    def send_email(self):
        """ Sends an email_addr to each tenant_id """
        self.mail_server.login(self.rtp.mail_user, self.rtp.mail_pswd)
        for tb in self.rtp.tbl:
            if not self.rtp.bill_tenant_0:
                if tb.tenant_id == 0:
                    continue
            body = tb.email_msg.as_string()
            self.mail_server.sendmail(self.rtp.mail_user, tb.email_addr, body)
            time.sleep(1)
        self.mail_server.quit()

    def email_to_landord(self):
        """ Changes all email addresses to the address associated with tenant_id 0 """
        email = ''
        for tb in self.rtp.tbl:
            if tb.tenant_id == 0:
                email = tb.email_addr

        if email == '':
            self.rtp.critical_stop("Failed to find email address match in mail.email_to_landlord()")

        for tb in self.rtp.tbl:
            tb.email_addr = email
