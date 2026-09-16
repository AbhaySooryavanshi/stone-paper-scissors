import asyncio
import random
import os
import websockets


rooms = {}


# =========================
# ROOM ID
# =========================

def create_room_id():

    while True:

        room_id = str(
            random.randint(100000, 999999)
        )

        if room_id not in rooms:
            return room_id


# =========================
# GAME RESULT
# =========================

def get_result(choice1, choice2):

    if choice1 == choice2:
        return "Draw"

    if (
        (choice1 == "Stone" and choice2 == "Scissors")
        or
        (choice1 == "Paper" and choice2 == "Stone")
        or
        (choice1 == "Scissors" and choice2 == "Paper")
    ):

        return "Player1"

    return "Player2"


# =========================
# SEND TO PLAYERS
# =========================

async def send_to_players(room, message):

    players = [
        room.get("player1"),
        room.get("player2")
    ]

    for player in players:

        if player is not None:

            try:
                await player.send(message)

            except:
                pass


# =========================
# SEND TURN
# =========================

async def send_turn(room):

    starter = room["starter"]

    await send_to_players(
        room,
        f"TURN:{starter}"
    )


# =========================
# NEXT ROUND
# =========================

async def start_next_round(room):

    # Small delay so players can actually see
    # the result of the previous round.

    await asyncio.sleep(2)

    if room["match_over"]:
        return

    room["round_number"] += 1

    room["choice1"] = None
    room["choice2"] = None

    await send_turn(room)


# =========================
# HANDLE MESSAGE
# =========================

async def handle_message(websocket, message):

    # =========================
    # CREATE ROOM
    # =========================

    if message == "CREATE":

        room_id = create_room_id()

        rooms[room_id] = {

            "player1": websocket,
            "player2": None,

            "choice1": None,
            "choice2": None,

            "score1": 0,
            "score2": 0,

            "mode": None,
            "target": None,

            "match_over": False,

            # First round randomly chooses starter
            "starter": random.choice([1, 2]),

            "round_number": 1,

            "rematch_requested_by": None
        }

        websocket.room_id = room_id
        websocket.player_number = 1

        await websocket.send(
            f"ROOM:{room_id}"
        )

        return


    # =========================
    # JOIN ROOM
    # =========================

    if message.startswith("JOIN:"):

        room_id = message.split(":", 1)[1]

        if room_id not in rooms:

            await websocket.send(
                "ROOM_NOT_FOUND"
            )

            return

        room = rooms[room_id]

        if room["player2"] is not None:

            await websocket.send(
                "ROOM_FULL"
            )

            return

        room["player2"] = websocket

        websocket.room_id = room_id
        websocket.player_number = 2

        await websocket.send(
            "JOINED"
        )

        await room["player1"].send(
            "PLAYER2_JOINED"
        )

        return


    # =========================
    # MATCH MODE
    # =========================

    if message.startswith("MODE:"):

        room_id = getattr(
            websocket,
            "room_id",
            None
        )

        if room_id not in rooms:
            return

        room = rooms[room_id]

        mode = message.split(":", 1)[1]

        if mode == "BO3":

            target = 2

        elif mode == "BO5":

            target = 3

        else:

            target = None

        room["mode"] = mode
        room["target"] = target

        room["choice1"] = None
        room["choice2"] = None

        room["score1"] = 0
        room["score2"] = 0

        room["match_over"] = False

        room["round_number"] = 1

        # Every new match starts with
        # a random starter.

        room["starter"] = random.choice([1, 2])

        room["rematch_requested_by"] = None

        await send_to_players(
            room,
            f"MODE_SET:{mode}"
        )

        await send_turn(room)

        return


    # =========================
    # CHOICE
    # =========================

    if message.startswith("CHOICE:"):

        room_id = getattr(
            websocket,
            "room_id",
            None
        )

        if room_id not in rooms:
            return

        room = rooms[room_id]

        if room["player2"] is None:

            await websocket.send(
                "WAITING_FOR_PLAYER"
            )

            return

        if room["match_over"]:

            await websocket.send(
                "MATCH_OVER"
            )

            return

        choice = message.split(
            ":",
            1
        )[1]

        if choice not in [
            "Stone",
            "Paper",
            "Scissors"
        ]:

            await websocket.send(
                "INVALID_CHOICE"
            )

            return

        player = websocket.player_number


        # =========================
        # STARTER CHOOSES FIRST
        # =========================

        if player != room["starter"]:

            first_choice = (
                room["choice1"]
                if room["starter"] == 1
                else room["choice2"]
            )

            if first_choice is None:

                await websocket.send(
                    "WAITING_FOR_TURN"
                )

                return


        # =========================
        # PREVENT DOUBLE CHOICE
        # =========================

        if player == 1:

            if room["choice1"] is not None:

                await websocket.send(
                    "ALREADY_CHOSEN"
                )

                return

            room["choice1"] = choice

        else:

            if room["choice2"] is not None:

                await websocket.send(
                    "ALREADY_CHOSEN"
                )

                return

            room["choice2"] = choice


        # =========================
        # STARTER CHOSE
        # =========================

        if (
            room["choice1"] is None
            or
            room["choice2"] is None
        ):

            # Tell the other player that
            # it is now their turn.

            other_player = (
                room["player2"]
                if player == 1
                else room["player1"]
            )

            if other_player is not None:

                await other_player.send(
                    "YOUR_TURN"
                )

            # Tell starter their choice
            # remains hidden.

            await websocket.send(
                "WAITING_FOR_OPPONENT_CHOICE"
            )

            return


        # =========================
        # BOTH CHOICES RECEIVED
        # =========================

        choice1 = room["choice1"]
        choice2 = room["choice2"]

        result = get_result(
            choice1,
            choice2
        )


        # =========================
        # UPDATE SCORE
        # =========================

        if result == "Player1":

            room["score1"] += 1

        elif result == "Player2":

            room["score2"] += 1


        # =========================
        # CHECK MATCH OVER
        # =========================

        match_over = False

        if room["target"] is not None:

            if room["score1"] >= room["target"]:

                match_over = True

            elif room["score2"] >= room["target"]:

                match_over = True


        room["match_over"] = match_over


        # =========================
        # SEND RESULT
        # =========================

        await send_to_players(
            room,
            (
                f"RESULT:"
                f"{choice1}:"
                f"{choice2}:"
                f"{result}:"
                f"{room['score1']}:"
                f"{room['score2']}:"
                f"{match_over}"
            )
        )


        # =========================
        # MATCH FINISHED
        # =========================

        if match_over:

            room["choice1"] = None
            room["choice2"] = None

            return


        # =========================
        # CHOOSE NEXT STARTER
        # =========================

        if result == "Player1":

            # Round winner starts next round
            room["starter"] = 1

        elif result == "Player2":

            # Round winner starts next round
            room["starter"] = 2

        else:

            # Draw = same starter
            pass


        # =========================
        # START NEXT ROUND
        # =========================

        asyncio.create_task(
            start_next_round(room)
        )

        return


    # =========================
    # REMATCH REQUEST
    # =========================

    if message == "REMATCH_REQUEST":

        room_id = getattr(
            websocket,
            "room_id",
            None
        )

        if room_id not in rooms:
            return

        room = rooms[room_id]

        player = websocket.player_number

        if room["rematch_requested_by"] == player:

            await websocket.send(
                "REMATCH_ALREADY_REQUESTED"
            )

            return

        room["rematch_requested_by"] = player

        other_player = (
            2 if player == 1 else 1
        )

        other_socket = (
            room["player2"]
            if other_player == 2
            else room["player1"]
        )

        await websocket.send(
            "REMATCH_WAITING"
        )

        if other_socket is not None:

            await other_socket.send(
                f"REMATCH_REQUESTED:{player}"
            )

        return


    # =========================
    # REMATCH ACCEPT
    # =========================

    if message == "REMATCH_ACCEPT":

        room_id = getattr(
            websocket,
            "room_id",
            None
        )

        if room_id not in rooms:
            return

        room = rooms[room_id]

        if room["rematch_requested_by"] is None:
            return

        if (
            websocket.player_number
            ==
            room["rematch_requested_by"]
        ):

            return


        # =========================
        # RESET MATCH
        # =========================

        room["choice1"] = None
        room["choice2"] = None

        room["score1"] = 0
        room["score2"] = 0

        room["match_over"] = False

        room["round_number"] = 1

        room["starter"] = random.choice([1, 2])

        room["rematch_requested_by"] = None


        await send_to_players(
            room,
            "REMATCH_START"
        )

        await send_turn(room)

        return


    # =========================
    # REMATCH DECLINE
    # =========================

    if message == "REMATCH_DECLINE":

        room_id = getattr(
            websocket,
            "room_id",
            None
        )

        if room_id not in rooms:
            return

        room = rooms[room_id]

        requester = room[
            "rematch_requested_by"
        ]

        if requester is None:
            return

        if (
            websocket.player_number
            ==
            requester
        ):

            return

        requester_socket = (
            room["player1"]
            if requester == 1
            else room["player2"]
        )

        room["rematch_requested_by"] = None

        if requester_socket is not None:

            await requester_socket.send(
                "REMATCH_DECLINED"
            )

        await websocket.send(
            "REMATCH_DECLINED"
        )

        return


# =========================
# CLIENT CONNECTION
# =========================

async def client_connected(websocket):

    print(
        "WebSocket client connected"
    )

    websocket.room_id = None
    websocket.player_number = None

    try:

        async for message in websocket:

            await handle_message(
                websocket,
                message
            )

    except websockets.exceptions.ConnectionClosed:

        print(
            "Client disconnected"
        )

    except Exception as e:

        print(
            "Connection error:",
            e
        )

    finally:

        room_id = getattr(
            websocket,
            "room_id",
            None
        )

        if room_id in rooms:

            room = rooms[room_id]

            if room["player1"] == websocket:

                room["player1"] = None

            if room["player2"] == websocket:

                room["player2"] = None

            await send_to_players(
                room,
                "PLAYER_DISCONNECTED"
            )

            if (
                room["player1"] is None
                and
                room["player2"] is None
            ):

                del rooms[room_id]


# =========================
# SERVER
# =========================

async def main():

    port = int(
        os.environ.get(
            "PORT",
            5001
        )
    )

    print(
        f"Server starting on port {port}"
    )

    async with websockets.serve(
        client_connected,
        "0.0.0.0",
        port
    ):

        print(
            f"Server running on port {port}"
        )

        await asyncio.Future()


if __name__ == "__main__":

    asyncio.run(main())