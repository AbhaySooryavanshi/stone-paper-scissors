import tkinter as tk
import random
import json
import os
import threading

from websockets.sync.client import connect


# ============================================================
# ONLINE SERVER
# ============================================================

SERVER_URL = "ws://127.0.0.1:5001"

network_client = None
online_connected = False

online_player_number = None
online_room_id = None


# ============================================================
# GAME DATA
# ============================================================

choices = ["Stone", "Paper", "Scissors"]

winning_combinations = {
    "Stone": "Scissors",
    "Paper": "Stone",
    "Scissors": "Paper"
}


# ============================================================
# PLAYER PROFILES
# ============================================================

PLAYERS_FILE = "players.json"

players = {}
current_player = ""


def load_players():

    global players

    if os.path.exists(PLAYERS_FILE):

        try:

            with open(
                PLAYERS_FILE,
                "r"
            ) as file:

                players = json.load(file)

        except:

            players = {}

    else:

        players = {}


def save_players():

    with open(
        PLAYERS_FILE,
        "w"
    ) as file:

        json.dump(
            players,
            file,
            indent=4
        )


def create_player(name):

    global current_player

    current_player = name

    if name not in players:

        players[name] = {
            "wins": 0,
            "losses": 0,
            "draws": 0
        }

        save_players()


# ============================================================
# CONNECTION
# ============================================================

def connect_online():

    global network_client
    global online_connected

    try:

        network_client = connect(
            SERVER_URL,
            proxy=None,
            open_timeout=5
        )

        online_connected = True

        print(
            "WebSocket connected successfully!"
        )

        return True

    except Exception as e:

        print(
            "Connection error:",
            e
        )

        network_client = None
        online_connected = False

        return False


# ============================================================
# SEND MESSAGE
# ============================================================

def send_online(message):

    global network_client

    if not online_connected or network_client is None:

        print(
            "Not connected to server."
        )

        return False

    try:

        network_client.send(message)

        print(
            "Sent:",
            message
        )

        return True

    except Exception as e:

        print(
            "Send error:",
            e
        )

        return False


# ============================================================
# RECEIVE MESSAGE
# ============================================================

def receive_online():

    global network_client
    global online_connected

    try:

        while online_connected and network_client is not None:

            message = network_client.recv()

            print(
                "Received:",
                message
            )

            window.after(
                0,
                handle_online_message,
                message
            )

    except Exception as e:

        print(
            "Receive error:",
            e
        )

    finally:

        online_connected = False


# ============================================================
# HANDLE SERVER MESSAGE
# ============================================================

def handle_online_message(message):

    global online_room_id
    global online_player_number

    if message.startswith("ROOM:"):

        online_room_id = message.split(
            ":",
            1
        )[1]

        online_player_number = 1

        room_label.config(
            text=f"Room ID: {online_room_id}"
        )

        online_status_label.config(
            text="Room created. Waiting for Player 2..."
        )


    elif message == "JOINED":

        online_player_number = 2

        online_status_label.config(
            text="Joined room successfully!"
        )

        show_online_mode()


    elif message == "PLAYER2_JOINED":

        online_status_label.config(
            text="Player 2 joined! Choose match mode."
        )

        show_online_mode()


    elif message == "REMATCH_START":

        online_score_label.config(
            text="Score: 0 - 0"
        )

        online_result_label.config(
            text="Rematch started!"
        )


    elif message.startswith("ERROR:"):

        error = message.split(
            ":",
            1
        )[1]

        if error == "ROOM_NOT_FOUND":

            online_status_label.config(
                text="Room not found!"
            )

        elif error == "ROOM_FULL":

            online_status_label.config(
                text="Room is full!"
            )


    elif message.startswith("RESULT:"):

        data = message.split(":")

        if len(data) >= 6:

            choice1 = data[1]
            choice2 = data[2]
            result = data[3]

            score1 = data[4]
            score2 = data[5]

            match_over = False

            if len(data) >= 7:

                match_over = data[6] == "True"

            online_score_label.config(
                text=f"Score: {score1} - {score2}"
            )

            if online_player_number == 1:

                my_choice = choice1
                opponent_choice = choice2

            else:

                my_choice = choice2
                opponent_choice = choice1


            if result == "Draw":

                online_result_label.config(
                    text=f"Draw!\nBoth chose {my_choice}"
                )

            elif (
                result == "Player1"
                and online_player_number == 1
            ) or (
                result == "Player2"
                and online_player_number == 2
            ):

                online_result_label.config(
                    text=f"You Win!\n"
                         f"You: {my_choice}\n"
                         f"Opponent: {opponent_choice}"
                )

            else:

                online_result_label.config(
                    text=f"You Lose!\n"
                         f"You: {my_choice}\n"
                         f"Opponent: {opponent_choice}"
                )


            if match_over:

                online_result_label.config(
                    text=online_result_label.cget(
                        "text"
                    ) + "\n\nMATCH OVER!"
                )


# ============================================================
# OFFLINE GAME
# ============================================================

game_mode = "computer"
match_mode = "BO3"

player_score = 0
computer_score = 0

target_score = 2


def get_target_score():

    global target_score

    if match_mode == "BO3":

        target_score = 2

    elif match_mode == "BO5":

        target_score = 3

    else:

        target_score = None


def computer_choice():

    return random.choice(
        choices
    )


def get_result(player, computer):

    if player == computer:

        return "Draw"

    if winning_combinations[player] == computer:

        return "Win"

    return "Lose"


def update_profile(result):

    if current_player == "":
        return

    if current_player not in players:
        return

    if result == "Win":

        players[current_player]["wins"] += 1

    elif result == "Lose":

        players[current_player]["losses"] += 1

    else:

        players[current_player]["draws"] += 1

    save_players()


def play_offline(player_choice):

    global player_score
    global computer_score

    if game_mode == "pvp":

        return

    computer = computer_choice()

    result = get_result(
        player_choice,
        computer
    )

    if result == "Win":

        player_score += 1

    elif result == "Lose":

        computer_score += 1


    if match_mode == "Unlimited":

        result_label.config(
            text=f"You: {player_choice}\n"
                 f"Computer: {computer}\n\n"
                 f"{result}"
        )

        score_label.config(
            text=f"Score: {player_score} - {computer_score}"
        )

        update_profile(result)

        return


    score_label.config(
        text=f"Score: {player_score} - {computer_score}"
    )


    if (
        player_score >= target_score
        or
        computer_score >= target_score
    ):

        if player_score > computer_score:

            final_result = "You won the match!"

        else:

            final_result = "Computer won the match!"


        result_label.config(
            text=f"You: {player_choice}\n"
                 f"Computer: {computer}\n\n"
                 f"{result}\n\n"
                 f"{final_result}"
        )

    else:

        result_label.config(
            text=f"You: {player_choice}\n"
                 f"Computer: {computer}\n\n"
                 f"{result}"
        )


def play_pvp(player_choice):

    pass


# ============================================================
# ONLINE GAME
# ============================================================

def choose_online(choice):

    if not online_connected:

        online_result_label.config(
            text="Not connected to server!"
        )

        return

    if send_online(
        f"CHOICE:{choice}"
    ):

        online_result_label.config(
            text=f"You chose {choice}\nWaiting for opponent..."
        )


# ============================================================
# GUI
# ============================================================

window = tk.Tk()

window.title(
    "Stone Paper Scissors"
)

window.geometry(
    "700x600"
)

window.resizable(
    False,
    False
)


# ============================================================
# HELPERS
# ============================================================

def hide_all():

    frames = [
        splash_frame,
        home_frame,
        name_frame,
        mode_frame,
        game_frame,
        profile_frame,
        online_frame,
        online_mode_frame,
        online_game_frame,
        match_mode_frame
    ]

    for frame in frames:

        frame.pack_forget()


# ============================================================
# SPLASH SCREEN
# ============================================================

splash_frame = tk.Frame(
    window
)

tk.Label(
    splash_frame,
    text="STONE\nPAPER\nSCISSORS",
    font=("Arial", 32, "bold")
).pack(
    pady=180
)


# ============================================================
# HOME
# ============================================================

home_frame = tk.Frame(
    window
)

tk.Label(
    home_frame,
    text="STONE PAPER SCISSORS",
    font=("Arial", 28, "bold")
).pack(
    pady=80
)


tk.Button(
    home_frame,
    text="PLAY",
    font=("Arial", 18),
    width=15,
    command=lambda: show_name()
).pack(
    pady=10
)


tk.Button(
    home_frame,
    text="PROFILE",
    font=("Arial", 18),
    width=15,
    command=lambda: show_profile()
).pack(
    pady=10
)


# ============================================================
# NAME SCREEN
# ============================================================

name_frame = tk.Frame(
    window
)

tk.Label(
    name_frame,
    text="Enter your name",
    font=("Arial", 22, "bold")
).pack(
    pady=80
)

name_entry = tk.Entry(
    name_frame,
    font=("Arial", 18)
)

name_entry.pack(
    pady=10
)


def start_name():

    name = name_entry.get().strip()

    if name == "":
        return

    create_player(name)

    show_mode()


tk.Button(
    name_frame,
    text="CONTINUE",
    font=("Arial", 16),
    command=start_name
).pack(
    pady=20
)


# ============================================================
# MODE SCREEN
# ============================================================

mode_frame = tk.Frame(
    window
)

tk.Label(
    mode_frame,
    text="Choose Game Mode",
    font=("Arial", 24, "bold")
).pack(
    pady=50
)


def set_game_mode(mode):

    global game_mode

    game_mode = mode

    if mode == "online":

        show_online()

    else:

        show_match_mode()


tk.Button(
    mode_frame,
    text="VS COMPUTER",
    font=("Arial", 16),
    width=18,
    command=lambda: set_game_mode("computer")
).pack(
    pady=10
)


tk.Button(
    mode_frame,
    text="2 PLAYER",
    font=("Arial", 16),
    width=18,
    command=lambda: set_game_mode("pvp")
).pack(
    pady=10
)


tk.Button(
    mode_frame,
    text="ONLINE",
    font=("Arial", 16),
    width=18,
    command=lambda: set_game_mode("online")
).pack(
    pady=10
)


# ============================================================
# MATCH MODE
# ============================================================

def show_match_mode():

    hide_all()

    match_mode_frame.pack(
        fill="both",
        expand=True
    )


match_mode_frame = tk.Frame(
    window
)

tk.Label(
    match_mode_frame,
    text="Choose Match",
    font=("Arial", 24, "bold")
).pack(
    pady=50
)


def set_match_mode(mode):

    global match_mode
    global player_score
    global computer_score

    match_mode = mode

    player_score = 0
    computer_score = 0

    get_target_score()

    show_game()


tk.Button(
    match_mode_frame,
    text="BEST OF 3",
    font=("Arial", 16),
    width=18,
    command=lambda: set_match_mode("BO3")
).pack(
    pady=10
)


tk.Button(
    match_mode_frame,
    text="BEST OF 5",
    font=("Arial", 16),
    width=18,
    command=lambda: set_match_mode("BO5")
).pack(
    pady=10
)


tk.Button(
    match_mode_frame,
    text="UNLIMITED",
    font=("Arial", 16),
    width=18,
    command=lambda: set_match_mode("Unlimited")
).pack(
    pady=10
)


# ============================================================
# GAME SCREEN
# ============================================================

game_frame = tk.Frame(
    window
)

tk.Label(
    game_frame,
    text="Choose",
    font=("Arial", 26, "bold")
).pack(
    pady=30
)


score_label = tk.Label(
    game_frame,
    text="Score: 0 - 0",
    font=("Arial", 18)
)

score_label.pack(
    pady=10
)


result_label = tk.Label(
    game_frame,
    text="",
    font=("Arial", 18)
)

result_label.pack(
    pady=30
)


def make_choice(choice):

    if game_mode == "computer":

        play_offline(choice)

    elif game_mode == "online":

        choose_online(choice)


tk.Button(
    game_frame,
    text="STONE",
    font=("Arial", 18),
    width=15,
    command=lambda: make_choice("Stone")
).pack(
    pady=8
)


tk.Button(
    game_frame,
    text="PAPER",
    font=("Arial", 18),
    width=15,
    command=lambda: make_choice("Paper")
).pack(
    pady=8
)


tk.Button(
    game_frame,
    text="SCISSORS",
    font=("Arial", 18),
    width=15,
    command=lambda: make_choice("Scissors")
).pack(
    pady=8
)


tk.Button(
    game_frame,
    text="BACK",
    font=("Arial", 14),
    command=lambda: show_mode()
).pack(
    pady=20
)


def show_game():

    hide_all()

    game_frame.pack(
        fill="both",
        expand=True
    )


# ============================================================
# PROFILE SCREEN
# ============================================================

profile_frame = tk.Frame(
    window
)

tk.Label(
    profile_frame,
    text="PROFILE",
    font=("Arial", 28, "bold")
).pack(
    pady=50
)


profile_label = tk.Label(
    profile_frame,
    text="",
    font=("Arial", 18)
)

profile_label.pack(
    pady=30
)


def show_profile():

    hide_all()

    text = ""

    if not players:

        text = "No players yet."

    else:

        for name, data in players.items():

            text += (
                f"{name}\n"
                f"Wins: {data['wins']}\n"
                f"Losses: {data['losses']}\n"
                f"Draws: {data['draws']}\n\n"
            )

    profile_label.config(
        text=text
    )

    profile_frame.pack(
        fill="both",
        expand=True
    )


tk.Button(
    profile_frame,
    text="BACK",
    font=("Arial", 15),
    command=lambda: show_home()
).pack(
    pady=30
)


# ============================================================
# ONLINE SCREEN
# ============================================================

online_frame = tk.Frame(
    window
)

tk.Label(
    online_frame,
    text="ONLINE MULTIPLAYER",
    font=("Arial", 26, "bold")
).pack(
    pady=40
)


online_status_label = tk.Label(
    online_frame,
    text="Connecting...",
    font=("Arial", 17)
)

online_status_label.pack(
    pady=20
)


room_label = tk.Label(
    online_frame,
    text="Room ID: ---",
    font=("Arial", 22, "bold")
)

room_label.pack(
    pady=20
)


def create_room():

    send_online(
        "CREATE"
    )


def join_room():

    room = join_entry.get().strip()

    if room == "":
        return

    send_online(
        f"JOIN:{room}"
    )


tk.Button(
    online_frame,
    text="CREATE ROOM",
    font=("Arial", 16),
    width=18,
    command=create_room
).pack(
    pady=10
)


join_entry = tk.Entry(
    online_frame,
    font=("Arial", 18)
)

join_entry.pack(
    pady=10
)


tk.Button(
    online_frame,
    text="JOIN ROOM",
    font=("Arial", 16),
    width=18,
    command=join_room
).pack(
    pady=10
)


tk.Button(
    online_frame,
    text="BACK",
    font=("Arial", 14),
    command=lambda: show_mode()
).pack(
    pady=30
)


def show_online():

    hide_all()

    online_frame.pack(
        fill="both",
        expand=True
    )

    if not online_connected:

        if connect_online():

            threading.Thread(
                target=receive_online,
                daemon=True
            ).start()

            online_status_label.config(
                text="Connected!"
            )

        else:

            online_status_label.config(
                text="Could not connect to server."
            )

    else:

        online_status_label.config(
            text="Connected!"
        )


# ============================================================
# ONLINE MATCH MODE
# ============================================================

online_mode_frame = tk.Frame(
    window
)

tk.Label(
    online_mode_frame,
    text="ONLINE MATCH",
    font=("Arial", 26, "bold")
).pack(
    pady=50
)


def choose_online_mode(mode):

    if not online_connected:

        return

    send_online(
        f"MODE:{mode}"
    )

    show_online_game()


tk.Button(
    online_mode_frame,
    text="BEST OF 3",
    font=("Arial", 16),
    width=18,
    command=lambda: choose_online_mode("BO3")
).pack(
    pady=10
)


tk.Button(
    online_mode_frame,
    text="BEST OF 5",
    font=("Arial", 16),
    width=18,
    command=lambda: choose_online_mode("BO5")
).pack(
    pady=10
)


tk.Button(
    online_mode_frame,
    text="UNLIMITED",
    font=("Arial", 16),
    width=18,
    command=lambda: choose_online_mode("UNLIMITED")
).pack(
    pady=10
)


def show_online_mode():

    hide_all()

    online_mode_frame.pack(
        fill="both",
        expand=True
    )


# ============================================================
# ONLINE GAME SCREEN
# ============================================================

online_game_frame = tk.Frame(
    window
)

tk.Label(
    online_game_frame,
    text="ONLINE GAME",
    font=("Arial", 26, "bold")
).pack(
    pady=30
)


online_score_label = tk.Label(
    online_game_frame,
    text="Score: 0 - 0",
    font=("Arial", 18)
)

online_score_label.pack(
    pady=10
)


online_result_label = tk.Label(
    online_game_frame,
    text="Choose your move",
    font=("Arial", 18)
)

online_result_label.pack(
    pady=30
)


def show_online_game():

    hide_all()

    online_game_frame.pack(
        fill="both",
        expand=True
    )


tk.Button(
    online_game_frame,
    text="STONE",
    font=("Arial", 18),
    width=15,
    command=lambda: choose_online("Stone")
).pack(
    pady=8
)


tk.Button(
    online_game_frame,
    text="PAPER",
    font=("Arial", 18),
    width=15,
    command=lambda: choose_online("Paper")
).pack(
    pady=8
)


tk.Button(
    online_game_frame,
    text="SCISSORS",
    font=("Arial", 18),
    width=15,
    command=lambda: choose_online("Scissors")
).pack(
    pady=8
)


def online_rematch():

    if not online_connected:

        return

    send_online(
        "REMATCH"
    )


tk.Button(
    online_game_frame,
    text="REMATCH",
    font=("Arial", 15),
    width=15,
    command=online_rematch
).pack(
    pady=15
)


tk.Button(
    online_game_frame,
    text="BACK",
    font=("Arial", 14),
    command=lambda: show_online()
).pack(
    pady=10
)


# ============================================================
# NAVIGATION
# ============================================================

def show_home():

    hide_all()

    home_frame.pack(
        fill="both",
        expand=True
    )


def show_name():

    hide_all()

    name_entry.delete(
        0,
        tk.END
    )

    name_frame.pack(
        fill="both",
        expand=True
    )


def show_mode():

    hide_all()

    mode_frame.pack(
        fill="both",
        expand=True
    )


# ============================================================
# START
# ============================================================

load_players()


def start_app():

    hide_all()

    home_frame.pack(
        fill="both",
        expand=True
    )


splash_frame.pack(
    fill="both",
    expand=True
)


window.after(
    2200,
    start_app
)


window.mainloop()