from board import Direction, Rotation
from random import Random
from time import sleep
from exceptions import NoBlockException

# references
# https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
class Player:
    def choose_action(self, board):
        raise NotImplementedError
class MyPlayer(Player):
    # heuristic constants
    heightConstant = -0.510066
    linesConstant = 1.260666
    holesConstant = -0.55663
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
        score = board.score - originalBoard.score
        complete_line = 0
        # points given
        if score >= 1600:
            complete_line += 4
        elif score >= 800:
            complete_line += 3
        elif score >= 400:
            complete_line += 2
        # elif score >= 100:
        #     complete_line += 1
        return complete_line * self.linesConstant

    
    def check_holes(self, board):
        columns = self.generate_column_height(board)
        tally = [0] * 10 
        for x in range(board.width):
            for y in range(board.height - columns[x], board.height):
                if (x, y) not in board.cells:
                        tally[x] += 1
        return self.holesConstant * sum(tally)

    def check_wells(self, board):
        columns = self.generate_column_height(board)
        tally = [0] * 10 
        for x in range(board.width):
            for y in range(board.height - columns[x], board.height):
                if(x,y) not in board.cells:
                    tally[x] += 1
        return max(tally) * self.holesConstant

    def calc_score(self, originalBoard, board):
        total = self.check_height(board) + self.check_holes(board) + self.check_lines(originalBoard, board) + self.check_bumpiness(board) + self.check_wells(board)
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

    def simulate_best_position(self, board):
        score = None
        previous_rotation = None
        previous_move = None

        for rotation in range(4):
            for horizontal_moves in range(board.width):
                cloned_board = board.clone()
                print("firt shape",cloned_board.falling.cells)
                temp_previous_rotation = None
                temp_previous_move = None
                for i in range(2):
                    self.try_rotation(rotation, cloned_board)
                    self.try_moves(horizontal_moves, cloned_board)
                    
                    if (i == 0 and score is None):
                        
                        previous_rotation = rotation
                        previous_move = 4 - horizontal_moves
                        temp_previous_rotation = None
                        temp_previous_move = None

                    if i == 0:
                        temp_previous_move = 4 - horizontal_moves
                        temp_previous_rotation = rotation
                        # print("next shape",cloned_board.falling.cells)


                    if (i == 1):
                        calculated_score = self.calc_score(board, cloned_board)
                        if (score is None):
                            score = calculated_score
                            self.best_rotation_position = previous_rotation
                            self.best_horizontal_position = previous_move
                
                        if (calculated_score > score):
                            score = calculated_score
                            previous_rotation = temp_previous_rotation
                            previous_move = temp_previous_move
            self.best_horizontal_position = previous_move
            self.best_rotation_position = previous_rotation
    
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
