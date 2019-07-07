import billing_lib as blib
from sqlinterface import SqlInterface
from pdfcompositor import PdfCompositor
from mailer import Mailer

main = blib.Menu("Hello Dave. please choose:\n1 a thing\n2 another thing\n3 a final thing", [blib.func_1, blib.func_2, blib.func_3], loop=True, loop_prompt="Would you like to know more?")
main.run()
