import billing_lib as blib
from sqlinterface import SqlInterface
from pdfcompositor import PdfCompositor
from mailer import Mailer

i = input
p = print

p("MT Wallets Billing Software")
p("In all numeric menus, you can just press enter for the first option.")
p("Please Select one of the following options:\n1: Add utility bill\n2: Mark tenant bills as paid\n3: Prepare tenant bills")
select = int(i(""))
p(type(select))
if select == '':
    select = 1


