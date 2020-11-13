from board import Direction, Rotation, Shape, shape_to_cells
from random import Random
from time import sleep
from exceptions import NoBlockException


class Player:
    def choose_action(self, board):
        raise NotImplementedError
class MyPlayer(Player):
    # heuristic constants
    heightConstant = -0.510066
    linesConstant = 1.260666
    holesConstant = -0.35663
    meanHeightConstant = -0.66
    bumpinessConstant = -0.184483

    next_is_I = False

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

    def check_mean_height(self,board):
        return sum(self.generate_column_height(board)) / 10 * self.meanHeightConstant

    def check_height(self,board):
        return sum(self.generate_column_height(board)) * self.heightConstant
    
    def check_bumpiness(self, board):
        total = 0
        columns = self.generate_column_height(board)
        for i in range(9):
            total += abs(columns[i] - columns[i+1])
        return total * self.bumpinessConstant

    def check_lines(self, originalBoard, board):
        score = board.score - originalBoard.score
        complete_line = 0
        # points given
        if score >= 1600:
            complete_line += 4
            return complete_line * self.linesConstant
        elif score >= 800:
            complete_line += 3
            return complete_line * (self.linesConstant / 2)
        elif score >= 400:
            complete_line += 2
            return complete_line * (self.linesConstant / 3)
        elif score >= 100:
            complete_line += 1
            return complete_line * (self.linesConstant / 4)
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
        #  + self.check_mean_height(board)
        return total


    def try_rotation(self,rotation, board):
        for _ in range(rotation):
                    try:
                        board.rotate(Rotation.Anticlockwise)
                    except NoBlockException:
                        pass
    def try_moves(self, moves, board):
    # 4 here since the board spawns the shape at 6 and not in center ***
            move = 4 - moves
            if (move >= 0):
                for _ in range(move):
                    try:
                        board.move(Direction.Right)
                    except NoBlockException:
                        pass
            else:
                for _ in range(abs(move)):
                    try:
                        board.move(Direction.Left)
                    except NoBlockException:
                        pass
            try:
                board.move(Direction.Drop)
            except NoBlockException:
                pass

    def check_shape_is_I(self, cells):
        is_I = True
        for (x,y) in cells:
            if (x,y) not in {(5,1), (5,2), (5,0), (5,3)}:
                is_I = False
        return is_I

    def simulate_best_position(self, board):
        score = None
        for rotation in range(4):
            should_break = False
            for horizontal_moves in range(board.width):
                cloned_board = board.clone()
                should_break = False
                if self.check_shape_is_I(cloned_board.falling.cells):
                    print(True)
                    self.next_is_I = True
                    should_break = True
                    break
                self.try_rotation(rotation, cloned_board)
                self.try_moves(horizontal_moves, cloned_board)

                calculated_score = self.calc_score(board,cloned_board)

                if (score is None):
                    score = calculated_score
                    self.best_rotation_position = rotation
                    self.best_horizontal_position = 4 - horizontal_moves
                
                if (calculated_score > score):
                    best_board = cloned_board
                    self.best_rotation_position = rotation
                    score = calculated_score
                    self.best_horizontal_position = 4 - horizontal_moves
        if (self.next_is_I):
            self.next_is_I = False
            cloned_board = board.clone()
            for _ in range(4):
                board.move(Direction.Right)
            cloned_board.move(Direction.Drop)
            right_score = self.calc_score(board, cloned_board)
            cloned_board = board.clone()
            for _ in range(5):
                cloned_board.move(Direction.Left)
            cloned_board.move(Direction.Drop)
            left_score = self.calc_score(board, cloned_board)

            print("left score", left_score)
            print("right score", right_score)
            if left_score > right_score:
                self.best_horizontal_position = 4
            else:
                self.best_horizontal_position = -5
            self.best_rotation_position = 0
            return
    
    def generate_moves(self):
        generated_moves = []
        for _ in range(self.best_rotation_position):
            generated_moves.append(Rotation.Anticlockwise)
        if (self.best_horizontal_position < 0):
            for _ in range(abs(self.best_horizontal_position)):
                generated_moves.append(Direction.Left)
        else:
            for _ in range(self.best_horizontal_position):
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
