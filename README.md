# Introduction
mt_wallets_billing is a utility for landlords to automatically generate and email rent bills to their tenants. It utilizes SQL for data storage, and comes with a not-at-all stylish command line interface. 

The program follows the data/model/view design philosophy: The components are well encapsulated and it would be easy to load the the libraries into a totally new interface, such as a web server. The data is stored in an sqlite db, the model for the data is contained within billing_lib.py, sql_interface.py, pdf_compositor.py, and bill_mailer.py. Finallym, the view is provided by menus.py and menu_prompts.py.  

# How do I use it?
The included CLI is a basic text menu like this:
 
 ![Title Screen](https://i.imgur.com/J4B3Q2s.png)

These menus guide you through the process of marking the previous bills as paid, adding new utility bills, and then turning those into tenant bills which will be emailed to your tenants.

Then menus are simply made, but designed for fast and easy use. In every menu, you may simply press enter to continue, or enter 0, q, or * to abort, in addition to whichever numbered options you are presented with.

A user will always begin each task with entering an integer for the month and year. Entering a blank line will cause the program to use the current month/year. The month and year are used by all processes to automatically select tenants from the db, and pick which bills apply to them.

# Dependencies
This project is dependant on a number of 3rd party libraries:
* colorama
* comtypes
* config parser
* docx mailmerge

The project also uses a number of 1st party libraries such as *smtplib*, and *typing*. You will also need an email account with some mail provider.

# Limitations & Liabilities
This code is completely unlicensed. Using it may harm your PC, or cause hair loss. If you try to use this program and your computer experiences spontaneous combustion or spiritual awakening, seek the help of a certififed professional.

As of this moment, OAuth2 is not yet implemented. 

#### THIS SOFTWARE IS NOT SECURE.  
#### The password for your email account is stored in a config file, in plain text. Use a throwaway email account not tied to any online services for this software. 
#### USE THIS SOFTWARE ENTIRELY AT YOUR OWN RISK.

# Deployment
This code has not been tested on any operating system besides Windows 10. It does not (yet?) have an installer, but instead seeks out config files on google drive by parsing the google drive config files in the windows user's appdata folder. You will need to mdoify this to suit your own needs. Or modify your computer to suit the programs needs. See the RunTimeProperties class in billing_lib.py, and the Limitations & Liabilities section.

# How does it work?
As previously mentioned, this program is well encapsulated. The *RunTimeParameter* class provides all of the necessary user data and config settings for each module. The modules are *SqlInterface*, *PdfCompositor*, and *BillMailer*.
To initialize the software, all you need is:
```
# pretend this line is import statments

rtp = billing_lib.RunTimeParams()
sql = sql_interface.SqlInterface(rtp)
pdf = pdf_compositor.PdfCompositor(rtp)
mail = bill_mailer.Mailer(rtp)
```

Now each module can operate on its own, and they all have references to rtp. Every function called modifies the lists of tenants, utiltiy_bills, or tenant_bills that rtp holds. 

The CLUI is it's own class that constructs rtp, sql, pdf, and mail, and then calls their various functions in order, as laid out by the member functions in the menu class.

Therefore, building a new menu iss as simple as adding some more functions and print statements to the menu class. Similarly, this software could be integrated with another interface, such as a webserver, just by importing the four main .py files, billing_lib, sql_interface, pdf_compositor, and bill_mailer.

# What do I do with the sqlite DB?
There isn't yet a facility to add tenants from the CLUI. You'll need to use something like sqlite studio to open the DB and add tenants on your own. If the bill_tenant_0 flag is True in the settings file, the tenant in the database whose id number is zero will be treated like a live-in landlord, and will not be sent a bill, but will be included the utility bill division.
