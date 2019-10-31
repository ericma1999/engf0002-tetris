from adversary import RandomAdversary
from board import Board, Direction, Rotation, Shape
from constants import BOARD_HEIGHT, BOARD_WIDTH, BLOCK_LIMIT
from exceptions import UnknownInstructionException, BlockLimitException
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


board = Board(BOARD_WIDTH, BOARD_HEIGHT)

player = RemotePlayer()
adversary = RandomAdversary(getenv('SEED'), BLOCK_LIMIT)


score = 0
try:
    for move in board.run(player, adversary):
        if isinstance(move, Shape):
            print(move.value)

        if board.score != score:
            stderr.write(f'{board.score}\n')
            score = board.score
except BlockLimitException:
    print('END')
