
import datetime
import time
import itertools
from colorama import Fore, Back, Style, init
init()


def win(current_game):

    def all_same(l):
        if l.count(l[0]) == len(l) and l[0] != 0:
            return True
        else:
            return False

    # Horizontal Check
    for row in game:
        print(row)
        if all_same(row):
            print(f'Player {row[0]} is the winner horizontally!')
            return True

    #  Vertical Check
    for col in range(len(game)):
        check = []
        for row in game:
            check.append(row[col])
        if all_same(check):
            print(f'Player {check[0]} is the winner vertically')
            return True

    # Diagonal Check
    diags = []
    for ix in range(len(game)):
        diags.append(game[ix][ix])
    if all_same(diags):
        print(f'Player {diags[0]} is the winner diagonally')
        return True

    # Reverse Diagonal Check
    diags = []
    for col, row in enumerate(reversed(range(len(game)))):
        diags.append(game[row][col])
    if all_same(diags):
        print(f'Player {diags[0]} is the winner reverse diagonally')
        return True

    return False


def display_game(game_map, player=0, row=0, column=0, just_display=False):
    timestamp = datetime.datetime.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    dg_id = str(id(display_game))
    try:
        if game_map[row][column] != 0:
            print('This position is occupied! Choose another!')
            return game_map, False
        print('   ' + '  '.join([str(i) for i in range(len(game_map))]))
        if not just_display:
            game_map[row][column] = player


        for count, row in enumerate(game_map):
            colored_row = ''
            for item in row:
                if item == 0:
                    colored_row += '   '
                elif item == 1:
                    colored_row += Fore.GREEN + ' X ' + Style.RESET_ALL
                elif item == 2:
                    colored_row += Fore.MAGENTA + ' O ' + Style.RESET_ALL
            print(count, colored_row)

        return game_map, True

    except IndexError as e:
        print('DESIGN ERROR DETECTED: make sure row/column entered as 0 1 or 2', e)
        return game_map, False

    except Exception as e:
        print(timestamp, ' | ', 'def ID:', dg_id, ' | ', 'DESIGN ERROR DETECTED', ' | ', 'Exception:',e)
        return game_map, False


play = True
players = [1, 2]
while play:

    game_size = int(input('What size game board would you like? '))
    game = [[0 for i in range(game_size)] for i in range(game_size)]
    game_one = False
    game, _ = display_game(game, just_display=True)
    player_choice = itertools.cycle([1, 2])
    while not game_one:
        current_player = next(player_choice)
        print(f'Player: {current_player}')
        played = False

        while not played:
            column_choice = int(input('What column do you want to play?:  '))
            row_choice = int(input('What row do you want to play?:  '))
            game, played = display_game(game, current_player,row_choice, column_choice)

        if win(game):
            game_one = True
            again = input('The game is over, would you like to play again? (y/n) ')
            if again.lower() == 'y':
                print('restarting')
            elif again.lower() == 'n':
                print('Have a good day!')
                play = False
            else:
                print('Not a valid answer, see you later!')
                play = False







