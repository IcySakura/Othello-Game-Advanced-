# Myles Liu, yuxil11@uci.edu, 50997122


# Import


import copy
import itertools


# Classes

class GameState:
    '''This class is used to represent the current state of the game.
    I didn't create the board in this game logic file, since I didn't know what will creating board function or method
    be for the tkinter version, which is the next project. I created the board in a function in the interface file.'''


    def __init__(self, num_of_rows: int, num_of_columns: int, rule: int) -> None:
        '''This method is used to initialize the state.'''
        self._initialize_pieces()
        self._initialize_rules()
        self.num_of_rows = num_of_rows
        self.num_of_columns = num_of_columns
        self.rule = rule
        self.data = []


    def get_num_of_pieces(self, piece: int) -> int:
        '''Return the number of the exact piece on the current board.
         If the piece is 'B', it will be for black pieces.
         else if 'W', it will be for white pieces.'''
        return sum(row.count(piece) for row in self.board)


    def _initialize_pieces(self) -> None:
        '''This method is used to initialize all the pieces are represented by what.'''
        self.EMPTY = 0
        self.BLACK = 1
        self.WHITE = 2


    def _initialize_rules(self) -> None:
        '''More pieces to win is 1, less pieces to win is 2.'''
        self.MORE_WIN_RULE = 1
        self.LESS_WIN_RULE = 2


    def initialize_blank_board(self) -> None:
        self.board = [[self.EMPTY for column in range(self.num_of_columns)] for row in range(self.num_of_rows)]


    def initialize_board(self, rows: list) -> None:
        '''This function will create a board for the game.'''
        self.board = rows

    def initialize_player(self, player: int) -> None:
        self.current_player = player

    def save_data(self, board: list):
        '''This function is used to put the previous board into a list.'''
        self.data.append(copy.deepcopy(board))

    def undo_one_step(self):
        '''This function will make the board to one step before, if possible.'''
        if self.data:
            self.board = self.data.pop()
            self.current_player = get_opposite_player(self)


# Get list that contains new position


def _get_line_list(gamestate: GameState, position: list, option: bool) -> list:
    '''(The position first parameter is row, second is column.)
    Return a 2D list which the first parameter is a cell, and the second is the position of that cell.
    (The cell in the position input will be changed by the piece input).
    From left to right or from top to bottom.
    If the option is True, this function will return row.
    If False, return column.'''
    temp_board = _get_new_board(gamestate, position)
    result_list = []
    for num in range(len(temp_board[position[0]])) if option else range(len(temp_board)):
        result_list.append([temp_board[position[0]][num], [position[0], num]] if option
                           else [temp_board[num][position[1]], [num, position[1]]])
    return result_list


def _get_slash_list(gamestate: GameState, position: list, reverse: bool) -> list:
    '''(The position first parameter is row, second is column.)
    Return a 2D list which the first parameter is a cell, and the second is the position of that cell.
    (The cell in the position input will be changed by the piece input).
    From top to bottom.
    If the reverse is True the list will be from top right to bottom left,
    if False, from top left to bottom right.'''
    temp_board = _get_new_board(gamestate, position)
    result_list = []
    for num_of_row in reversed(range(gamestate.num_of_rows)) if reverse else range(gamestate.num_of_rows):
        index_number = position[1]-((num_of_row - position[0]) if reverse else (position[0] - num_of_row))
        if 0 <= index_number <= gamestate.num_of_columns - 1:
            result_list.append([temp_board[num_of_row][index_number], [num_of_row, index_number]])
    return result_list


# Functions for checking


def _check_position_assist(line: list, cell_list: list, index_number: int, list_of_range: list, option: bool) -> list:
    '''This function is used to assist the _check_position_in_list function for avoiding duplicating codes.
    If option is True, reverse the range, otherwise, not.'''
    mode = False
    wait_for_change = []
    for num in reversed(range(*list_of_range)) if option else range(*list_of_range):
        if not mode:
            if cell_list[num] == 0 or cell_list[num] == cell_list[index_number]:
                break
            elif cell_list[num] != cell_list[index_number]:
                mode = True
                wait_for_change.append(line[num][1])
        elif mode:
            if cell_list[num] == 0:
                break
            elif cell_list[num] == cell_list[index_number]:
                return wait_for_change
            else:
                wait_for_change.append(line[num][1])
    return []



def _check_position_in_list(line: list, position: list) -> list:
    '''The list will be one line that given by one of the two functions in Get list that contains new position part.
    (The position first parameter is row, second is column.)
    This function will check whether the position is legal in the list.
    If legal, the function will return all the positions of cells that need to be changed in a list.
    Otherwise, the list will be empty.'''
    cell_list = [cell_info[0] for cell_info in line]
    index_number = [cell_info[1] for cell_info in line].index(position)
    return (_check_position_assist(line, cell_list, index_number, [0, index_number], True) +
            _check_position_assist(line, cell_list, index_number, [index_number + 1, len(cell_list)], False))


def _check_one_piece(gamestate: GameState, position: list) -> list:
    '''This function will check whether one position is legal for one piece to place.
    If legal, the function will return all the positions of cells that need to be changed in a list.
    Otherwise, the list will be empty.'''
    result_list = sorted(_check_position_in_list(_get_line_list(gamestate, position, True), position) +
                         _check_position_in_list(_get_line_list(gamestate, position, False), position) +
                         _check_position_in_list(_get_slash_list(gamestate, position, True), position) +
                         _check_position_in_list(_get_slash_list(gamestate, position, False), position))
    return [result_list for result_list, _ in itertools.groupby(result_list)]


# Function About getting Value for Legal Position


def get_all_possibilities(gamestate: GameState) -> list:
    '''Using the current gamestate to get all the possible positions to move for the exact piece input,
    and then return them in a list.'''
    possible_positions = []
    for index_of_row in range(len(gamestate.board)):
        for index_of_column in range(len(gamestate.board[index_of_row])):
            if gamestate.board[index_of_row][index_of_column] == 0:
                position = [index_of_row, index_of_column]
                positions_for_change = _check_one_piece(gamestate, position)
                if positions_for_change:
                    possible_positions.append([position, positions_for_change])
    return possible_positions


# Other Core Functions


def _get_new_board(gamestate: GameState, position: list) -> list:
    '''This function will build a new board with one cell changed by the position and piece input.
    Then return the new board.'''
    new_board = copy.deepcopy(gamestate.board)
    new_board[position[0]][position[1]] = gamestate.current_player
    return new_board


def make_move(gamestate: GameState, positions_to_change: list) -> GameState:
    '''This function will change the board by the position and piece input, and then return the changed gamestate.
    Actually I don't need to check the positions to change since if my program runs properly, the MoveError should never be raised.
    But the professor says that we should check any parameter and raise an error if there is something wrong.'''
    try:
        gamestate.save_data(gamestate.board)
        gamestate.board[positions_to_change[0][0]][positions_to_change[0][1]] = gamestate.current_player
        for position in positions_to_change[1]:
            gamestate.board[position[0]][position[1]] = gamestate.current_player
        return gamestate
    except:
        raise MoveError



def get_opposite_player(gamestate: 'GameState') -> int:
    '''This function will return the opposite player of the current player input.'''
    if gamestate.current_player == gamestate.BLACK:
        return gamestate.WHITE
    else:
        return gamestate.BLACK


def get_winner(gamestate: GameState) -> int:
    '''This function will return a winner by the gamestate and the rule input. 0 means draw.'''
    black_pieces = gamestate.get_num_of_pieces(gamestate.BLACK)
    white_pieces = gamestate.get_num_of_pieces(gamestate.WHITE)
    if black_pieces > white_pieces:
        if gamestate.rule == gamestate.MORE_WIN_RULE:
            return gamestate.BLACK
        else:
            return gamestate.WHITE
    elif black_pieces < white_pieces:
        if gamestate.rule == gamestate.MORE_WIN_RULE:
            return gamestate.WHITE
        else:
            return gamestate.BLACK
    else:
        return gamestate.EMPTY


# Exceptions


class MoveError(Exception):
    '''This error will be raised if the user is trying to make an invalid moce.'''
    pass

