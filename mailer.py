""" Contains all the code for mailing bills """
from billing_lib import Tenant

class Mailer:
    def __init__(self):
        pass

    def compose_email(self, tenant: Tenant):
        """ Composes an email and returns it as an object """

        ##### OLD CODE FOR EDUCATIONAL PURPOSES ONLY! ########
        fromaddr = "MTWallets@outlook.com"
        toaddr = str(tenantEmail)

        msg = MIMEMultipart()

        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Rent bill for {}".format(billingDate.strftime('%B %Y'))

        body = "Please see the attached bill for {} rent at 3G Crestlea Crescent".format(
            billingDate.strftime('%B %Y'))

        msg.attach(MIMEText(body, 'plain'))

        filename = "{}s Rent for {}.docx".format(format_values(mergeName), mergeBilling)
        attachment = open(filename, "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        msg.attach(part)

        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(fromaddr, "MTnoreply430")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()

    def send_email(self, tenant: Tenant):
        """ Send an email """
        pass
