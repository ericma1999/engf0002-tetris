from adversary import Adversary
from board import Board, Direction, Rotation, Shape
from constants import BOARD_HEIGHT, BOARD_WIDTH
from exceptions import UnknownInstructionException
from player import SelectedPlayer


class RemoteAdversary(Adversary):
    def move(self, board):
        try:
            command = input().strip()
        except EOFError:
            return

        if command == 'END':
            # Adversary reached the block limit; stop cleanly.
            raise SystemExit

        try:
            return Shape(command)
        except ValueError:
            pass

        raise UnknownInstructionException


board = Board(BOARD_HEIGHT, BOARD_WIDTH)

player = SelectedPlayer()
adversary = RemoteAdversary()

for move in board.run(player, adversary):
    if isinstance(move, Direction):
        print(move.value)
    elif isinstance(move, Rotation):
        print(move.value)
