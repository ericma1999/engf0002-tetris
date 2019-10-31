from adversary import RandomAdversary
from arguments import parser
from board import Board, Direction, Rotation
from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED
from player import SelectedPlayer, Player

import curses
import curses.ascii
import signal


COLOR_WALL = 1
COLOR_BLOCK = 2
COLOR_CELL = 3
COLOR_NOTHING = 4


def paint(window, x, y, color, count=1):
    window.addstr(y, x*2, '  ' * count, curses.color_pair(color))


def render(window, board):
    """
    Write a depiction of the board to standard output.
    """

    for y in range(board.height):
        # Draw part of the left wall.
        paint(window, 0, y, COLOR_WALL)

        # Draw each individual row
        for x in range(board.width):
            if board.falling is not None and (x, y) in board.falling:
                # Location is occupied by falling block
                color = COLOR_BLOCK
            elif (x, y) in board:
                # Location is occupied by fallen block
                color = COLOR_CELL
            else:
                # There is nothing here.
                color = COLOR_NOTHING
            paint(window, x+1, y, color)

        # Draw part of right wall.
        paint(window, x+2, y, COLOR_WALL)

    # Draw the bottom wall
    paint(window, 0, y+1, COLOR_WALL, count=board.width+2)

    # Draw the next piece

    for y in range(6):
        for x in range(4):
            if (x, y) in board.next:
                color = COLOR_BLOCK
            else:
                color = COLOR_NOTHING

            paint(window, board.width+x+3, y+1, color)

    # Draw the score line below the window.
    window.addstr(
        board.height+1,
        0,
        f'Score: {board.score} ',
        curses.color_pair(COLOR_NOTHING)
    )

    window.refresh()


class UserPlayer(Player):
    """
    A simple user player that reads moves from the command line.
    """

    screen = None

    def __init__(self, window):
        self.window = window

    def move(self, board):
        key = self.window.getch()

        if key == curses.KEY_RIGHT:
            return Direction.Right
        elif key == curses.KEY_LEFT:
            return Direction.Left
        elif key == curses.KEY_DOWN:
            return Direction.Down
        elif key == ord(' '):
            return Direction.Drop
        elif key == curses.KEY_UP:
            return Rotation.Clockwise
        elif key == ord('z'):
            return Rotation.Anticlockwise
        elif key == ord('x'):
            return Rotation.Clockwise
        elif key == curses.ascii.ESC:
            raise SystemExit


def run(window):
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    adversary = RandomAdversary(DEFAULT_SEED)

    def force_drop(signum, frame):
        signal.alarm(1)
        board.move(Direction.Down)
        render(window, board)

    signal.signal(signal.SIGALRM, force_drop)
    signal.alarm(1)

    args = parser.parse_args()
    if args.manual:
        player = UserPlayer(window)
    else:
        window.timeout(0)
        player = SelectedPlayer()

    for move in board.run(player, adversary):
        render(window, board)

        if not args.manual:
            while True:
                key = window.getch()
                if key == -1:
                    break
                elif key == curses.ascii.ESC:
                    raise SystemExit


if __name__ == '__main__':
    try:
        # Initialize terminal settings
        curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()

        window = curses.newwin(
            BOARD_HEIGHT + 2,
            (BOARD_WIDTH + 2 + 6)*2 + 1
        )
        window.keypad(True)

        # Prepare some colors to use for drawing.
        curses.init_pair(COLOR_WALL, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(COLOR_BLOCK, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(COLOR_CELL, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(COLOR_NOTHING, curses.COLOR_WHITE, curses.COLOR_BLACK)

        run(window)
    finally:
        # Clean up terminal settings once we are done
        window.keypad(False)

        curses.nocbreak()
        curses.echo()
        curses.endwin()
