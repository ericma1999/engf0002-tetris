from adversary import RandomAdversary
from board import Board, Direction, Rotation
from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED
from player import SelectedPlayer, Player

import curses
import curses.ascii


COLOR_WALL = 1
COLOR_BLOCK = 2
COLOR_CELL = 3
COLOR_NOTHING = 4


def render(window, board):
    """
    Write a depiction of the board to standard output.
    """

    for y in range(board.height):
        # Draw part of the left wall.
        window.addstr(y, 0, '  ', curses.color_pair(COLOR_WALL))

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
            window.addstr(y, (x+1)*2, '  ', curses.color_pair(color))

        # Draw part of right wall.
        window.addstr(y, (x+2)*2, '  ', curses.color_pair(COLOR_WALL))

    # Draw the bottom wall
    window.addstr(
        y+1,
        0,
        '  ' * (board.width+2),
        curses.color_pair(COLOR_WALL)
    )

    # Draw the score line below the window.
    window.addstr(
        y+2,
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

        if key == -1:
            return Direction.Down
        elif key == curses.KEY_RIGHT:
            return Direction.Right
        elif key == curses.KEY_LEFT:
            return Direction.Left
        elif key == curses.KEY_DOWN:
            return Direction.Down
        elif key == ord(' '):
            return Direction.Drop
        elif key == curses.KEY_UP:
            return Rotation.Clockwise
        elif key == curses.ascii.ESC:
            raise SystemExit


def run(window):
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    adversary = RandomAdversary(DEFAULT_SEED)

    # Fall back to user player if none selected.
    if SelectedPlayer is None:
        player = UserPlayer(window)
    else:
        player = SelectedPlayer()

    for move in board.run(player, adversary):
        render(window, board)


if __name__ == '__main__':
    try:
        # Initialize terminal settings
        curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()

        window = curses.newwin(BOARD_HEIGHT + 2, (BOARD_WIDTH + 2)*2+1)
        window.keypad(True)
        window.timeout(1000)

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
