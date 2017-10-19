# Myles Liu, yuxil11@uci.edu, 50997122
# Current Process: Level 2-E4 (1 - 4)
# Rule: Only for the player with the most discs on the board at the end of the game wins.
# Level 1: Think about 1 step, and give the move that has the most benefit. (Easy Level added)
# Level 2-A: Can first get the corner, and avoid the user to get the corner.
# Level 2-B: Think about 2 step, and give the move that has the most benefit. (Normal Level added)
# Level 2-C: In some special conditions, the ai will get the positions around the corners.
# Level 2-D: In some conditions, the score of one move may be used to calculate the best move.
# Level 2-E: In most of conditions, the score of one move will be used to calculate the best move.
# Level 2-E2: Some small improvement and bugs fixed.
# Level 2-E3: Bugs fixed.
# Level 2-E4: More bugs fixed.
# Level 3: Combine all the calculation together, and give the move that has the most benefit.(Hard Level probably will be added)
# Level 4: (Probably Master level)(Master Level probably will be added)

# Last update: 02/28/2017
# Last modified: 03/12/2017


# Import


import copy
import module_othello
from multiprocessing import Pool
import multiprocessing


# Docs


AI_LEVEL = '2-E4'


# Core Functions


def process_possibilities(gamestate: 'GameState', possibilities: list, option: bool) -> tuple:
    '''Take all the possibilities as input and give the most benefit move.'''
    processed_possibilities = sort_possibilities(possibilities)
    corners = get_corners(gamestate)
    dangerous_positions = get_real_dangerous_positions(gamestate, get_tl_br_dangerous_positions(gamestate), get_tr_bl_dangerous_positions(gamestate))
    moves_for_corners = check_if_positions(processed_possibilities, corners)
    deleted_list = delete_possibilities(possibilities, dangerous_positions)
    type_of_move = ''
    if deleted_list:
        processed_possibilities = deleted_list
    else:
        type_of_move = 'BAD2'           # Need Improvement
    for move_for_corner in moves_for_corners:
        type_of_move = 'BEST'
        return move_for_corner, type_of_move
    list_for_comparing = []
    list_level_1 = []
    for possibility_num in range(len(processed_possibilities)):
        user_possibilities, user_gamestate = get_next_possibilities_and_gamestate(gamestate, processed_possibilities[possibility_num])
        dangerous_positions_for_user = get_real_dangerous_positions(user_gamestate, get_tl_br_dangerous_positions(user_gamestate), get_tr_bl_dangerous_positions(user_gamestate))
        if check_if_positions(user_possibilities, corners):
            continue
        if user_possibilities:
            score = calculate_score(gamestate, processed_possibilities, possibility_num, user_possibilities, user_gamestate, option)
            if check_if_all_in(user_possibilities, dangerous_positions_for_user):
                list_level_1.append([possibility_num, score])
            else:
                list_for_comparing.append([possibility_num, score])
        else:
            if type_of_move != 'BAD2':
                type_of_move = 'NORMAL2'
            return processed_possibilities[possibility_num], type_of_move
    if list_level_1:
        if type_of_move != 'BAD2':
            type_of_move = 'NORMAL3'
        return processed_possibilities[sorted(list_level_1, key=lambda x: x[1], reverse=True)[0][0]], type_of_move
    if list_for_comparing:
        if type_of_move != 'BAD2':
            type_of_move = 'NORMAL'
        return processed_possibilities[sorted(list_for_comparing, key=lambda x: x[1], reverse=True)[0][0]], type_of_move
    type_of_move = 'BAD'
    return processed_possibilities[0], type_of_move


def get_next_possibilities_and_gamestate(gamestate: 'GameState', possibility: list) -> tuple:
    '''Return the sorted possibilities and the gamestate of next move of the user.'''
    new_gamestate = copy.deepcopy(gamestate)
    new_gamestate = module_othello.make_move(new_gamestate, possibility)
    new_gamestate.current_player = module_othello.get_opposite_player(new_gamestate)
    return sort_possibilities(module_othello.get_all_possibilities(new_gamestate)), new_gamestate


def sort_possibilities(possibilities: list) -> list:
    '''Return the sorted possibilities, start from the highest benefit.'''
    return sorted(possibilities, key=lambda x: len(x[1]), reverse=True)


def check_if_positions(possibilities: list, positions: list) -> list:
    '''This function will check whether there is a corner in the possibilities.'''
    result_list = []
    for possibility in possibilities:
        for position in positions:
            if position == possibility[0]:
                result_list.append(possibility)
    return result_list


def check_if_all_in(possibilities: list, positions: list) -> bool:
    '''This function will check if all the positions are in the possibilities.'''
    for possibility in possibilities:
        if possibility[0] in positions:
            continue
        return False
    return True


def delete_possibilities(possibilities: list, positions: list) -> list:
    '''This function will delete all the positions that appear in the possibilities.'''
    return [possibility for possibility in possibilities if possibility[0] not in positions]


def get_corners(gamestate: 'GameState') -> list:
    '''Take the gamestate and return the four corners of the board.'''
    last_row_num = len(gamestate.board) - 1
    last_column_num = len(gamestate.board[-1]) - 1
    corners = [[0, 0],
               [0, last_column_num],
               [last_row_num, 0],
               [last_row_num, last_column_num]]
    return corners


def get_tl_br_dangerous_positions(gamestate: 'GameState') -> list:
    '''Take the gamestate and return the up dangerous positions of the board.'''
    last_row_num = len(gamestate.board) - 1
    last_column_num = len(gamestate.board[-1]) - 1
    dangerous_positions = [[0, 1], [1, 0], [1, 1],
                           [last_row_num - 1, last_column_num - 1], [last_row_num - 1, last_column_num], [last_row_num, last_column_num - 1]]
    return dangerous_positions


def get_tr_bl_dangerous_positions(gamestate: 'GameState') -> list:
    '''Take the gamestate and return the down dangerous positions of the board.'''
    last_row_num = len(gamestate.board) - 1
    last_column_num = len(gamestate.board[-1]) - 1
    dangerous_positions = [[0, last_column_num - 1], [1, last_column_num - 1], [1, last_column_num],
                           [last_row_num - 1, 0], [last_row_num - 1, 1], [last_row_num, 1]]
    return dangerous_positions


def get_real_dangerous_positions(gamestate: 'GameState', tl_br_dangerous_positions: list, tr_bl_dangerous_positions: list) -> list:
    '''This function will return some real dangerous positions which is decided by the current board.'''
    dangerous_positions = []
    if gamestate.board[0][0] == 0:
        dangerous_positions.extend(tl_br_dangerous_positions[:3])
    if gamestate.board[-1][-1] == 0:
        dangerous_positions.extend(tr_bl_dangerous_positions[3:])
    if gamestate.board[0][-1] == 0:
        dangerous_positions.extend(tr_bl_dangerous_positions[:3])
    if gamestate.board[-1][0] == 0:
        dangerous_positions.extend(tr_bl_dangerous_positions[3:])
    return dangerous_positions


def get_twenty_positions() -> list:
    '''This function will return twenty positions in the four sides of the board.
    Need Improvement(Now is just a test for 8 * 8 board.)'''
    return [[0, 2], [1, 2], [2, 2], [2, 1], [2, 0],
            [0, 5], [1, 5], [2, 5], [2, 6], [2, 7],
            [5, 0], [5, 1], [5, 2], [6, 2], [7, 2],
            [5, 7], [5, 6], [5, 5], [6, 5], [7, 5]]


def check_list(gamestate: 'GameState', list_for_check: list) -> bool:
    '''Take a list and check if it is safe.'''
    if list_for_check[:2] == [0, 0] and list_for_check[-2:] == [0, 0]:
        if module_othello.get_opposite_player(gamestate) not in list_for_check:
            return True
    if list_for_check[0] == gamestate.current_player or list_for_check[-1] == gamestate.current_player:  # Need Improvement
        return True
    return False


def check_if_in_boundaries(gamestate: 'GameState', position: list) -> int:
    '''This function will check whether the postion input is in the boundaries of the board.
    1 is up, 2 is down, 3 is left, 4 is right.'''
    if position[0] == 0:
        return 1
    elif position[0] == len(gamestate.board) - 1:
        return 2
    elif position[1] == 0:
        return 3
    elif position[1] == len(gamestate.board[0]) - 1:
        return 4
    else:
        return 0


def check_if_first_condition_in_boundaries(gamestate: 'GameState', mode: int, position: list) -> bool:
    '''This function will check the conditon like this. [...0, 1, 1, 1, 0, (1), 0, 0...].
    If the corner has already been taken, return False.'''
    if mode == 1 or mode == 2:
        mode = True
    else:
        mode = False
    line = module_othello._get_line_list(gamestate, position, mode)
    for cell_info_num in range(len(line)):
        if line[cell_info_num][1] == position:
            if cell_info_num - 2 > 0:
                wait_for_check_1 = [x[0] for x in line[cell_info_num - 2: cell_info_num]]
                if wait_for_check_1 == [0, 0]:
                    return False
            if cell_info_num + 2 < len(line) - 1:
                wait_for_check_3 = [x[0] for x in line[cell_info_num + 1: cell_info_num + 3]]
                if wait_for_check_3 == [0, 0]:
                    return True
    return True


def get_ai_next_move_quality(user_gamestate: 'GameState', possibility: list) -> str:
    '''This will assuse the ai to make another move and return that move's quality.'''
    possibilities, gamestate = get_next_possibilities_and_gamestate(user_gamestate, possibility)
    if possibilities:
        return process_possibilities(gamestate, possibilities, False)[1]
    else:
        return ''

def calculate_score(gamestate: 'GameState', possibilities: list, possibility_num: int, user_possibilities: list, user_gamestate: 'GameState', option: bool) -> int:
    score = len(possibilities[possibility_num][1])
    user_possibilities_comparing_list = []
    mode = check_if_in_boundaries(gamestate, possibilities[possibility_num][0])
    if possibilities[possibility_num][0] in get_twenty_positions():
        #print('Our score plus 5.')
        score += 5
    if mode:
        score += 3
        if check_if_first_condition_in_boundaries(gamestate, mode, possibilities[possibility_num][0]):
            score -= 3
    for wait_for_change_position in possibilities[possibility_num][1]:
        if check_if_in_boundaries(gamestate, wait_for_change_position):
            score += 3
    if option:
        p = Pool(processes=multiprocessing.cpu_count())
        results = []
    for user_possibility_num in range(len(user_possibilities)):
        if option:
            results.append(p.apply_async(calculate_score_assistant, args=(gamestate, user_gamestate, user_possibilities, user_possibility_num, option)))
        else:
            user_possibilities_comparing_list.append(calculate_score_assistant(gamestate, user_gamestate, user_possibilities, user_possibility_num, option))
    if option:
        all_move_qualities = []
        p.close()
        p.join()
        for result in results:
            all_move_qualities = [result.get()[1]]
            user_possibilities_comparing_list.append(result.get()[0])
        if all(quality == 'BEST' for quality in all_move_qualities):
            score += 100
        elif all(quality == 'NORMAL2' for quality in all_move_qualities):
            score += 30
        elif all(quality == 'NORMAL3' for quality in all_move_qualities):
            score += 30
        elif all(quality == 'BAD' for quality in all_move_qualities):
            score -= 100
        elif all(quality == 'BAD2' for quality in all_move_qualities):
            score -= 30
    score -= sorted(user_possibilities_comparing_list, key=lambda x: x[1], reverse=True)[0][1]
    return score


def calculate_score_assistant(gamestate: 'GameState', user_gamestate: 'GameState', user_possibilities: list, user_possibility_num: int, option: bool) -> 'result':
    '''This function is used to assist the calculate_score function in multiprocessing.'''
    temp_score = 0
    user_mode = check_if_in_boundaries(gamestate, user_possibilities[user_possibility_num][0])

    if option:
        ai_next_move_quality = get_ai_next_move_quality(user_gamestate, user_possibilities[user_possibility_num])
        if ai_next_move_quality == 'BAD':
            temp_score += 100
        elif ai_next_move_quality == 'BAD2':
            temp_score += 30
    if user_mode:
        temp_score += 3
        if check_if_first_condition_in_boundaries(user_gamestate, user_mode, user_possibilities[user_possibility_num][0]):
            temp_score -= 8
    if check_if_in_boundaries(gamestate, user_possibilities[user_possibility_num][0]):
        temp_score += 3
    for wait_for_change_position_user in user_possibilities[user_possibility_num][1]:
        if check_if_in_boundaries(gamestate, wait_for_change_position_user):
            temp_score += 3
    if user_possibilities[user_possibility_num][0] in get_twenty_positions():
        #print('The enemy score plus 5.')
        temp_score += 5
    if option:
        return [user_possibility_num, len(user_possibilities[user_possibility_num][1]) + temp_score], ai_next_move_quality
    else:
        return [user_possibility_num, len(user_possibilities[user_possibility_num][1]) + temp_score]



