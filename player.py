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
    holesConstant = -0.35663
    bumpinessConstant = -0.184483

    moves = 0

    best_horizontal_position = None
    best_rotation_position = None

    second_move = None
    second_rotation = None

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
    
    def check_min_max_difference(self, board):
        columns = self.generate_column_height(board)

        return max(columns) - min(columns) * -0.3466

    
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
        self.moves +=1
        print("moves", self.moves)
        upper_bound = 10
        lower_bound = 2
        columns = self.generate_column_height(board)
        more_than_four = [column for column in columns if column >= 4]
        moure_than_eight = [column for column in columns if column >= 6]
        print(sum(columns) / len(columns))
        avg = sum(columns) / 8
        if(len(more_than_four) >= 6 or avg > 3.8 or len(moure_than_eight) >= 2):
            upper_bound = 10
            lower_bound = 0
            self.holesConstant = -0.55663 
            self.heightConstant = -0.610066
        else:
            self.holesConstant = -2.0
            self.heightConstant = -0.14
            upper_bound = 10
            lower_bound = 3

        for rotation in range(4):
            for horizontal_moves in range(lower_bound, upper_bound):
                cloned_board = board.clone()
                self.try_rotation(rotation, cloned_board)
                self.try_moves(horizontal_moves, cloned_board)
                calculated_score = self.calc_score(board,cloned_board)

                for second_rotation in range(4):
                    for second_horizontal_moves in range(lower_bound, upper_bound):
                        second_board = cloned_board.clone()
                        self.try_rotation(second_rotation, second_board)
                        self.try_moves(second_horizontal_moves, second_board)

                        calc_second_score = self.calc_score(cloned_board, second_board)
                        if score is None:
                            score = calc_second_score + calculated_score
                            self.second_rotation = second_rotation
                            self.second_move = 4 - second_horizontal_moves
                            self.best_horizontal_position = 4 - horizontal_moves
                            self.best_rotation_position = rotation

                        if calc_second_score + calculated_score > score:
                            score = calc_second_score + calculated_score
                            self.second_rotation = second_rotation
                            self.second_move = 4 - second_horizontal_moves
                            self.best_horizontal_position = 4 - horizontal_moves
                            self.best_rotation_position = rotation
    
    def generate_moves(self, rotation, move):
        generated_moves = []
        for _ in range(rotation):
            generated_moves.append(Rotation.Anticlockwise)
        if (move < 0):
            for _ in range(abs(move)):
                generated_moves.append(Direction.Left)
        else:
            for _ in range(move):
                generated_moves.append(Direction.Right)
        generated_moves.append(Direction.Drop)

        return generated_moves
    

    def choose_action(self, board):
        self.moves += 1
        if (self.moves == 400):
            raise "Test"
        print("moves", self.moves)
        if (self.second_move is not None and self.second_rotation is not None):
            print("if")
            print(self.second_move)

            rotation = self.second_rotation
            move = self.second_move
            self.second_move = None
            self.second_rotation = None
            return self.generate_moves(rotation, move)
        else:
            print("else")
            self.simulate_best_position(board)
            return self.generate_moves(self.best_rotation_position, self.best_horizontal_position)



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
