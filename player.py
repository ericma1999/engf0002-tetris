from board import Direction, Rotation
from random import Random
from time import sleep
from exceptions import NoBlockException


class Player:
    def choose_action(self, board):
        raise NotImplementedError



class MyPlayer(Player):
    # heuristic constants
    heightConstant = -0.510066
    linesConstant = 0.960666
    holesConstant = -0.35663
    bumpinessConstant = -0.184483

    best_horizontal_position = None
    best_rotation_position = None

    def __init__(self, seed=None):
        self.random = Random(seed)

    def generate_column_height(self, board):
        columns = [0] * board.width
        # take only the highest value of y into consideration
        # start from bottom of y
        for y in reversed(range(board.height)):
            for x in range(board.width):
                if (x,y) in board.cells:
                    height = abs(board.height - y)
                    columns[x] = height
        return columns

    def check_height(self,board):
        return sum(self.generate_column_height(board)) * self.heightConstant
    
    def check_bumpiness(self, board):
        total = 0
        columns = self.generate_column_height(board)
        for i in range(9):
            total += abs(columns[i] - columns[i+1])
        return total * self.bumpinessConstant

    def check_lines(self, originalBoard, board):
        # not sure if this is correct
        score = board.score - originalBoard.score
        complete_line = 0
        # points given
        if score >= 1600:
            complete_line += 4
        elif score >= 800:
            complete_line += 3
        elif score >= 400:
            complete_line += 2
        elif score >= 100:
            complete_line += 1
        return complete_line * self.linesConstant
    
    def check_holes(self, board):
        holes = 0
        for x in range(board.width):
            for y in range(board.height):
                if (x, y) not in board.cells:
                    if (x + 1,y) in board.cells and (x - 1,y) in board.cells and (x, y+1) in board.cells and (x, y-1) in board.cells:
                        holes += 1
        return self.holesConstant * holes

    def calc_score(self, originalBoard, board):
        total = self.check_height(board) + self.check_holes(board) + self.check_lines(originalBoard, board) + self.check_bumpiness(board)
        return total

    def simulate_best_position(self, board):
        score = None

        for rotation in range(0, 4):
            for horizontal_moves in range(0, board.width):
                cloned_board = board.clone()
                for _ in range(0, rotation):
                    try:
                        cloned_board.rotate(Rotation.Anticlockwise)
                    except NoBlockException:
                        pass
                # 4 here since the board spawns the shape at 6 and not in center ***
                move = 4 - horizontal_moves
                if (move >= 0):
                    for _ in range(0, move):
                        try:
                            cloned_board.move(Direction.Right)
                        except NoBlockException:
                            pass
                else:
                    for _ in range(0, abs(move)):
                        try:
                            cloned_board.move(Direction.Left)
                        except NoBlockException:
                            pass
                try:
                    cloned_board.move(Direction.Drop)
                except NoBlockException:
                    pass

                calculated_score = self.calc_score(board,cloned_board)

                if (score is None):
                    score = calculated_score
                    self.best_rotation_position = rotation
                    self.best_horizontal_position = move
                
                if (calculated_score > score):
                    self.best_rotation_position = rotation
                    score = calculated_score
                    self.best_horizontal_position = move
    
    def generate_moves(self):
        generated_moves = []
        for _ in range(0, self.best_rotation_position):
            generated_moves.append(Rotation.Anticlockwise)
        if (self.best_horizontal_position < 0):
            for _ in range(0, abs(self.best_horizontal_position)):
                generated_moves.append(Direction.Left)
        else:
            for _ in range(0, self.best_horizontal_position):
                generated_moves.append(Direction.Right)
        generated_moves.append(Direction.Drop)

        return generated_moves
    

    def choose_action(self, board):

        self.simulate_best_position(board)
        return self.generate_moves()



class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def choose_action(self, board):
        return self.random.choice([
            Direction.Left,
            Direction.Right,
            Direction.Down,
            Rotation.Anticlockwise,
            Rotation.Clockwise,
        ])


SelectedPlayer = MyPlayer
