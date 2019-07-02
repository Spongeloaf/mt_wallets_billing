from billing_lib import *
import mailer
import pdfcompositor


# init
tl = TenantList()
mail = mailer.Mailer()
pdf = pdfcompositor.PdfCompositor()

# run
tl.init_sql()
tl.get_tenant_info()
tl.get_bills()
for tenant in tl.tennant_list:
    pdf.compose_bill(tenant)
    mail.compose_email(tenant)
    mail.send_email(tenant)