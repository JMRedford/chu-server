from flask import Flask, request
app = Flask(__name__)

games = {}


class Game:
    def __init__(self):
        self.players = []
        self.next_move = [0, '']

    def add_player(self, user):
        if len(self.players) < 2:
            self.players.append(user)

    def full(self):
        return len(self.players) > 1

    def waiting(self):
        return len(self.players) == 1


def game_ready():
    for user, game in games:
        if game.waiting():
            return True
    return False


def join_game(user_name):
    global games

    if user_name not in games.keys():
        for user, game in games.items():
            if not game.full():
                game.add_player(user_name)
                games[user_name] = game
                return "joined game"
        # make a new game
        new_game = Game()
        new_game.add_player(user_name)
        games[user_name] = new_game
        return "made a new game with player " + user_name

    else:
        return "ERROR: username is already associated with a game"


@app.route('/join', methods=['GET', 'POST'])
def join_route():
    if request.method == 'POST':
        form_data = request.get_json()
        try:
            if form_data['key'] == 'chu-client':
                if 'user' in form_data.keys():
                    return join_game(form_data['user'])
                else:
                    return "ERROR: user name not provided ('user' key missing in POST data)"
            else:
                return "ERROR: invalid client key"
        except KeyError:
            return "ERROR: missing client key"
        except TypeError:
            return "ERROR: missing form data"

    else:
        if game_ready():
            return "ready to play"
        else:
            return "waiting on player"


@app.route('/game/<user_name>', methods=['GET', 'POST'])
def game_route(user_name):
    if user_name in games.keys():
        curr_game = games[user_name]
        which_player = curr_game.players.index(user_name)

        if request.method == 'POST': #put your move on the game
            form_data = request.get_json()
            try:
                move = form_data['move']
            except KeyError:
                return "ERROR: missing key 'move' in form data"

            try:
                if form_data['key'] == 'chu-client':
                    if curr_game.next_move[0] == which_player:
                        if curr_game.next_move[1] == '':
                            curr_game.next_move[1] = move
                            return "Submitted move " + move
                        else:
                            return "waiting on other player to read your last move"
                    else:
                        if curr_game.next_move[1] == '':
                            return "waiting on other player to move"
                        else:
                            return "please read other player's move before moving"
                else:
                    return "ERROR: invalid client key"
            except KeyError:
                return "ERROR: missing client key"

        else: #read your opponent's move
            next_move = curr_game.next_move
            if which_player != next_move[0]:
                if next_move[1] == '':
                    return "waiting on opponent to make their move"
                else:
                    the_move = next_move[1]
                    curr_game.next_move = [(next_move[0] + 1) % 2, '']
                    return "move: " + the_move
            else:
                if next_move[1] == '':
                    return "your turn to move"
                else:
                    return "waiting on opponent to read your last move"
    else:
        return "ERROR: game does not exist"