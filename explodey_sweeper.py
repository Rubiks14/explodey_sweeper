"""
A simple recreation of minesweeper to be played in the console.
"""

# TODO: Update comments and variable names to be have consistent wording
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set, Tuple
import random

DEFAULT_BOARD_WIDTH = 9
DEFAULT_BOARD_HEIGHT = 9
DEFAULT_MINE_COUNT = 10
UNCHECKED_SPACE = '▓'
EMPTY_SPACE = '░'
MINE = '*'
FLAG = 'φ'

# The 8 cells adjacent to the current cells starting from the left
# square then moving clockwise
adjacent_cells = (
    (-1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1)
)


class State(Enum):
    """
    Contains all of the states for the game
    """
    PLAYING = "play"
    PLAYER_WON = "win"
    PLAYER_LOST = "lost"


@dataclass
class Cell():
    """
    Contains the character located at the cell and a boolean
    stating if the cell has been revealed or not
    """
    character: str = field(default=EMPTY_SPACE)
    revealed: bool = field(default=False)
    flagged: bool = field(default=False)


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

    def fill_board_with_numbers(self):
        """
        Marks all cells adjacent to mines with the number of mines
        adjacent to the cell
        """
        x_tuple_position = 0
        y_tuple_position = 1

        # Loop over all cells with a mine and cells adjacent to each mine
        for mine_location in self.mine_locations:
            for position in adjacent_cells:
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
                cell = self.get_cell_character(
                    adjacent_x_position,
                    adjacent_y_position
                )
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

    def get_cell_character(self, x, y):
        """
        returns the character located at the provided x, y
        """
        return self.cells[y*self.width+x].character

    def is_revealed(self, x, y):
        """
        returns True if the cell at the provided (x,y) is revealed or false
        otherwise
        """
        return self.cells[y*self.width+x].revealed

    def reveal_cell(self, x, y):
        """
        reveals the cell logically so the drawing class can draw the cell
        """
        cell = self.cells[y*self.width+x]
        cell.revealed = True
        if cell.character == EMPTY_SPACE:
            self.reveal_surrounding_cells(x, y)

    def reveal_all_mines(self):
        """
        reveals all of the mines on the board
        """
        for mine_cell in self.mine_locations:
            self.cells[mine_cell[1]*self.width+mine_cell[0]].revealed = True

    def reveal_surrounding_cells(self, starting_x, starting_y):
        """
        Reveals all empty spaces and numbered spaces around an empty space
        """

        # The list of cells to move to next
        next_cells = list()
        # Loop through all cells adjacent to the current cell
        for adjacent_cell in adjacent_cells:
            x = starting_x + adjacent_cell[0]
            y = starting_y + adjacent_cell[1]
            # if the cell would be off of the board don't do anything with it
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                continue

            cell = self.cells[y*self.width+x]
            # if the cell is no revealed and it's a blank space
            # then reveal it and add it to the list to use as the centerpoint
            if cell.character == '░' and not cell.revealed:
                cell.revealed = True
                next_cells.append((x, y))
            # otherwise if the cell is not a mine then reveal it and don't
            # add it to the list of cells to be center points
            elif cell.character != '*':
                cell.revealed = True

            # loop through all revealed empty cells and reveal the cells
            # around them
            for cell in next_cells:
                self.reveal_surrounding_cells(cell[0], cell[1])

    def is_flagged(self, x, y):
        """
        Returns True or False depending on if the cell is flagged
        """
        return self.cells[y*self.width+x].flagged

    def flag_cell(self, x, y):
        """
        Flags the cell logically so that the flag can be drawn and logic
        can be used to determine if the player has won the game
        """
        self.cells[y*self.width+x].flagged = True


@dataclass
class Display():
    """
    Handles displaying the board based on the state of all cells
    """

    def display_board(self, board: Board):
        """
        Displays the contents of the board based on if the cell is revealed
        or not
        """
        # We don't want to try and work with an empty list
        if not len(board.cells):
            return

        # Print the x positions on the board
        x_pos = '0'
        print('  ', end='')
        for i in range(board.width):
            print(x_pos, end='')
            if ord(x_pos) < ord('9'):
                x_pos = str(int(x_pos) + 1)
            elif ord(x_pos) == ord('9'):
                x_pos = 'a'
            else:
                x_pos = chr(ord(x_pos) + 1)
        print()

        # Loop through x and y positions then check each cell
        # at the positions to see if they are revealed or not
        # if they are then print the cell otherwise print the
        # not revealed character
        y_pos = '0'
        for y in range(board.height):
            # print the y positions of the board
            print(f"{y_pos} ", end='')
            for x in range(board.width):
                cell = board.cells[y*board.width+x]
                if cell.revealed:
                    print(cell.character, end='')
                elif cell.flagged:
                    print(FLAG, end='')
                else:
                    print(UNCHECKED_SPACE, end='')

            if ord(y_pos) < ord('9'):
                y_pos = str(int(y_pos) + 1)
            elif ord(y_pos) == ord('9'):
                y_pos = 'a'
            else:
                y_pos = chr(ord(y_pos) + 1)
            print()

    def debug_display(self, board: Cells, board_width, board_height):
        """
        Displays the contents of the board based on if the cell is revealed
        or not
        """
        # We don't want to try and work with an empty list
        if not len(board):
            return

        # Loop through x and y positions then check each cell
        # at the positions to see if they are revealed or not
        # if they are then print the cell otherwise print the
        # not revealed character
        for y in range(board_height):
            for x in range(board_width):
                cell = board[y*board_width+x]
                print(cell.character, end='')
            print()


@dataclass
class Controller():
    """
    Controls all logic of the game from updating the board
    to notifying the display class to draw the game
    """

    class Move_Mode(Enum):
        REVEAL = 0
        FLAG = 1

    board: Board = field(default_factory=Board)
    current_state: State = field(default=State.PLAYING)
    mode: Move_Mode = field(default=Move_Mode.REVEAL)

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
            print("New Game!\n")
            return True
        else:
            print(f"Invalid board setup: {width}x{height} {num_mines}")
            print(f"Height range: {MIN_BOARD_HEIGHT}-{MAX_BOARD_HEIGHT}")
            print(f"Width range: {MIN_BOARD_WIDTH}-{MAX_BOARD_WIDTH}")
            print(f"Mine range for board size: {MIN_MINE_COUNT}-{MAX_MINE_COUNT}")  # noqa: E501
            self.board = None
            return False

    def convert_move_to_xy(self, col, row):
        """
        Gets the move from the user and returns (x, y)
        """
        x = -1
        y = -1

        # if the unicode for the entered column is less than
        # the unicode for the character '9' then set x to the
        # integer representation of column
        if ord(col) >= ord('0') and ord(col) <= ord('9'):
            x = int(col)

        # the character is set to 10 + the difference between the unicode
        # for the entered character minus the unicode for the character 'a'
        # example: col = 'c', ord(col) = 99, ord('a') = 97
        # 99 - 97 = 2 + 10 = 12 for column 12
        # really column 13 since counting starts from 0
        else:
            x = int(ord(col) - ord('a') + 10)

        # Same thing as before for the row
        if ord(row) >= ord('0') and ord(row) <= ord('9'):
            y = int(row)
        else:
            y = int(ord(row) - ord('a') + 10)

        return (x, y)

    def process_move(self, x, y):
        """
        processes the player's move
        """
        if self.mode == self.Move_Mode.REVEAL:
            # Don't let the player reveal a cell that is already revealed
            if self.board.is_revealed(x, y):
                print(f"Invalid Move: Cell ({x}, {y}) is already revealed")
            # otherwise if the cell is a mine then reveal all mines and set
            # game state to lost
            elif self.board.get_cell_character(x, y) == MINE:
                self.board.reveal_all_mines()
                self.current_state = State.PLAYER_LOST
            # otherwise reveal the cell and potentially other cells around it
            else:
                self.board.reveal_cell(x, y)
        elif self.mode == self.Move_Mode.FLAG:
            if self.board.is_revealed(x, y):
                print(print(f"Invalid Move: Cell ({x}, {y}) is already revealed"))  # noqa: E501
            else:
                self.board.flag_cell(x, y)


if __name__ == "__main__":
    game = Controller()
    display = Display()
    game.new_game(12, 12, 15)
    while game.current_state == State.PLAYING:
        display.display_board(game.board)
        mode = input("Enter selection mode (reveal, flag, quit): ")
        if mode.lower() == "reveal":
            game.mode = game.Move_Mode.REVEAL
        elif mode.lower() == "flag":
            game.mode = game.Move_Mode.FLAG
        elif mode.lower() == "quit":
            break
        move = input("Enter a cell to reveal: ")
        move = [char for char in move]
        move = game.convert_move_to_xy(move[0], move[1])
        if move[0] >= 0 and move[0] < game.board.width and\
                move[1] >= 0 and move[1] < game.board.height:
            game.process_move(move[0], move[1])
        else:
            print("Please enter a position on the board")
    display.display_board(game.board)
    print("YOU LOST!")
