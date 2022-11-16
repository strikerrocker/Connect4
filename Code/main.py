import math
import socket
import sys
import pygame_menu
import numpy as np
import pygame
from pygame_menu import themes

BLUE = (0, 0, 255)
BACKROUND_COLOR = (135, 206, 235)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7


player = 0
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE / 2 - 5)

s = None
conn = None

pygame.init()
surface = pygame.display.set_mode(size)
font = pygame.font.SysFont("monospace", 50)

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece
    draw_board(board)


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


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
                surface,
                BLUE,
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
                    RED,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
            elif board[r][c] == 2:
                pygame.draw.circle(
                    surface,
                    YELLOW,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
    pygame.display.update()


def render_txt(txt, color=(0, 0, 0)):
    pygame.draw.rect(surface, BACKROUND_COLOR, (0, 0, width, SQUARESIZE))
    label = font.render(txt, 1, color)
    surface.blit(label, (20, 10))
    pygame.display.update()


def start_game():
    global surface, board, player, conn
    board = create_board()
    draw_board(board)
    pygame.display.update()
    title = "Server Game" if player == 1 else "Client Game"
    print(title)
    skip = False
    game_over=False
    turn = 0
    while not game_over:
        # Wait for other player input
        if turn != (player - 1):
            render_txt("Other user turn")
            col = int(conn.recv(1024).decode())
            print("Recieved input from other user : ", col)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, turn + 1)
            render_txt("")
            if winning_move(board, turn + 1):
                render_txt("You lost :(", RED)
                game_over = True
            turn += 1
            turn = turn % 2
            skip = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(surface, BACKROUND_COLOR, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if player == 1:
                    pygame.draw.circle(
                        surface, RED, (posx, int(SQUARESIZE / 2)), RADIUS
                    )
                else:
                    pygame.draw.circle(
                        surface, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS
                    )
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Skip if other user has played
                if skip:
                    continue
                pygame.draw.rect(surface, BACKROUND_COLOR, (0, 0, width, SQUARESIZE))
                # Local Player user input
                if turn == (player - 1):
                    posx = event.pos[0]
                    col = int(math.floor(posx / SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, player)
                        print("Sending ", col)
                        conn.send(str(col).encode())
                        if winning_move(board, player):
                            render_txt("You win!!", RED)
                            game_over = True
                        turn += 1
                        turn = turn % 2
        skip = False
        if game_over:
            pygame.time.wait(5000)


def server():
    ip = socket.gethostbyname(socket.gethostname())
    def play():
        s=socket.socket()
        port = int(serverGUI.get_widget("port").get_value())
        global player, conn
        serverGUI.update
        print("Listening in ip {} and in port {}".format(ip, port))
        s.bind((ip, port))
        try:
            s.listen(5)
            c, addr = s.accept()
            print("Connected to client with address ", addr)
            player = 1
            conn = c
            start_game()
            c.close()
            main_menu.reset(1)
        except Exception as e:
            print(e)
            serverGUI.get_widget("label").set_title("Connection Error")
        s.close()

    serverGUI = pygame_menu.Menu(
        "Server Menu", size[0], size[1], theme=themes.THEME_DARK
    )
    serverGUI.add.label("",label_id="label")
    serverGUI.add.label("Server IP : "+ip)

    serverGUI.add.text_input(
        "Port to host :", default=9999, type="input-int", maxchar=5, textinput_id="port"
    )
    serverGUI.add.button("Play", play)
    main_menu._open(serverGUI)


def client():
    def play():
        s=socket.socket()
        ip = clientGUI.get_widget("ip").get_value()
        port = int(clientGUI.get_widget("port").get_value())
        global player, conn
        print("Connecting to ip {} and in port {}".format(ip, port))
        try:
            s.connect((ip, port))
            player = 2
            conn = s
            start_game()
            main_menu.reset(1)
        except Exception as e:
            print(e)
            clientGUI.get_widget("label").set_title("Can't connect")
        s.close()
        

    clientGUI = pygame_menu.Menu(
        "Client Menu", size[0], size[1], theme=themes.THEME_DARK
    )
    clientGUI.add.label("",label_id="label")
    clientGUI.add.text_input("IP to connect :", default="192.168.56.1", textinput_id="ip")
    clientGUI.add.text_input(
        "Port to connect :",
        default=9999,
        type="input-int",
        maxchar=5,
        textinput_id="port",
    )
    clientGUI.add.button("Play", play)
    main_menu._open(clientGUI)


pygame.display.set_caption("Connect 4 Game")
main_menu = pygame_menu.Menu("Main Menu", size[0], size[1], theme=themes.THEME_DARK)
main_menu.add.button("Server", server)
main_menu.add.button("Client", client)
main_menu.add.button("Quit", pygame_menu.events.EXIT)
main_menu.mainloop(surface)