import math
import socket
import sys
from threading import Thread
import pygame
import pygame_menu
from logic import *

# Colors
BOARD_BACKGROUND = (0, 0, 255)
BACKROUND_COLOR = (135, 206, 235)
PLAYER1_COLOR = (255, 0, 0)
PLAYER2_COLOR = (255, 255, 0)

# Game Logic Variables
game_over = False
ROW_COUNT = 6
COLUMN_COUNT = 7
turn = 0
mutex = 0 # 1 for waiting, 0 for not waiting, 1 for got result

# Variables used for rendering
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

# Network Variables
conn = None
op=0 # variable for storing incoming data

pygame.init()
surface = pygame.display.set_mode(size)
font = pygame.font.SysFont("monospace", 50)

# Draws the board for the game using pygame module.draw functions
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(
                surface,
                BOARD_BACKGROUND,
                (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE),
            )
            pygame.draw.circle(
                surface,
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
                    surface,
                    PLAYER1_COLOR,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
            elif board[r][c] == 2:
                pygame.draw.circle(
                    surface,
                    PLAYER2_COLOR,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
    pygame.display.update()


# Render text on top of the game
def render_txt(txt, color=(0, 0, 0)):
    pygame.draw.rect(surface, BACKROUND_COLOR, (0, 0, width, SQUARESIZE))
    label = font.render(txt, 1, color)
    surface.blit(label, (20, 10))
    pygame.display.update()


def get_other_user_turn(conn):
    global op, mutex
    mutex = 1
    op = int(conn.recv(1024).decode())
    print("Recieved input from Server : ", op)
    mutex = 2

def start_game():
    global surface, board, player, conn, game_over, mutex, turn, op
    board = create_board()
    draw_board(board)
    pygame.display.update()
    while not game_over:
        # Wait for other player input
        if  turn != (player - 1):
            render_txt("Other player's turn")
            if mutex == 0:
                thread = Thread(target=get_other_user_turn, args=(conn,))
                thread.start()
            elif mutex == 2:
                col = op
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, turn + 1)
                draw_board(board)
                render_txt("")
                if winning_move(board, turn + 1):
                    render_txt("You lost :(", PLAYER1_COLOR)
                    game_over = True
                turn = (turn+1) % 2
                mutex = 0


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if turn == (player - 1):
                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(
                        surface, BACKROUND_COLOR, (0, 0, width, SQUARESIZE)
                    )
                    posx = event.pos[0]
                    if player == 1:
                        pygame.draw.circle(
                            surface, PLAYER1_COLOR, (posx, int(SQUARESIZE / 2)), RADIUS
                        )
                    else:
                        pygame.draw.circle(
                            surface, PLAYER2_COLOR, (posx, int(SQUARESIZE / 2)), RADIUS
                        )
                    pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(
                        surface, BACKROUND_COLOR, (0, 0, width, SQUARESIZE)
                    )
                    # Local Player user input
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))
                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, player)
                        draw_board(board)
                        print("Sending ", col)
                        conn.send(str(col).encode())
                        if winning_move(board, player):
                            render_txt("You win!!", PLAYER1_COLOR)
                            print("You win!!")
                            game_over = True
                        turn = (turn+1) % 2

        if game_over:
            pygame.time.wait(5000)


def play():
    global conn, player
    conn = socket.socket()
    ip = clientGUI.get_widget("ip").get_value()
    port = int(clientGUI.get_widget("port").get_value())
    print("Connecting to ip {} and in port {}".format(ip, port))
    clientGUI.get_widget("label").set_title("Connecting to server. Please wait....")
    pygame.display.update()
    try:
        conn.connect((ip, port))
        player = int(conn.recv(1024).decode())  # Gets player / turn no
        print("Player ID :", player)
        start_game()
        clientGUI.get_widget("label").set_title("")
    except Exception as e:
        print(e)
        clientGUI.get_widget("label").set_title("Can't connect")
    conn.close()


pygame.display.set_caption("Connect 4 Game")
clientGUI = pygame_menu.Menu("Client Menu", size[0], size[1], theme=pygame_menu.themes.THEME_DARK)
clientGUI.add.label("", label_id="label")
clientGUI.add.text_input("IP to connect :", default="192.168.56.1", textinput_id="ip")
clientGUI.add.text_input(
    "Port to connect :",
    default=9999,
    type="input-int",
    maxchar=5,
    textinput_id="port",
)
clientGUI.add.button("Play", play)
clientGUI.add.button("Quit", pygame_menu.events.EXIT)
clientGUI.mainloop(surface)
