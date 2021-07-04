import gspread

####################################################################
# USER CONFIGURATION #
my_email = ''
my_password = ''
spreadsheet_url = ''

####################################################################

gc = gspread.login(my_email, my_password)
sh = gc.open_by_url(spreadsheet_url)


def get_sheets():
    # PRINTS LIST OF WORKSHEETS LOCATED IN THE SPREADSHEET
    worksheet_list = sh.worksheets()
    print(worksheet_list)


get_sheets()