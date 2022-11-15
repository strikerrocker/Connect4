from tkinter import simpledialog
import numpy as np
import pygame
import sys
import math
from tkinter import *
import socket

BLUE = (0, 0, 255)
BACKROUND_COLOR = (135, 206, 235)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

game_over = False
turn = 0
player = 0
# initalize pygame


# define our screen size
SQUARESIZE = 100

# define width and height of board
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE / 2 - 5)

root = Tk()
s = socket.socket()
conn = None


def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r][c + 1] == piece
                and board[r][c + 2] == piece
                and board[r][c + 3] == piece
            ):
                return True

    # Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c] == piece
                and board[r + 2][c] == piece
                and board[r + 3][c] == piece
            ):
                return True

    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c + 1] == piece
                and board[r + 2][c + 2] == piece
                and board[r + 3][c + 3] == piece
            ):
                return True

    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r - 1][c + 1] == piece
                and board[r - 2][c + 2] == piece
                and board[r - 3][c + 3] == piece
            ):
                return True


def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(
                screen,
                BLUE,
                (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE),
            )
            pygame.draw.circle(
                screen,
                BACKROUND_COLOR,
                (
                    int(c * SQUARESIZE + SQUARESIZE / 2),
                    int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
                ),
                RADIUS,
            )

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(
                    screen,
                    RED,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
            elif board[r][c] == 2:
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
    pygame.display.update()


def start_game():
    pygame.init()
    global screen, board, game_over, turn, player, conn
    myfont = pygame.font.SysFont("monospace", 75)
    screen = pygame.display.set_mode(size)
    board = create_board()
    # Calling function draw_board again
    draw_board(board)
    pygame.display.update()
    title = "Server Game" if player == 1 else "Client Game"
    pygame.display.set_caption(title)
    print(title)
    while not game_over:
        if turn != (player - 1):
            row = int(conn.recv(1024).decode())
            col = int(conn.recv(1024).decode())
            print("Recieved input from other user", row, col)
            drop_piece(board, row, col, turn + 1)
            if winning_move(board, turn + 1):
                label = myfont.render("You lost :(", 1, RED)
                screen.blit(label, (40, 10))
                game_over = True
            draw_board(board)
            turn += 1
            turn = turn % 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BACKROUND_COLOR, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                else:
                    pygame.draw.circle(
                        screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS
                    )
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BACKROUND_COLOR, (0, 0, width, SQUARESIZE))
                # Ask for Player 1 Input

                if turn == (player - 1):
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, player)
                        conn.send(str(row).encode())
                        conn.send(str(col).encode())
                        if winning_move(board, player):
                            label = myfont.render("You win!!", 1, RED)
                            screen.blit(label, (40, 10))
                            game_over = True

                # print_board(board)
                draw_board(board)

                turn += 1
                turn = turn % 2

        if game_over:
            pygame.time.wait(3000)


def server():
    root.withdraw()
    global player, conn
    # ip = simpledialog.askstring("IP Address","Enter IP Address to connect to")
    # port = simpledialog.askinteger("Port No","Enter port to listen from")
    ip = "127.0.0.1"
    port = 1234
    s.bind((ip, port))
    s.listen(5)
    c, addr = s.accept()
    player = 1
    conn = c
    start_game()
    c.close()
    s.close()


def client():
    root.withdraw()
    global player, conn
    # ip = simpledialog.askstring("IP Address","Enter IP Address to connect to")
    # port = simpledialog.askinteger("Port No","Enter port to connect to")
    ip = "127.0.0.1"
    port = 1234
    s.connect((ip, port))
    player = 2
    conn = s
    start_game()
    s.close()


# Get user input
txt = Text(root, cnf={"height": 1})
txt.insert(INSERT, "Is this server or client?")
txt.pack()
t = Button(root, text="Server", command=server)
t.pack()
q = Button(root, text="Client", command=client)
q.pack()
root.mainloop()
