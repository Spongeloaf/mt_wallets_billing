# imports and init
import billing_lib as blib
import sql_interface
import pdf_compositor
import bill_mailer
import menus

# init
rtp = blib.RunTimeParams()
sql = sql_interface.SqlInterface(rtp)
pdf = pdf_compositor.PdfCompositor(rtp)
mail = bill_mailer.Mailer(rtp)

main = menus.MenuStructure(rtp, sql, pdf, mail)

# run
main()
