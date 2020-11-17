def test2(self, board):
        score = None
        for rotation in range(4):
            for horizontal_moves in range(board.width):
                cloned_board = board.clone()
                self.try_rotation(rotation, cloned_board)
                self.try_moves(horizontal_moves, cloned_board)
                calculated_score = self.calc_score(board,cloned_board)

                for second_rotation in range(4):
                    for second_horizontal_moves in range(board.width):
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



def choose_action(self, board):

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