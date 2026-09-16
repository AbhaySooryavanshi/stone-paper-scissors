import os
import random
import asyncio
import websockets


# ============================================================
# ROOMS
# ============================================================

rooms = {}


# ============================================================
# ROOM ID
# ============================================================

def create_room_id():

    while True:

        room_id = str(
            random.randint(100000, 999999)
        )

        if room_id not in rooms:

            return room_id


# ============================================================
# GAME RESULT
# ============================================================

def get_result(choice1, choice2):

    if choice1 == choice2:

        return "Draw"

    winning = {
        "Stone": "Scissors",
        "Paper": "Stone",
        "Scissors": "Paper"
    }

    if winning[choice1] == choice2:

        return "Player1"

    return "Player2"


# ============================================================
# SEND TO BOTH PLAYERS
# ============================================================

async def send_to_players(room, message):

    players = [
        room["player1"],
        room["player2"]
    ]

    for player in players:

        if player is not None:

            try:

                await player.send(message)

            except:

                pass


# ============================================================
# RESET ROUND
# ============================================================

def reset_round(room):

    room["choice1"] = None
    room["choice2"] = None


# ============================================================
# RESET MATCH
# ============================================================

def reset_match(room):

    room["score1"] = 0
    room["score2"] = 0

    room["choice1"] = None
    room["choice2"] = None

    room["match_over"] = False


# ============================================================
# WEBSOCKET HANDLER
# ============================================================

async def handler(websocket):

    room_id = None
    player_number = None

    print("WebSocket client connected")

    try:

        async for message in websocket:

            print(
                "Received:",
                message
            )


            # ====================================================
            # CREATE ROOM
            # ====================================================

            if message == "CREATE":

                room_id = create_room_id()

                rooms[room_id] = {

                    "player1": websocket,

                    "player2": None,

                    "choice1": None,

                    "choice2": None,

                    "score1": 0,

                    "score2": 0,

                    "target": None,

                    "mode": None,

                    "match_over": False
                }

                player_number = 1

                await websocket.send(
                    f"ROOM:{room_id}"
                )

                print(
                    f"Room created: {room_id}"
                )


            # ====================================================
            # JOIN ROOM
            # ====================================================

            elif message.startswith("JOIN:"):

                requested_room = message.split(
                    ":",
                    1
                )[1]

                room = rooms.get(
                    requested_room
                )


                if room is None:

                    await websocket.send(
                        "ERROR:ROOM_NOT_FOUND"
                    )

                    continue


                if room["player2"] is not None:

                    await websocket.send(
                        "ERROR:ROOM_FULL"
                    )

                    continue


                room["player2"] = websocket

                room_id = requested_room

                player_number = 2


                await websocket.send(
                    "JOINED"
                )


                if room["player1"] is not None:

                    try:

                        await room["player1"].send(
                            "PLAYER2_JOINED"
                        )

                    except:

                        pass


                print(
                    f"Player 2 joined room: {room_id}"
                )


            # ====================================================
            # SELECT MATCH MODE
            # ====================================================

            elif message.startswith("MODE:"):

                if room_id is None:

                    continue


                room = rooms.get(
                    room_id
                )

                if room is None:

                    continue


                mode = message.split(
                    ":",
                    1
                )[1]


                if mode not in [
                    "BO3",
                    "BO5",
                    "UNLIMITED"
                ]:

                    continue


                room["mode"] = mode


                if mode == "BO3":

                    room["target"] = 2

                elif mode == "BO5":

                    room["target"] = 3

                else:

                    room["target"] = None


                reset_match(room)


                print(
                    f"Room {room_id} mode: {mode}"
                )


                await send_to_players(
                    room,
                    f"MODE_SET:{mode}"
                )


            # ====================================================
            # PLAYER CHOICE
            # ====================================================

            elif message.startswith("CHOICE:"):

                if room_id is None:

                    continue


                room = rooms.get(
                    room_id
                )

                if room is None:

                    continue


                if room["player2"] is None:

                    await websocket.send(
                        "ERROR:WAITING_FOR_PLAYER"
                    )

                    continue


                if room["match_over"]:

                    await websocket.send(
                        "ERROR:MATCH_OVER"
                    )

                    continue


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
                        "ERROR:INVALID_CHOICE"
                    )

                    continue


                # ================================================
                # PLAYER 1 CHOICE
                # ================================================

                if player_number == 1:

                    if room["choice1"] is not None:

                        await websocket.send(
                            "ERROR:ALREADY_CHOSEN"
                        )

                        continue


                    room["choice1"] = choice


                # ================================================
                # PLAYER 2 CHOICE
                # ================================================

                elif player_number == 2:

                    if room["choice2"] is not None:

                        await websocket.send(
                            "ERROR:ALREADY_CHOSEN"
                        )

                        continue


                    room["choice2"] = choice


                print(
                    f"Room {room_id}: "
                    f"Player {player_number} chose {choice}"
                )


                # ================================================
                # WAIT FOR BOTH PLAYERS
                # ================================================

                if (
                    room["choice1"] is None
                    or
                    room["choice2"] is None
                ):

                    continue


                # ================================================
                # BOTH CHOICES RECEIVED
                # ================================================

                choice1 = room["choice1"]

                choice2 = room["choice2"]


                result = get_result(
                    choice1,
                    choice2
                )


                # ================================================
                # UPDATE SCORE
                # ================================================

                if result == "Player1":

                    room["score1"] += 1

                elif result == "Player2":

                    room["score2"] += 1


                # ================================================
                # CHECK MATCH END
                # ================================================

                target = room["target"]

                match_over_now = False


                if target is not None:

                    if (
                        room["score1"] >= target
                        or
                        room["score2"] >= target
                    ):

                        room["match_over"] = True

                        match_over_now = True


                # ================================================
                # SEND RESULT
                # ================================================

                result_message = (
                    f"RESULT:"
                    f"{choice1}:"
                    f"{choice2}:"
                    f"{result}:"
                    f"{room['score1']}:"
                    f"{room['score2']}:"
                    f"{match_over_now}"
                )


                await send_to_players(
                    room,
                    result_message
                )


                print(
                    f"Room {room_id}: "
                    f"{choice1} vs {choice2} "
                    f"-> {result}"
                )


                # ================================================
                # CLEAR ROUND
                # ================================================

                reset_round(room)


            # ====================================================
            # REMATCH
            # ====================================================

            elif message == "REMATCH":

                if room_id is None:

                    continue


                room = rooms.get(
                    room_id
                )

                if room is None:

                    continue


                if (
                    room["player1"] is None
                    or
                    room["player2"] is None
                ):

                    continue


                reset_match(room)


                print(
                    f"Rematch started: {room_id}"
                )


                await send_to_players(
                    room,
                    "REMATCH_START"
                )


    # ============================================================
    # CONNECTION CLOSED
    # ============================================================

    except websockets.exceptions.ConnectionClosed:

        print(
            "WebSocket client disconnected"
        )


    except Exception as e:

        print(
            "Client error:",
            e
        )


    # ============================================================
    # CLEANUP
    # ============================================================

    finally:

        if room_id is not None:

            room = rooms.get(
                room_id
            )


            if room:

                if player_number == 1:

                    room["player1"] = None

                elif player_number == 2:

                    room["player2"] = None


                remaining_player = None


                if room["player1"] is not None:

                    remaining_player = room["player1"]

                elif room["player2"] is not None:

                    remaining_player = room["player2"]


                if remaining_player is not None:

                    try:

                        await remaining_player.send(
                            "PLAYER_DISCONNECTED"
                        )

                    except:

                        pass


                if (
                    room["player1"] is None
                    and
                    room["player2"] is None
                ):

                    del rooms[room_id]

                    print(
                        f"Room deleted: {room_id}"
                    )


# ============================================================
# SERVER
# ============================================================

async def main():

    port = int(
        os.environ.get(
            "PORT",
            "5001"
        )
    )


    print(
        "================================"
    )

    print(
        " STONE PAPER SCISSORS SERVER"
    )

    print(
        "================================"
    )

    print(
        f"Server running on port {port}"
    )

    print(
        "Waiting for players..."
    )

    print()


    async with websockets.serve(
        handler,
        "0.0.0.0",
        port
    ):

        await asyncio.Future()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
