import textwrap

main = textwrap.dedent("""\
MTWallets Billing Suite
Type a number and press enter to navigate. Just pressing enter selects option 1.
1: Tenant Bill Receivables
2: Add utility bills
3: Prepare tenant bills""")

prepare_tenant_bills = textwrap.dedent("""\
Prepare tenant bills.""")

prepare_tenant_bills_2 = textwrap.dedent("""\
Would you like to prepare another bill?
1: yes
2: no""")

get_billing_year = textwrap.dedent("""\
Please type in a year, or just press enter to select the current year.""")

check_tenant_bill_list = textwrap.dedent("""\
Review the tenant list and below and choose 1 to accept, 2 to abort.""")