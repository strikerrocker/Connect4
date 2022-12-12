import socket
import threading

from logic import *

PORT = 9999
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

waiting_clients = []

def handle_game(conn1:socket, conn2:socket):
    try:
        board = create_board()
        conn1.send("1".encode())
        conn2.send("2".encode())
        while True:
            player1Move = int(conn1.recv(1024).decode())
            row = get_next_open_row(board, player1Move)
            drop_piece(board, row, player1Move, 1)
            conn2.send(str(player1Move).encode())
            if winning_move(board, 1):
                print(f"{conn1.getpeername()} has won the game with {conn2.getpeername()}")
                break

            player2Move = int(conn2.recv(1024).decode())
            row = get_next_open_row(board, player2Move)
            drop_piece(board, row, player2Move, 2)
            conn1.send(str(player2Move).encode())
            if winning_move(board, 2):
                print(f"{conn2.getpeername()} has won the game with {conn1.getpeername()}")
                break
    except Exception as e:
        print(e)
        print("Connection closed")
    conn1.close()
    conn2.close()


def start():
    server.listen()
    print(f"[LISTENING Server is listening on IP {SERVER} and port {PORT} ]")
    while True:
        conn, addr = server.accept()
        print(f"Got connection from {addr}.")
        waiting_clients.append(conn)
        if len(waiting_clients) == 2:
            conn1,conn2 = waiting_clients.pop(),waiting_clients.pop()
            print(f"Created game b/w {conn1.getpeername()} and {conn2.getpeername()}")
            thread = threading.Thread(target=handle_game, args=(conn1,conn2))
            thread.start()
start()
