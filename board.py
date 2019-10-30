from enum import Enum


class Direction(Enum):
    """
    Possible directions to move a block, plus dropping.
    """

    Left = 'LEFT'
    Right = 'RIGHT'
    Down = 'DOWN'
    Drop = 'DROP'


class Rotation(Enum):
    """
    Possible rotations available to the player.
    """

    Clockwise = 'CLOCKWISE'
    Anticlockwise = 'ANTICLOCKWISE'


class Shape(Enum):
    """
    Possible shapes of tetrominoes.
    """

    I = 'I'  # noqa
    J = 'J'
    L = 'L'
    O = 'O'  # noqa
    S = 'S'
    T = 'T'
    Z = 'Z'


# Translate names of shapes to initial coordinates.
shape_to_cells = {
    Shape.I: {
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
    },
    Shape.J: {
                (1, 0),
                (1, 1),
        (0, 2), (1, 2), # noqa
    },
    Shape.L: {
        (0, 0),
        (0, 1),
        (0, 2), (1, 2),
    },
    Shape.O: {
        (0, 0), (1, 0),
        (0, 1), (1, 1),
    },
    Shape.S: {
                (1, 0), (2, 0),
        (0, 1), (1, 1),
    },
    Shape.T: {
        (0, 0), (1, 0), (2, 0),
                (1, 1),
    },
    Shape.Z: {
        (0, 0), (1, 0),
                (1, 1), (2, 1),
    },
}


class Position:
    x = None
    y = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Bitmap:
    """
    Base class for classes that store information about cells.
    """

    cells = None

    def collides(self, other):
        return any(cell in other for cell in self)

    def __iter__(self):
        return iter(self.cells)

    def __contains__(self, cell):
        return cell in self.cells


class Block(Bitmap):
    """
    Keeps track of the position of cells of a block.
    """

    def __init__(self, shape):
        self.cells = shape_to_cells[shape]

    @property
    def left(self):
        """
        The leftmost x-position of the block.
        """

        return min(x for (x, y) in self)

    @property
    def right(self):
        """
        The rightmost x-position of the block.
        """

        return max(x for (x, y) in self)

    @property
    def top(self):
        """
        The topmost y-position of the block.
        """

        return min(y for (x, y) in self)

    @property
    def bottom(self):
        """
        The bottommost y-position of the block.
        """

        return max(y for (x, y) in self)

    @property
    def center_x(self):
        return self.left + (self.right - self.left) // 2

    def center(self, board):
        """
        Centers the block on the board.
        """

        shift = board.width // 2 - self.center_x
        self.cells = {(x+shift, y) for (x, y) in self}

    def supported(self, board):
        """
        Returns true if and only if the block is supported by the bottom of
        the board, or by another block. Basically, this means that moving the
        block down once more will mark it as dropped.
        """

        return any(
            (x, y+1) in board or y+1 == board.height
            for (x, y) in self
        )

    def move(self, direction, board, count=1):
        """
        Moves block count steps on on the board in the given direction. Returns
        true if this action caused the block to be dropped, false otherwise.
        """

        old_cells = self.cells
        if direction == Direction.Right:
            self.cells = {(x+count, y) for (x, y) in self}
            if self.right >= board.width or self.collides(board):
                # We hit something by moving; undo.
                self.cells = old_cells
            return False
        elif direction == Direction.Left:
            self.cells = {(x-count, y) for (x, y) in self}
            if self.left < 0 or self.collides(board):
                # We hit something by moving; undo.
                self.cells = old_cells
            return False
        elif direction == Direction.Down:
            if self.supported(board):
                # There is already something directly below the block; mark it
                # as dropped and do not move it.
                return True

            self.cells = {(x, y+count) for (x, y) in self}

            # Score a point for every row a block drops.
            board.score += 1

            return False
        elif direction == Direction.Drop:
            while not self.supported(board):
                self.move(Direction.Down, board)
            return True

    def rotate(self, rotation, board):
        """
        Rotates block in the given direction on the board. Returns true if this
        action caused the block to be dropped, false otherwise.
        """

        # Save cells so we can cancel later.
        old_cells = self.cells

        # Save the top-right bound before rotation
        (old_left, old_bottom) = (self.left, self.bottom)

        if rotation == Rotation.Clockwise:
            self.cells = {(-y, x) for (x, y) in self}
        elif rotation == Rotation.Anticlockwise:
            self.cells = {(y, -x) for (x, y) in self}

        # Reinstate old bottom-right bound after rotation.
        (new_left, new_bottom) = (self.left, self.bottom)
        self.cells = {
            (x-new_left+old_left, y-new_bottom+old_bottom)
            for (x, y) in self
        }

        # If block has hit left boundary, back off.
        left = self.left
        if left < 0:
            self.move(Direction.Right, board, -left)

        # Same for the right boundary.
        right = self.right
        if right >= board.width:
            self.move(Direction.Left, board, right-board.width+1)

        # Do not move beyond the top boundary either.
        top = self.top
        if top < 0:
            self.move(Direction.Down, board, -top)

        # Go back to old position if we overlap an existing cell.
        if self.collides(board):
            self.cells = old_cells
            return


class Board(Bitmap):
    """
    Class that keeps track of occupied cells and the current falling block,
    as well as the score of the player. Can be used to duplicate the current
    state and explore possible future moves.
    """

    width = None
    height = None
    score = None

    falling = None

    players_turn = None

    def __init__(self, width, height, score=0):
        self.width = width
        self.height = height
        self.score = score
        self.cells = set()

    def line_full(self, line):
        """
        Checks if the given line is fully occupied by cells.
        """

        return all((x, line) in self for x in range(0, self.width))

    def remove_line(self, line):
        """
        Removes all blocks on a given line and moves down all blocks above.
        """

        self.cells = {
            (x, y) if y > line else (x, y+1)
            for (x, y) in self if y != line
        }

    def clean(self):
        """
        Cleans all fully occupied lines from the bottom down, and moves lines
        above the cleaned lines down as well.
        """

        scores = [0, 100, 400, 800, 1600]
        removed = 0

        line = self.height-1
        while line > 0:
            while self.line_full(line):
                self.remove_line(line)
                removed += 1
            line -= 1

        return scores[removed]

    @property
    def alive(self):
        """
        Checks if the falling block has collided with another existing block.
        If this is true, then the game is over.
        """

        return self.falling is None or not self.falling.collides(self)

    def run_adversary(self, adversary):
        """
        Asks the adversary for a new block and places it on the board. Returns
        the shape of the newly placed block.
        """

        shape = adversary.move(self)
        self.falling = Block(shape)
        self.falling.center(self)
        return shape

    def run_player(self, player):
        """
        Asks the player for the next move and executes that on the board.
        Returns a tuple of a boolean and the move made, where the boolean
        indicates whether or not the current block has dropped.
        """

        move = player.move(self)

        # The player did not make a move.
        if move is None:
            return False, None

        landed = False
        if isinstance(move, Direction):
            landed = self.falling.move(move, self)
        elif isinstance(move, Rotation):
            self.falling.rotate(move, self)

        return landed, move

    def run(self, player, adversary):
        """
        Run the game with the given adversary and player. Will yield control
        back to the calling function every time a move has been made. Yields
        shapes (of new blocks) and moves (directions/rotations) as produced
        by the adversary or the player respectively.
        """

        # Let the adversary choose the first block.
        yield self.run_adversary(adversary)

        while self.alive:
            # The player's turn starts now.
            self.players_turn = True

            landed = False
            while not landed:
                # Ask the player for the next move to make.
                landed, choice = self.run_player(player)
                yield choice

            # End of the player's turn.
            self.players_turn = False

            # The block has fallen and becomes part of the cells on the board.
            self.cells |= self.falling.cells
            self.falling = None

            # Clean up any completed rows and adjust score.
            self.score += self.clean()

            # The adversary can now choose a new block.
            yield self.run_adversary(adversary)

    def move(self, direction):
        """
        Moves the current block in the direction given.
        """

        self.falling.move(direction, self)

    def rotate(self, rotation):
        """
        Rotates the current block as requested.
        """

        self.falling.rotate(rotation, self)

    def clone(self):
        """
        Creates a copy of the board; can be used to simulate possible moves.
        """

        board = Board(self.width, self.height, self.score)
        board.cells = {cell for cell in self}
        return board
