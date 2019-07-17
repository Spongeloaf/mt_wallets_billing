from billing_lib import *
from typing import List
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class Mailer:
    def __init__(self, rtp: RunTimeParams):
        self.rtp = rtp
        self.logger_fname = rtp.google_path + 'mail_log.txt'
        self.logger = create_logger(self.logger_fname, "DEBUG", "mail_log")

        # init mail server
        self.mail_server = smtplib.SMTP(self.rtp.mail_server, self.rtp.mail_port)
        self.mail_server.starttls()

    def compose_email(self):
        """ Composes an email_addr for each tenant """
        for t in self.rtp.tl:
            if not self.rtp.bill_tenant_0:
                if t.id == 0:
                    continue
            t.email_msg = MIMEMultipart()
            # Do we need this?
            t.email_msg['From'] = self.rtp.mail_user
            t.email_msg['To'] = t.email_addr
            t.email_msg['Subject'] = "Rent for {} {}".format(self.rtp.month, self.rtp.year)
            t.email_msg.attach(MIMEText(self.rtp.mail_msg, 'plain'))
            try:
                attachment = open(t.pdf, "rb")
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', "attachment; filename= %s" % t.pdf_short_name)
                t.email_msg.attach(part)
            except TypeError:
                self.logger.critical("Invalid path to attachment in mail.compose_mail: {}".format(t.pdf))
                self.rtp.critical_stop("stopped by TypeError in mail.compose_mail")
            except ValueError:
                self.logger.critical("ValueError in mail.compose_mail: {}".format(t.pdf))
                self.rtp.critical_stop("stopped by ValueError in mail.compose_mail")

    def send_email(self):
        """ Sends an email_addr to each tenant """
        self.mail_server.login(self.rtp.mail_user, self.rtp.mail_pswd)
        for t in self.rtp.tl:
            if not self.rtp.bill_tenant_0:
                if t.id == 0:
                    continue
            body = t.email_msg.as_string()
            self.mail_server.sendmail(self.rtp.mail_user, t.email_addr, body)
        self.mail_server.quit()

    def email_to_landord(self):
        """ Changes all email addresses to the address associated with tenant 0 """
        email = ''
        for t in self.rtp.tl:
            if t.id == 0:
                email = t.email_addr

        if email == '':
            self.rtp.critical_stop("Failed to find email address match in mail.email_to_landlord()")

        for t in self.rtp.tl:
            t.email_addr = email
