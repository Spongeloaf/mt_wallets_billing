import textwrap

main_loop_begin = textwrap.dedent("""\
MTWallets Billing Suite
Type a number and press enter to navigate. Just pressing enter selects option 1.
1: Tenant Bill Receivables
2: Add utility bills
3: Prepare tenant_id bills
0: Abort""")

prepare_tenant_bills = textwrap.dedent("""\
Would you like to generate new tenant_id bills?
1: Yes
2: No - Skip and use existing tenant_id bills.
0: Abort""")

prepare_tenant_bills_end = textwrap.dedent("""\
Would you like to prepare another bill?
1: Yes
2: No - Return to main menu
0: Abort""")

get_billing_year = textwrap.dedent("""\
Please type an integer for the year. Alternatively, just press enter to select the current year.
You may enter 0, q, or * to exit.""")

get_billing_month = textwrap.dedent("""\
Please type an integer for the month. Alternatively, just press enter to select the current month.
You may enter 0, q, or * to exit.""")

check_tenant_bill_list = textwrap.dedent("""\
Review the tenant_id list and billing date. 
1: Accept
0: Abort""")

prepare_pdf = textwrap.dedent("""\
Would you like to prepare DOCX and/or PDF files of the tenant_id bills?
1: Prepare PDFs
2: Prepare DOCX only
3: No - Skip and use existing files
0: Abort""")

prepare_email = textwrap.dedent("""\
Would you like to compose and send emails?
1: Compose and send
2: Compose and send all to landlord""")

utility_bill_type = textwrap.dedent("""\
Add utility bills for billing date {} {}.
Please choose a type of bill:
1: Electricity
2: Gas
3: Internet
4: Other""")

utility_bill_amount = textwrap.dedent("""\
Please enter an amount: """)

utility_bill_memo = textwrap.dedent("""\
Enter a memo if you wish: """)

utility_bill_end = textwrap.dedent("""\
Would you like to add another utility bill?
1: Yes
0: No - Return to main menu
""")

check_utility_bill_list = textwrap.dedent("""\
Review the utility bill list and billing date. 
1: Accept
0: Abort""")

dummy = textwrap.dedent("""\
""")
