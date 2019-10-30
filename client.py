from adversary import RandomAdversary
from board import Board, Direction, Rotation, Shape
from constants import BOARD_HEIGHT, BOARD_WIDTH
from exceptions import UnknownInstructionException
from player import Player

from sys import stderr
from os import getenv


class RemotePlayer(Player):
    def move(self, board):
        try:
            instruction = input().strip()
        except EOFError:
            return

        try:
            return Direction(instruction)
        except ValueError:
            pass

        try:
            return Rotation(instruction)
        except ValueError:
            pass

        raise UnknownInstructionException


board = Board(BOARD_HEIGHT, BOARD_WIDTH)

player = RemotePlayer()
adversary = RandomAdversary(getenv('SEED'))


score = 0
for move in board.run(player, adversary):
    if isinstance(move, Shape):
        print(move.value)

    if board.score != score:
        stderr.write(f'{board.score}\n')
        score = board.score
