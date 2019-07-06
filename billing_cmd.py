import billing_lib as blib
from sqlinterface import SqlInterface
from pdfcompositor import PdfCompositor
from mailer import Mailer

main = blib.Menu("Hello Dave", [blib.func_1, blib.func_2, blib.func_3], loop=True)
main.run()
