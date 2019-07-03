from billing_lib import *
import sqlinterface
import mailer
import pdfcompositor


# init
rtp = RunTimeParams()
tl = TenantList()
sql = sqlinterface.SqlInterface()
mail = mailer.Mailer()
pdf = pdfcompositor.PdfCompositor()

# run
sql.get_tenant_list(tl)
for tenant in tl.tennant_list:
    if rtp.prepare:
        sql.get_utility_bills(tenant)
    else:
        # TODO: we're not preparing new bills, we must be sending or composing existing ones. Handle this case!
        pass

    if rtp.compose:
        pdf.compose_bill(tenant)
    else:
        # TODO: handle this case!
        pass

    if rtp.send:
        mail.compose_email(tenant)
        mail.send_email(tenant)
    else:
        # TODO: handle this case!
        pass
