import wikipedia as wiki
import pprint as pp
from colorama import Fore, Back, Style, init
import time
from time import strftime, ctime, gmtime
import datetime
init()

session_count = 0
result = ''
category = ''
greeting = ''


def init_query():
    global greeting
    global session_count
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    iq_id = str(id(init_query))
    if session_count == 0:
        greeting = 'Welcome to Wikipedia. What would you like to search? '
    elif session_count == 1:
        greeting = 'I see you have come back for a 2nd time. What would you like to search? '
    elif session_count == 2:
        greeting = 'Back again and still no answer? Maybe doing it just for fun!?! Try another search: '
    elif session_count == 3:
        greeting = 'Third times the charm or so they say. Let\'s give it another shot, search here: '
    elif session_count == 4:
        greeting = 'Aloha to you. What would you like to learn about? '

    user_request = input(greeting)
    global result
    result = wiki.page(user_request)
    global category
    category = result.categories
    session_count = session_count + 1
    print('Searching, please wait...')
    pp.pprint(result.summary)
    # print(f'{timestamp} | {vc_id} | User Populated all records')
    # session_note = Fore.RED + f'You have completed query #{session_count}' + Style.RESET_ALL
    # print(session_note)
    print(Fore.RED + f'{timestamp} | def ID {iq_id} | User completed query #{session_count}' + Style.RESET_ALL)
    follow_up = input(str('Was this information helpful? (y or n) '))
    if follow_up == 'y':
        print('Have a great day!')
    else:
        auto_suggest()


def auto_suggest():
    print('Here are related categories:')
    category_response = Fore.LIGHTBLUE_EX + str(category) + Style.RESET_ALL
    print(category_response)
    proceed = input('Would you like to search again? (y or n) ')
    if proceed == 'y':
        init_query()
    else:
        end_session()


def end_session():
    print(f'You have searched Wikiipedia {session_count} time(s). Have a great day!')


init_query()






