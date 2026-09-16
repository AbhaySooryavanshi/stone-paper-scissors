import socket

HOST = "127.0.0.1"
PORT = 5000

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client.connect((HOST, PORT))

print("Connected!")

print("1. Create Room")
print("2. Join Room")

option = input("Choose: ")


# CREATE
if option == "1":

    client.sendall("CREATE".encode())

    response = client.recv(1024).decode()

    room_id = response.split(":")[1]

    player_number = 1

    print()
    print("Room ID:", room_id)
    print("Waiting for Player 2...")

    message = client.recv(1024).decode()

    if message == "PLAYER2_JOINED":
        print("Player 2 joined!")


# JOIN
elif option == "2":

    room_id = input("Enter Room ID: ")

    client.sendall(
        f"JOIN:{room_id}".encode()
    )

    response = client.recv(1024).decode()

    if response != "JOINED":

        print("Could not join room.")
        client.close()
        exit()

    player_number = 2

    print("Joined successfully!")


else:

    print("Invalid option.")
    client.close()
    exit()


# MATCH MODE
print()
print("Choose Match Mode")
print("1. Best of 3")
print("2. Best of 5")
print("3. Unlimited")

mode = input("Choose: ")

if mode == "1":
    client.sendall("MODE:BO3".encode())

elif mode == "2":
    client.sendall("MODE:BO5".encode())

elif mode == "3":
    client.sendall("MODE:UNLIMITED".encode())

else:
    print("Invalid mode.")
    client.close()
    exit()


# GAME LOOP

while True:

    print()
    print("==============================")
    print("STONE PAPER SCISSORS")
    print("==============================")

    print("s = Stone")
    print("p = Paper")
    print("c = Scissors")

    choice = input("Your choice: ").lower()

    if choice == "s":
        selected = "Stone"

    elif choice == "p":
        selected = "Paper"

    elif choice == "c":
        selected = "Scissors"

    else:
        print("Invalid choice!")
        continue

    client.sendall(
        f"CHOICE:{selected}".encode()
    )

    print("Waiting for opponent...")

    response = client.recv(1024).decode()

    if response.startswith("RESULT:"):

        data = response.split(":")

        my_choice = data[1]
        opponent_choice = data[2]
        result = data[3]

        score1 = int(data[4])
        score2 = int(data[5])

        match_over = data[6] == "True"

        print()
        print("------------------------------")

        if player_number == 1:

            print("You:", my_choice)
            print("Opponent:", opponent_choice)

        else:

            print("You:", opponent_choice)
            print("Opponent:", my_choice)

        if result == "Draw":

            print("DRAW!")

        elif (
            (player_number == 1 and result == "Player1")
            or
            (player_number == 2 and result == "Player2")
        ):

            print("YOU WIN! 🎉")

        else:

            print("YOU LOSE!")

        print()
        print("Score:", score1, "-", score2)

        print("------------------------------")

        if match_over:

            if score1 > score2:
                winner = "Player 1"
            else:
                winner = "Player 2"

            print()
            print("🏆 MATCH OVER!")
            print("Winner:", winner)

            again = input(
                "Play again? (y/n): "
            ).lower()

            if again == "y":

                client.sendall(
                    "REMATCH".encode()
                )

                message = client.recv(1024).decode()

                if message == "REMATCH_START":

                    print()
                    print("🔄 Rematch started!")

                    continue

            else:

                print("Thanks for playing!")
                break