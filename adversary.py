from random import Random
from board import Shape


class Adversary:
    def move(self, board):
        raise NotImplementedError


class RandomAdversary(Adversary):
    def __init__(self, seed):
        self.random = Random(seed)

    def move(self, board):
        return self.random.choice(list(Shape))
