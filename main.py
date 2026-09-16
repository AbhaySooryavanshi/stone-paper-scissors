import tkinter as tk
import random
import json
import os
import threading

from websockets.sync.client import connect


SERVER_URL = "wss://stone-paper-scissors-cdvp.onrender.com"

# =========================
# ONLINE VARIABLES
# =========================

network_client = None
online_connected = False
online_player_number = None
online_room_id = None
online_starter = None
online_can_choose = False
rematch_request_from = None


# =========================
# PLAYER PROFILE
# =========================

PROFILE_FILE = "players.json"

if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as file:
        players = json.load(file)
else:
    players = {}

current_player = None


def save_players():
    with open(PROFILE_FILE, "w") as file:
        json.dump(players, file, indent=4)


# =========================
# MAIN WINDOW
# =========================

root = tk.Tk()
root.title("Stone Paper Scissors")
root.geometry("700x800")
root.resizable(False, False)


# =========================
# COLORS / FONTS
# =========================

BG = "#1e1e2f"
BUTTON = "#3b3b5c"
TEXT = "white"
GREEN = "#4CAF50"
RED = "#F44336"
YELLOW = "#FFC107"


# =========================
# GAME VARIABLES
# =========================

game_mode = ""
match_mode = ""

player_score = 0
computer_score = 0

target_score = 0
match_over = False


# =========================
# FRAMES
# =========================

splash_frame = tk.Frame(root, bg=BG)
home_frame = tk.Frame(root, bg=BG)
name_frame = tk.Frame(root, bg=BG)
mode_frame = tk.Frame(root, bg=BG)
match_frame = tk.Frame(root, bg=BG)
game_frame = tk.Frame(root, bg=BG)
profile_frame = tk.Frame(root, bg=BG)

online_frame = tk.Frame(root, bg=BG)
online_mode_frame = tk.Frame(root, bg=BG)
online_game_frame = tk.Frame(root, bg=BG)


# =========================
# HELPER
# =========================

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def show_frame(frame):
    for f in [
        splash_frame,
        home_frame,
        name_frame,
        mode_frame,
        match_frame,
        game_frame,
        profile_frame,
        online_frame,
        online_mode_frame,
        online_game_frame
    ]:
        f.pack_forget()

    frame.pack(fill="both", expand=True)


# =========================
# SPLASH
# =========================

splash_label = tk.Label(
    splash_frame,
    text="STONE\nPAPER\nSCISSORS",
    font=("Arial", 40, "bold"),
    fg=TEXT,
    bg=BG
)

splash_label.pack(expand=True)


def show_home():
    show_frame(home_frame)


# =========================
# HOME
# =========================

home_title = tk.Label(
    home_frame,
    text="STONE PAPER SCISSORS",
    font=("Arial", 28, "bold"),
    fg=TEXT,
    bg=BG
)

home_title.pack(pady=100)


play_button = tk.Button(
    home_frame,
    text="PLAY",
    font=("Arial", 18, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: show_name()
)

play_button.pack(pady=20)


profile_button = tk.Button(
    home_frame,
    text="PROFILE",
    font=("Arial", 18, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: show_profile()
)

profile_button.pack(pady=20)


# =========================
# NAME
# =========================

name_title = tk.Label(
    name_frame,
    text="ENTER YOUR NAME",
    font=("Arial", 26, "bold"),
    fg=TEXT,
    bg=BG
)

name_title.pack(pady=100)


name_entry = tk.Entry(
    name_frame,
    font=("Arial", 18),
    justify="center"
)

name_entry.pack(pady=20)


def save_name():

    global current_player

    name = name_entry.get().strip()

    if name == "":
        return

    current_player = name

    if name not in players:

        players[name] = {
            "games": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0
        }

    save_players()

    show_mode()


tk.Button(
    name_frame,
    text="CONTINUE",
    font=("Arial", 16, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=save_name
).pack(pady=20)


def show_name():

    show_frame(name_frame)

    name_entry.delete(
        0,
        tk.END
    )


# =========================
# MODE
# =========================

mode_title = tk.Label(
    mode_frame,
    text="CHOOSE MODE",
    font=("Arial", 28, "bold"),
    fg=TEXT,
    bg=BG
)

mode_title.pack(pady=80)


def select_computer():

    global game_mode

    game_mode = "computer"

    show_match_mode()


def select_pvp():

    global game_mode

    game_mode = "pvp"

    show_match_mode()


def select_online():

    global game_mode

    game_mode = "online"

    show_online()


tk.Button(
    mode_frame,
    text="VS COMPUTER",
    font=("Arial", 17, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=select_computer
).pack(pady=15)


tk.Button(
    mode_frame,
    text="2 PLAYER",
    font=("Arial", 17, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=select_pvp
).pack(pady=15)


tk.Button(
    mode_frame,
    text="ONLINE",
    font=("Arial", 17, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=select_online
).pack(pady=15)


def show_mode():

    show_frame(mode_frame)


# =========================
# MATCH MODE
# =========================

match_title = tk.Label(
    match_frame,
    text="CHOOSE MATCH",
    font=("Arial", 28, "bold"),
    fg=TEXT,
    bg=BG
)

match_title.pack(pady=80)


def select_bo3():

    global match_mode

    match_mode = "BO3"

    start_offline_game()


def select_bo5():

    global match_mode

    match_mode = "BO5"

    start_offline_game()


def select_unlimited():

    global match_mode

    match_mode = "UNLIMITED"

    start_offline_game()


tk.Button(
    match_frame,
    text="BEST OF 3",
    font=("Arial", 17, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=select_bo3
).pack(pady=15)


tk.Button(
    match_frame,
    text="BEST OF 5",
    font=("Arial", 17, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=select_bo5
).pack(pady=15)


tk.Button(
    match_frame,
    text="UNLIMITED",
    font=("Arial", 17, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=select_unlimited
).pack(pady=15)


def show_match_mode():

    show_frame(match_frame)


# =========================
# OFFLINE GAME
# =========================

game_title = tk.Label(
    game_frame,
    text="STONE PAPER SCISSORS",
    font=("Arial", 24, "bold"),
    fg=TEXT,
    bg=BG
)

game_title.pack(pady=30)


score_label = tk.Label(
    game_frame,
    text="You: 0   |   Computer: 0",
    font=("Arial", 20, "bold"),
    fg=TEXT,
    bg=BG
)

score_label.pack(pady=20)


result_label = tk.Label(
    game_frame,
    text="Choose your move",
    font=("Arial", 18, "bold"),
    fg=TEXT,
    bg=BG
)

result_label.pack(pady=30)


def get_target_score():

    if match_mode == "BO3":
        return 2

    elif match_mode == "BO5":
        return 3

    return None


def play_offline(choice):

    global player_score
    global computer_score
    global match_over

    if match_over:
        return

    computer_choice = random.choice(
        ["Stone", "Paper", "Scissors"]
    )

    if choice == computer_choice:

        result = "Draw!"

    elif (
        (choice == "Stone" and computer_choice == "Scissors")
        or
        (choice == "Paper" and computer_choice == "Stone")
        or
        (choice == "Scissors" and computer_choice == "Paper")
    ):

        player_score += 1

        result = "You won this round!"

    else:

        computer_score += 1

        result = "Computer won this round!"

    score_label.config(
        text=f"You: {player_score}   |   Computer: {computer_score}"
    )

    text = (
        f"You chose: {choice}\n"
        f"Computer chose: {computer_choice}\n\n"
        f"{result}"
    )

    target = get_target_score()

    if target is not None:

        if player_score >= target:

            match_over = True

            text += (
                "\n\n"
                "MATCH OVER!\n"
                "You won the match!"
            )

            update_profile("win")

            result_label.config(
                text=text,
                fg=GREEN
            )

            show_game_end_buttons()

            return

        elif computer_score >= target:

            match_over = True

            text += (
                "\n\n"
                "MATCH OVER!\n"
                "Computer won the match!"
            )

            update_profile("loss")

            result_label.config(
                text=text,
                fg=RED
            )

            show_game_end_buttons()

            return

    result_label.config(
        text=text,
        fg=TEXT
    )


def update_profile(result):

    if current_player is None:
        return

    if current_player not in players:
        return

    players[current_player]["games"] += 1

    if result == "win":

        players[current_player]["wins"] += 1

    elif result == "loss":

        players[current_player]["losses"] += 1

    elif result == "draw":

        players[current_player]["draws"] += 1

    save_players()


def start_offline_game():

    global player_score
    global computer_score
    global target_score
    global match_over

    player_score = 0
    computer_score = 0

    target_score = get_target_score()

    match_over = False

    score_label.config(
        text="You: 0   |   Computer: 0"
    )

    result_label.config(
        text="Choose your move",
        fg=TEXT
    )

    clear_game_end_buttons()

    show_frame(game_frame)


def play_again():

    start_offline_game()


def show_game_end_buttons():

    if hasattr(show_game_end_buttons, "frame"):

        show_game_end_buttons.frame.destroy()

    frame = tk.Frame(
        game_frame,
        bg=BG
    )

    frame.pack(pady=20)

    show_game_end_buttons.frame = frame

    tk.Button(
        frame,
        text="PLAY AGAIN",
        font=("Arial", 15, "bold"),
        width=15,
        bg=BUTTON,
        fg=TEXT,
        command=play_again
    ).pack(pady=5)

    tk.Button(
        frame,
        text="BACK TO MENU",
        font=("Arial", 15, "bold"),
        width=15,
        bg=BUTTON,
        fg=TEXT,
        command=show_home
    ).pack(pady=5)


def clear_game_end_buttons():

    if hasattr(show_game_end_buttons, "frame"):

        show_game_end_buttons.frame.destroy()

        del show_game_end_buttons.frame


tk.Button(
    game_frame,
    text="STONE",
    font=("Arial", 16, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: play_offline("Stone")
).pack(pady=8)


tk.Button(
    game_frame,
    text="PAPER",
    font=("Arial", 16, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: play_offline("Paper")
).pack(pady=8)


tk.Button(
    game_frame,
    text="SCISSORS",
    font=("Arial", 16, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: play_offline("Scissors")
).pack(pady=8)


tk.Button(
    game_frame,
    text="BACK",
    font=("Arial", 14),
    width=12,
    bg=BUTTON,
    fg=TEXT,
    command=show_home
).pack(pady=30)


# =========================
# 2 PLAYER
# =========================

def play_pvp():
    pass


# =========================
# PROFILE
# =========================

profile_title = tk.Label(
    profile_frame,
    text="PROFILE",
    font=("Arial", 28, "bold"),
    fg=TEXT,
    bg=BG
)

profile_title.pack(pady=70)


profile_info = tk.Label(
    profile_frame,
    text="",
    font=("Arial", 18),
    fg=TEXT,
    bg=BG,
    justify="center"
)

profile_info.pack(pady=30)


def show_profile():

    if current_player is None:

        profile_info.config(
            text="No profile"
        )

    else:

        data = players.get(
            current_player,
            {
                "games": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0
            }
        )

        profile_info.config(
            text=(
                f"Name: {current_player}\n\n"
                f"Games: {data['games']}\n"
                f"Wins: {data['wins']}\n"
                f"Losses: {data['losses']}\n"
                f"Draws: {data['draws']}"
            )
        )

    show_frame(profile_frame)


tk.Button(
    profile_frame,
    text="BACK",
    font=("Arial", 15, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=show_home
).pack(pady=50)


# =========================
# ONLINE CONNECTION
# =========================

def connect_online():

    global network_client
    global online_connected

    try:

        network_client = connect(
            SERVER_URL,
            proxy=None,
            open_timeout=15
        )

        online_connected = True

        threading.Thread(
            target=receive_online,
            daemon=True
        ).start()

        return True

    except Exception as e:

        online_connected = False

        print("Connection error:", e)

        return False


def receive_online():

    global online_connected

    try:

        while online_connected:

            message = network_client.recv()

            root.after(
                0,
                lambda m=message: handle_online_message(m)
            )

    except Exception as e:

        print("Receive error:", e)

        online_connected = False


# =========================
# ONLINE SCREEN
# =========================

online_title = tk.Label(
    online_frame,
    text="ONLINE",
    font=("Arial", 28, "bold"),
    fg=TEXT,
    bg=BG
)

online_title.pack(pady=70)


online_status_label = tk.Label(
    online_frame,
    text="",
    font=("Arial", 17),
    fg=TEXT,
    bg=BG
)

online_status_label.pack(pady=20)


def create_room():

    if not online_connected:

        if not connect_online():

            online_status_label.config(
                text="Could not connect to server",
                fg=RED
            )

            return

    try:

        network_client.send("CREATE")

        online_status_label.config(
            text="Creating room..."
        )

    except Exception as e:

        online_status_label.config(
            text="Connection error",
            fg=RED
        )

        print(e)


def join_room():

    room_id = join_entry.get().strip()

    if room_id == "":
        return

    if not online_connected:

        if not connect_online():

            online_status_label.config(
                text="Could not connect to server",
                fg=RED
            )

            return

    try:

        network_client.send(
            f"JOIN:{room_id}"
        )

        online_status_label.config(
            text="Joining room..."
        )

    except Exception as e:

        online_status_label.config(
            text="Connection error",
            fg=RED
        )

        print(e)


tk.Button(
    online_frame,
    text="CREATE ROOM",
    font=("Arial", 16, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=create_room
).pack(pady=15)


join_entry = tk.Entry(
    online_frame,
    font=("Arial", 18),
    justify="center"
)

join_entry.pack(pady=10)


tk.Button(
    online_frame,
    text="JOIN ROOM",
    font=("Arial", 16, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=join_room
).pack(pady=15)


tk.Button(
    online_frame,
    text="BACK",
    font=("Arial", 14),
    width=12,
    bg=BUTTON,
    fg=TEXT,
    command=show_home
).pack(pady=40)


def show_online():

    show_frame(online_frame)

    online_status_label.config(
        text="Create a room or join a room",
        fg=TEXT
    )

    join_entry.delete(
        0,
        tk.END
    )


# =========================
# ONLINE MODE
# =========================

online_mode_title = tk.Label(
    online_mode_frame,
    text="CHOOSE MATCH",
    font=("Arial", 28, "bold"),
    fg=TEXT,
    bg=BG
)

online_mode_title.pack(pady=80)


def send_online_mode(mode):

    try:

        network_client.send(
            f"MODE:{mode}"
        )

    except Exception as e:

        print(e)


tk.Button(
    online_mode_frame,
    text="BEST OF 3",
    font=("Arial", 17, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: send_online_mode("BO3")
).pack(pady=15)


tk.Button(
    online_mode_frame,
    text="BEST OF 5",
    font=("Arial", 17, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: send_online_mode("BO5")
).pack(pady=15)


tk.Button(
    online_mode_frame,
    text="UNLIMITED",
    font=("Arial", 17, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: send_online_mode("UNLIMITED")
).pack(pady=15)


tk.Button(
    online_mode_frame,
    text="BACK",
    font=("Arial", 14),
    width=12,
    bg=BUTTON,
    fg=TEXT,
    command=show_online
).pack(pady=40)


def show_online_mode():

    show_frame(online_mode_frame)


# =========================
# ONLINE GAME
# =========================

online_game_title = tk.Label(
    online_game_frame,
    text="ONLINE GAME",
    font=("Arial", 26, "bold"),
    fg=TEXT,
    bg=BG
)

online_game_title.pack(pady=30)


online_score_label = tk.Label(
    online_game_frame,
    text="You: 0   |   Opponent: 0",
    font=("Arial", 20, "bold"),
    fg=TEXT,
    bg=BG
)

online_score_label.pack(pady=20)


online_result_label = tk.Label(
    online_game_frame,
    text="Waiting...",
    font=("Arial", 18, "bold"),
    fg=TEXT,
    bg=BG,
    justify="center"
)

online_result_label.pack(pady=30)


# =========================
# ONLINE CHOICE BUTTONS
# =========================

def choose_online(choice):

    global online_can_choose

    if not online_connected:
        return

    # Only allow the player to choose
    # when the server has given them permission.

    if not online_can_choose:

        online_result_label.config(
            text="WAIT FOR YOUR TURN",
            fg=YELLOW
        )

        return

    try:

        network_client.send(
            f"CHOICE:{choice}"
        )

        # Choice has now been submitted.
        # Keep it hidden until both players choose.

        online_can_choose = False

        online_result_label.config(
            text=(
                f"You chose {choice}\n\n"
                "Waiting for opponent..."
            ),
            fg=TEXT
        )

    except Exception as e:

        print(e)


tk.Button(
    online_game_frame,
    text="STONE",
    font=("Arial", 16, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: choose_online("Stone")
).pack(pady=8)


tk.Button(
    online_game_frame,
    text="PAPER",
    font=("Arial", 16, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: choose_online("Paper")
).pack(pady=8)


tk.Button(
    online_game_frame,
    text="SCISSORS",
    font=("Arial", 16, "bold"),
    width=15,
    bg=BUTTON,
    fg=TEXT,
    command=lambda: choose_online("Scissors")
).pack(pady=8)


# =========================
# REMATCH BUTTON
# =========================

def request_rematch():

    global online_can_choose

    if not online_connected:
        return

    try:

        network_client.send(
            "REMATCH_REQUEST"
        )

        online_can_choose = False

        online_result_label.config(
            text=(
                "REMATCH REQUEST SENT\n\n"
                "Waiting for opponent..."
            ),
            fg=YELLOW
        )

        rematch_button.config(
            state="disabled"
        )

    except Exception as e:

        print(e)


rematch_button = tk.Button(
    online_game_frame,
    text="REQUEST REMATCH",
    font=("Arial", 15, "bold"),
    width=18,
    bg=BUTTON,
    fg=TEXT,
    command=request_rematch
)

rematch_button.pack(pady=20)


# =========================
# REMATCH RESPONSE BUTTONS
# =========================

def accept_rematch():

    if not online_connected:
        return

    try:

        network_client.send(
            "REMATCH_ACCEPT"
        )

        rematch_response_frame.pack_forget()

    except Exception as e:

        print(e)


def decline_rematch():

    if not online_connected:
        return

    try:

        network_client.send(
            "REMATCH_DECLINE"
        )

        rematch_response_frame.pack_forget()

    except Exception as e:

        print(e)


rematch_response_frame = tk.Frame(
    online_game_frame,
    bg=BG
)

tk.Button(
    rematch_response_frame,
    text="ACCEPT",
    font=("Arial", 14, "bold"),
    width=10,
    bg=BUTTON,
    fg=TEXT,
    command=accept_rematch
).pack(side="left", padx=5)


tk.Button(
    rematch_response_frame,
    text="DECLINE",
    font=("Arial", 14, "bold"),
    width=10,
    bg=BUTTON,
    fg=TEXT,
    command=decline_rematch
).pack(side="left", padx=5)


# =========================
# BACK
# =========================

tk.Button(
    online_game_frame,
    text="BACK",
    font=("Arial", 14),
    width=12,
    bg=BUTTON,
    fg=TEXT,
    command=show_home
).pack(pady=20)


def show_online_game():

    show_frame(online_game_frame)

    rematch_response_frame.pack_forget()

    rematch_button.config(
        state="normal"
    )


# =========================
# ONLINE MESSAGE HANDLER
# =========================

def handle_online_message(message):

    global online_player_number
    global online_room_id
    global online_starter
    global online_can_choose
    global rematch_request_from

    print("SERVER:", message)

    # =========================
    # ROOM CREATED
    # =========================

    if message.startswith("ROOM:"):

        online_room_id = message.split(":")[1]

        online_player_number = 1

        online_status_label.config(
            text=(
                f"ROOM ID: {online_room_id}\n\n"
                "Waiting for Player 2..."
            ),
            fg=TEXT
        )


    # =========================
    # JOINED
    # =========================

    elif message == "JOINED":

        online_player_number = 2

        online_status_label.config(
            text="Joined room. Waiting for host..."
        )


    # =========================
    # PLAYER 2 JOINED
    # =========================

    elif message == "PLAYER2_JOINED":

        online_status_label.config(
            text=(
                "Player 2 joined!\n"
                "Choose match mode."
            )
        )

        if online_player_number == 1:

            show_online_mode()


    # =========================
    # MODE SET
    # =========================

    elif message.startswith("MODE_SET:"):

        mode = message.split(":")[1]

        online_can_choose = False

        online_score_label.config(
            text="You: 0   |   Opponent: 0"
        )

        online_result_label.config(
            text=(
                f"{mode}\n\n"
                "Waiting for first player..."
            ),
            fg=TEXT
        )

        show_online_game()


    # =========================
    # TURN
    # =========================

    elif message.startswith("TURN:"):

        online_starter = int(
            message.split(":")[1]
        )

        if online_player_number == online_starter:

            # Starter gets the first choice.

            online_can_choose = True

            online_result_label.config(
                text=(
                    "YOU START THIS ROUND\n\n"
                    "Choose your move"
                ),
                fg=GREEN
            )

        else:

            # Other player must wait until
            # the starter submits.

            online_can_choose = False

            online_result_label.config(
                text=(
                    "OPPONENT STARTS THIS ROUND\n\n"
                    "Wait for opponent to choose..."
                ),
                fg=YELLOW
            )

        show_online_game()


    # =========================
    # YOUR TURN
    # =========================

    elif message == "YOUR_TURN":

        # Starter has already chosen.
        # Now the second player gets to choose.

        online_can_choose = True

        online_result_label.config(
            text=(
                "YOUR TURN\n\n"
                "Choose your move"
            ),
            fg=GREEN
        )

        show_online_game()


    # =========================
    # WAITING FOR OPPONENT CHOICE
    # =========================

    elif message == "WAITING_FOR_OPPONENT_CHOICE":

        online_can_choose = False

        online_result_label.config(
            text=(
                "Your choice is hidden.\n\n"
                "Waiting for opponent..."
            ),
            fg=TEXT
        )


    # =========================
    # REMATCH START
    # =========================

    elif message == "REMATCH_START":

        online_can_choose = False

        online_score_label.config(
            text="You: 0   |   Opponent: 0"
        )

        rematch_response_frame.pack_forget()

        rematch_button.config(
            state="normal"
        )

        online_result_label.config(
            text="New match started!",
            fg=TEXT
        )

        show_online_game()


    # =========================
    # REMATCH REQUESTED
    # =========================

    elif message.startswith("REMATCH_REQUESTED:"):

        rematch_request_from = int(
            message.split(":")[1]
        )

        online_can_choose = False

        show_online_game()

        rematch_button.config(
            state="disabled"
        )

        online_result_label.config(
            text=(
                "YOUR OPPONENT WANTS A REMATCH\n\n"
                "Do you want to play again?"
            ),
            fg=YELLOW
        )

        rematch_response_frame.pack(
            pady=10
        )


    # =========================
    # REMATCH WAITING
    # =========================

    elif message == "REMATCH_WAITING":

        online_can_choose = False

        rematch_button.config(
            state="disabled"
        )

        online_result_label.config(
            text=(
                "REMATCH REQUEST SENT\n\n"
                "Waiting for opponent's response..."
            ),
            fg=YELLOW
        )


    # =========================
    # REMATCH DECLINED
    # =========================

    elif message == "REMATCH_DECLINED":

        online_can_choose = False

        rematch_response_frame.pack_forget()

        rematch_button.config(
            state="normal"
        )

        online_result_label.config(
            text="Rematch declined.",
            fg=RED
        )


    # =========================
    # REMATCH ALREADY REQUESTED
    # =========================

    elif message == "REMATCH_ALREADY_REQUESTED":

        online_result_label.config(
            text=(
                "Rematch request already sent.\n"
                "Waiting for opponent..."
            ),
            fg=YELLOW
        )


    # =========================
    # RESULT
    # =========================

    elif message.startswith("RESULT:"):

        # Nobody can choose while the result
        # is being displayed.

        online_can_choose = False

        parts = message.split(":")

        if len(parts) >= 7:

            choice1 = parts[1]
            choice2 = parts[2]
            result = parts[3]

            score1 = int(parts[4])
            score2 = int(parts[5])

            match_is_over = parts[6] == "True"

            if online_player_number == 1:

                my_choice = choice1
                opponent_choice = choice2

                my_score = score1
                opponent_score = score2

            else:

                my_choice = choice2
                opponent_choice = choice1

                my_score = score2
                opponent_score = score1


            online_score_label.config(
                text=(
                    f"You: {my_score}   |   "
                    f"Opponent: {opponent_score}"
                )
            )


            # =========================
            # ROUND RESULT
            # =========================

            if result == "Draw":

                round_text = "DRAW!"

            elif (
                (
                    online_player_number == 1
                    and
                    result == "Player1"
                )
                or
                (
                    online_player_number == 2
                    and
                    result == "Player2"
                )
            ):

                round_text = "YOU WON THIS ROUND!"

            else:

                round_text = "YOU LOST THIS ROUND!"


            text = (
                f"You chose: {my_choice}\n"
                f"Opponent chose: {opponent_choice}\n\n"
                f"{round_text}"
            )


            # =========================
            # MATCH OVER
            # =========================

            if match_is_over:

                if my_score > opponent_score:

                    text += (
                        "\n\n"
                        "MATCH OVER!\n"
                        "YOU WON THE MATCH!"
                    )

                    online_result_label.config(
                        text=text,
                        fg=GREEN
                    )

                elif opponent_score > my_score:

                    text += (
                        "\n\n"
                        "MATCH OVER!\n"
                        "YOU LOST THE MATCH!"
                    )

                    online_result_label.config(
                        text=text,
                        fg=RED
                    )

                else:

                    text += (
                        "\n\n"
                        "MATCH OVER!\n"
                        "MATCH DRAW!"
                    )

                    online_result_label.config(
                        text=text,
                        fg=YELLOW
                    )

                rematch_button.config(
                    state="normal"
                )

            else:

                online_result_label.config(
                    text=text,
                    fg=TEXT
                )


    # =========================
    # WAITING FOR TURN
    # =========================

    elif message == "WAITING_FOR_TURN":

        online_can_choose = False

        online_result_label.config(
            text=(
                "WAIT FOR YOUR TURN\n\n"
                "The other player must choose first."
            ),
            fg=YELLOW
        )


    # =========================
    # ALREADY CHOSEN
    # =========================

    elif message == "ALREADY_CHOSEN":

        online_can_choose = False

        online_result_label.config(
            text=(
                "You already chose this round.\n"
                "Waiting for opponent..."
            ),
            fg=YELLOW
        )


    # =========================
    # WAITING FOR PLAYER
    # =========================

    elif message == "WAITING_FOR_PLAYER":

        online_can_choose = False

        online_result_label.config(
            text="Waiting for Player 2...",
            fg=YELLOW
        )


    # =========================
    # MATCH OVER
    # =========================

    elif message == "MATCH_OVER":

        online_can_choose = False

        online_result_label.config(
            text=(
                "MATCH OVER!\n\n"
                "You can request a rematch."
            ),
            fg=YELLOW
        )

        rematch_button.config(
            state="normal"
        )


    # =========================
    # INVALID CHOICE
    # =========================

    elif message == "INVALID_CHOICE":

        online_result_label.config(
            text="Invalid choice!",
            fg=RED
        )


    # =========================
    # ROOM NOT FOUND
    # =========================

    elif message == "ROOM_NOT_FOUND":

        online_status_label.config(
            text="Room not found!",
            fg=RED
        )


    # =========================
    # ROOM FULL
    # =========================

    elif message == "ROOM_FULL":

        online_status_label.config(
            text="Room is full!",
            fg=RED
        )


    # =========================
    # PLAYER DISCONNECTED
    # =========================

    elif message == "PLAYER_DISCONNECTED":

        online_can_choose = False

        online_result_label.config(
            text="Opponent disconnected.",
            fg=RED
        )


# =========================
# START
# =========================

show_frame(splash_frame)

root.after(
    2000,
    show_home
)

root.mainloop()