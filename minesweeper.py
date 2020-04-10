"""
A simple recreation of minesweeper to be played in the console.
by: Derek Thompson, Copyright 2020 under GPLv3
"""

# TODO: Update comments and variable names to be have consistent wording
from dataclasses import dataclass, field
from typing import List, Set, Tuple
import random

DEFAULT_BOARD_WIDTH = 9
DEFAULT_BOARD_HEIGHT = 9
DEFAULT_MINE_COUNT = 10
UNCHECKED_SPACE = '▓'
EMPTY_SPACE = '░'
MINE = '*'


@dataclass
class Cell():
    """
    Contains the character located at the cell and a boolean
    stating if the cell has been revealed or not
    """
    character: str = field(default=EMPTY_SPACE)
    revealed: bool = field(default=False)


# custom cells datatype for type hints
Cells = List[Cell]


@dataclass
class Board():
    """
    Contains all of the data relevant to the game board:
    cells: List of characters representing the board
    mine_locations: Set of (x, y) tuples for all mine locations
    width: integer representing board width
    height: integer representing board height
    number_of_mines: integer representing the number of mines on the board

    """
    cells: Cells = field(init=False, repr=False)
    mine_locations: Set[Tuple[int, int]] = field(default_factory=set)
    width: int = field(default=DEFAULT_BOARD_WIDTH)
    height: int = field(default=DEFAULT_BOARD_HEIGHT)
    number_of_mines: int = field(default=DEFAULT_MINE_COUNT)

    def __post_init__(self):
        """
        Initializes the cells on the board based on the provided witdh, height
        and mine count
        """

        # initialize all cells to be empty
        self.cells = [Cell() for i in range(self.width * self.height)]

        # randomly place mines throughout the board
        for i in range(self.number_of_mines):
            x = y = -1
            while x < 0 or y < 0 or (x, y) in self.mine_locations:
                x = random.randrange(0, self.width)
                y = random.randrange(0, self.height)
            self.mine_locations.add((x, y))
            self.cells[y*self.width+x].character = MINE

        self.fill_board_with_numbers()

    def display_board(self):
        """
        prints out current state of the board
        Example:
            A B C D E
            ┌─┬─┬─┬─┬─┐
          1 │ │ │1│░│░│
            ├─┼─┼─┼─┼─┤
          2 | | |2|1|1|
            ├─┼─┼─┼─┼─┤
          3 | | | | | |
            ├─┼─┼─┼─┼─┤
          4 | | | | | |
            ├─┼─┼─┼─┼─┤
          5 │ │ │ │ │ │
            └─┴─┴─┴─┴─┘
        """
        for y in range(self.height):
            for x in range(self.width):
                print(self.cells[y*self.width+x].character, end='')
            print('')

    def fill_board_with_numbers(self):
        """
        Marks all cells adjacent to mines with the number of mines
        adjacent to the cell
        """

        # The 8 cells adjacent to the current cells starting from the left
        # square then moving clockwise
        adjacent_positions = (
                              (-1, 0),
                              (-1, -1),
                              (0, -1),
                              (1, -1),
                              (1, 0),
                              (1, 1),
                              (0, 1),
                              (-1, 1)
                             )
        x_tuple_position = 0
        y_tuple_position = 1

        # Loop over all cells with a mine and cells adjacent to each mine
        for mine_location in self.mine_locations:
            for position in adjacent_positions:
                # First calculate the cell position according to the mine
                adjacent_x_position = mine_location[x_tuple_position] +\
                    position[x_tuple_position]
                adjacent_y_position = mine_location[y_tuple_position] +\
                    position[y_tuple_position]

                # if the adjacent cell falls outside of the bounds of the board
                # dont do anything with it
                if adjacent_x_position < 0 or \
                   adjacent_y_position < 0 or \
                   adjacent_x_position >= self.width or \
                   adjacent_y_position >= self.height:
                    continue

                # get the character at the adjacent position being checked
                cell = self.get_cell(adjacent_x_position, adjacent_y_position)
                # if the character is an EMPTY_SPACE then make it a '1'
                if cell == EMPTY_SPACE:
                    cell = '1'
                # else if the character is a MINE then do move to next square
                elif cell == MINE:
                    continue
                # otherwise increase the number and change the character
                # to the new number
                else:
                    cell = str(int(cell) + 1)

                # update the cells list with the new character
                self.cells[adjacent_y_position *
                           self.width+adjacent_x_position].character = cell

    def get_cell(self, x, y):
        """
        returns the character located at the provided x, y
        """
        return self.cells[y*self.width+x].character

    def reveal_cell(self, x, y):
        """
        reveals the cell logically so the drawing class can draw the cell
        """
        self.cells[y*self.width+x].revealed = True


@dataclass
class Display():
    """
    Handles displaying the board based on the state of all cells
    """

    def display_board(self, board: Cells, board_width, board_height):
        if not len(board):
            return
        for y in range(board_height):
            for x in range(board_width):
                cell = board[y*board_width+x]
                if cell.revealed:
                    print(cell.character, end='')
                else:
                    print(UNCHECKED_SPACE, end='')
            print()


@dataclass
class Controller():
    """
    Controls all logic of the game from updating the board
    to notifying the display class to draw the game
    """
    board: Board = field(default_factory=Board)

    def new_game(self, width, height, num_mines):
        """
        initializes and returns True with the provided parameters
        if they are in the correct range otherwise prints an error message
        and returns False
        """
        MIN_BOARD_WIDTH = 9
        MAX_BOARD_WIDTH = 30
        MIN_BOARD_HEIGHT = 9
        MAX_BOARD_HEIGHT = 24
        MIN_MINE_COUNT = 10
        MAX_MINE_COUNT = 668
        MIN_MINE_COUNT = 10
        MAX_MINE_COUNT = (width - 1) * (height - 1)

        # Create the board if all provided parameters fall within the min and
        # max thresholds. Otherwise print the thresholds and don't create the
        # board
        if width >= MIN_BOARD_WIDTH and width <= MAX_BOARD_WIDTH and\
                height >= MIN_BOARD_HEIGHT and height <= MAX_BOARD_HEIGHT and\
                num_mines >= MIN_MINE_COUNT and num_mines <= MAX_MINE_COUNT\
                and num_mines >= MIN_MINE_COUNT and\
                num_mines <= MAX_MINE_COUNT:

            self.board = Board(
                width=width,
                height=height,
                number_of_mines=num_mines
            )
            print("New Game!")
            return True
        else:
            print(f"Invalid board setup: {width}x{height} {num_mines}")
            print(f"Height range: {MIN_BOARD_HEIGHT}-{MAX_BOARD_HEIGHT}")
            print(f"Width range: {MIN_BOARD_WIDTH}-{MAX_BOARD_WIDTH}")
            print(f"Mine range for board size: {MIN_MINE_COUNT}-{MAX_MINE_COUNT}")
            self.board = None
            return False


if __name__ == "__main__":
    game = Controller()
    display = Display()
    game.new_game(9, 9, 10)
    for i in range(10):
        x = random.randrange(0, game.board.width)
        y = random.randrange(0, game.board.height)
        game.board.cells[y*game.board.width+x].revealed = True
    game.board.display_board()
    print(game.board)
    display.display_board(
        board=game.board.cells,
        board_width=game.board.width,
        board_height=game.board.height
    )
