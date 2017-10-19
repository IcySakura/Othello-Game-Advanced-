# Myles Liu, yuxil11@uci.edu, 50997122


#Edit
#2017-06-24 Bug fix: Now the hints can be refreshed correctly.
#2017-06-25 Bugs fix: Now the game can jump to the correct player if another player's turn has been skipped.
#2017-06-27 Bug fix: Fix a bug that can causes the AI not to make a move at first when the player's turn has been skipped.


# Import


import module_othello
import module_othello_ai
import tkinter
from tkinter import messagebox
import copy
import webbrowser
import main


# Font

def get_default_font() -> tuple:
    '''This function will return the default '''
    return ('Helvetica', 14)


# Classes


class MainWindow:

    '''This is the class to build the main window of the game.'''



    def __init__(self) -> None:

        '''This method is used to initialize the game.

        state_of_game is to display the status of the game.'''

        self._init_state_of_game()

        self._init_root_window()

        self._set_game()





    def _init_root_window(self) -> None:

        '''This method will initialize the root window.'''

        self._root_window = tkinter.Tk()

        self._root_window.iconbitmap('moe_icon.ico')

        self._root_window.wm_title('Moe Othello')

        self._bg_image = tkinter.PhotoImage(file='moe_bg.gif')

        self._init_menubar()

        self._root_window.config(menu=self._menubar)

        self._root_window.rowconfigure(1, weight=1)

        self._root_window.columnconfigure(0, weight=1)





    def _init_state_of_game(self) -> None:

        '''This method will initialize the state of game.

         0 is not start, 1 is initializing, 2 is playing, 3 is end.'''

        self._not_start_state = 0

        self._initializing_state = 1

        self._playing_state = 2

        self._is_end_state = 3

        self.state_of_game = self._not_start_state





# Main





    def run(self) -> None:

        '''This is used to run the game.'''

        self._root_window.mainloop()





    def _set_game(self) -> None:

        '''This method will use the settings class to initialize some data of the game.

        modde_of_game is used to display whether the user is playing with a robot or another user.

        0 is with another user, 1 is with robot.'''

        s = Settings(self._root_window)

        s.show()

        if s.get_ok_clicked():

            if s.get_hint() == 1:

                self._have_hint = True

            else:

                self._have_hint = False

            self.gamestate = module_othello.GameState(s.get_rows(), s.get_columns(), s.get_rule())

            self.gamestate.initialize_blank_board()

            self.gamestate.initialize_player(s.get_player())

            self._mode_of_game = 0

            self._prepare_game()

        elif s.get_ai_clicked():

            self._start_ai_game()





    def _start_ai_game(self) -> None:

        '''This method is used to start a ai game.'''

        _show_notification('Notification', 'Since the game is still in development,\n'

                                           'the game had been automatically reset to the following settings.\n'

                                           'Rows: 8   Columns: 8\nRule: More to win\nUser is BLACK\nUser goes first')

        a_s = Ai_Extra_Settings(self._root_window)

        a_s.show()

        if a_s.whether_ok_clicked():

            self._have_hint = a_s.get_hint() == 0

            self._ai_level = a_s.get_level()

            self._mode_of_game = 1

            self.gamestate = module_othello.GameState(8, 8, 1)

            self.gamestate.initialize_blank_board()

            self.gamestate.initialize_player(self.gamestate.BLACK)

            self._prepare_game()

        else:

            self._set_game()





    def _save_data(self) -> None:

        '''This method will save the data for initializing the game.'''

        self._saved_gamestate = copy.deepcopy(self.gamestate)





    def _restart_game(self) -> None:

        '''This method will restart the game.'''

        if self.state_of_game != self._not_start_state and self.state_of_game != self._initializing_state:

            self.gamestate = copy.deepcopy(self._saved_gamestate)

            self._start_game()

        else:

            _show_start_game_warning()





    def _restart_game_from_prepare(self) -> None:

        '''This method will restart the game from preparing the board.'''

        if self.state_of_game != self._not_start_state and self.state_of_game != self._initializing_state:

            self.gamestate = copy.deepcopy(self._saved_gamestate)

            self.gamestate.initialize_blank_board()

            self.redraw_the_board()

            self._prepare_game()

        else:

            _show_start_game_warning()





    def _prepare_game(self) -> None:

        '''This method will start to prepare the game.'''

        self._rotate_player = self.gamestate.current_player

        self._current_prepare_player = self.gamestate.BLACK

        self._undo_count = 0

        self._cheat_count = 0

        if self.state_of_game != self._not_start_state:

            self._label_info.destroy()

            self._canvas.destroy()

        self._init_board()

        self._init_infobar('Initializing the Board')





    def _start_game(self) -> None:

        '''This method will start the game.'''

        self._is_just_start = True

        self._save_data()

        if self.state_of_game == self._initializing_state:

            self._infobar_ok_button.destroy()

        self._refresh_num_of_pieces()

        self.state_of_game = self._playing_state

        self.redraw_the_board()

        real_time_status = self._check_if_pass_or_end()

        if real_time_status == 2:

            self._end_the_game()

        else:

            if real_time_status == 1 and self._mode_of_game == 1:

                self._ai_make_move(self._ai_level)

            self._refresh_infobar_playing()





    def _undo(self) -> None:

        '''This method will undo one step if now is playing with another user,

        undo two steps if not is plying with robot. 0 is user, 1 is robot.'''

        if self.state_of_game == self._playing_state:

            if not self._is_just_start:

                self._undo_count += 1

                if self._mode_of_game == 0:

                    self.gamestate.undo_one_step()

                elif self._mode_of_game == 1:

                    self.gamestate.undo_one_step()

                    self.gamestate.undo_one_step()

                self.redraw_the_board()

                self._refresh_num_of_pieces()

                self._refresh_infobar_playing()

            else:

                messagebox.showwarning(title='Warning', message='Please give at least one valid move.')

        else:

            _show_start_game_warning()





    def _end_the_game(self) -> None:

        '''This method is used to end the game.'''

        self.state_of_game = self._is_end_state

        self._refresh_num_of_pieces()

        self.redraw_the_board()

        winner = _get_str_of_player(module_othello.get_winner(self.gamestate), self.gamestate)

        board_info = 'BLACK ' + self._num_of_black + ' VS WHITE ' + self._num_of_white

        if winner == 'EMPTY':

            self._refresh_infobar('Draw!   ' + board_info)

            _show_notification('Result', 'Draw!\n ' + board_info)

        else:

            self._refresh_infobar('The ' +

                                  winner + ' player win!   ' + board_info)

            _show_notification('Result', 'The ' +

                               winner + ' player win!\n ' + board_info)





# Board





    def _init_board(self) -> None:

        '''This method is to initialize the board.'''

        self.state_of_game = self._initializing_state

        self._status = False

        self._num_of_white = '0'

        self._num_of_black = '1'

        self._canvas = tkinter.Canvas(master=self._root_window,

                                      width=self.gamestate.num_of_columns * 100,

                                      height=self.gamestate.num_of_rows * 100)

        self._canvas.grid(row=1, column=0, columnspan=2, padx=10, pady=10,

                          sticky=tkinter.N + tkinter.S + tkinter.W + tkinter.E)

        self._canvas.bind('<Configure>', self._canvas_resized)

        self._canvas.bind('<Button-1>', self._place_on_clicked)





    def _place_on_clicked(self, event: tkinter.Event) -> None:

        '''This method will be used when the player click on the canvas.'''

        if self.state_of_game != self._not_start_state and self.state_of_game != self._is_end_state:

            position = self._from_pixel_to_rate((event.x, event.y))

            row_number = -1

            column_number = -1

            for row in range(len(self._rows_rates)):

                if position[1] < self._rows_rates[row][1]:

                    row_number = row

                    break

            for column in range(len(self._columns_rates)):

                if position[0] < self._columns_rates[column][0]:

                    column_number = column

                    break

            if row_number != -1 and column_number != -1:

                self._make_move([row_number, column_number])





    def _make_prepare_move(self, position: list) -> None:

        '''This method is only used to make a prepared move.'''

        self.gamestate.board[position[0]][position[1]] = _rotate_player(self.gamestate.board[position[0]][position[1]], self.gamestate)

        #if self.gamestate.board[position[0]][position[1]] != _get_opposite_player(self._current_prepare_player, self.gamestate):

        #    self.gamestate.board[position[0]][position[1]] = self._current_prepare_player





    def _refresh_possibilities(self) -> None:

        '''This method will refresh the current player's possibilities.'''

        self._possibilities = module_othello.get_all_possibilities(self.gamestate)





    def _refresh_hints(self) -> None:

        '''This method will refresh the current hints.'''

        self._hints = [possibility[0] for possibility in module_othello.get_all_possibilities(self.gamestate)]





    def _change_player(self) -> None:

        '''This method will change the current player to the other player.'''

        self.gamestate.current_player = module_othello.get_opposite_player(self.gamestate)





    def _ai_make_move(self, ai_level: int) -> None:

        '''This method is used to let ai make one move.'''

        ai_is_moved = False

        real_time_status = self._check_if_pass_or_end()

        if real_time_status == 0:

            self._refresh_infobar('AI is computing.')

            move_from_ai = module_othello_ai.process_possibilities(self.gamestate, self._possibilities, ai_level)

            self.gamestate = module_othello.make_move(self.gamestate, move_from_ai[0])

            self._refresh_num_of_pieces()

            ai_is_moved = True

            self._change_player()

            self.redraw_the_board()

        elif real_time_status == 2:

            self._end_the_game()

        if ai_is_moved:

            real_time_status_2 = self._check_if_pass_or_end()

            if real_time_status_2 == 1:

                self._ai_make_move(ai_level)

            elif real_time_status_2 == 2:

                self._end_the_game()

        if self.state_of_game == self._playing_state:

            self._refresh_infobar_playing()





    def _cheat_make_move(self) -> None:

        '''This method will be used when the player want to cheat for a move.'''

        if self.state_of_game == self._playing_state:

            self._cheat_count += 1

            self._ai_make_move(1)

        else:

            _show_start_game_warning()





    def _make_normal_move(self, position: list) -> bool:

        '''This method is only used to make a normal move. If the move is made, then return True,

        otherwise, return False.'''

        real_time_status = self._check_if_pass_or_end()

        if real_time_status == 0:

            for possibility in self._possibilities:

                if position == possibility[0]:

                    self.gamestate = module_othello.make_move(self.gamestate, possibility)

                    self._change_player()

                    self._is_just_start = False

                    real_time_status_2 = self._check_if_pass_or_end()

                    if real_time_status_2 == 2:

                        self._end_the_game()

                    return True

        elif real_time_status == 1:

            return True      #Temp fix: pretend to not make a move in order to let AI make a move.

        elif real_time_status == 2:

            self._end_the_game()

        return False





    def _check_if_pass_or_end(self) -> int:

        '''This method will check whether the next player will pass or the game is ended.

        If pass, return 1, elif the game is ended, return 2, otherwise return 0.'''

        self._refresh_possibilities()

        if self._possibilities:

            return 0

        else:

            self._change_player()

            self._refresh_possibilities()

            if self._possibilities:

                return 1

            else:

                return 2





    def _refresh_num_of_pieces(self) -> None:

        '''This method will refresh the numbers of both black and white pieces.'''

        self._num_of_black = str(self.gamestate.get_num_of_pieces(self.gamestate.BLACK))

        self._num_of_white = str(self.gamestate.get_num_of_pieces(self.gamestate.WHITE))





    def _make_move(self, position: list) -> None:

        '''This method will make a move depending on the state of game.'''

        is_moved = False

        if self.state_of_game == self._initializing_state:

            self._make_prepare_move(position)

            self._refresh_num_of_pieces()

            self._refresh_infobar('Current State: BLACK ' + self._num_of_black + ' VS WHITE ' + self._num_of_white)

        elif self.state_of_game == self._playing_state:

            is_moved = self._make_normal_move(position)

            if is_moved:

                self._refresh_num_of_pieces()

                if self.state_of_game != self._is_end_state:

                    self._refresh_infobar_playing()

        self.redraw_the_board()

        if is_moved:

            if self.state_of_game != self._is_end_state:

                if self.state_of_game == self._playing_state and self._mode_of_game == 1:

                    self._ai_make_move(self._ai_level)





    def _canvas_resized(self, event: tkinter.Event) -> None:

        '''This method will be used when the board is resized.'''

        self.redraw_the_board()





    def _refresh_info(self) -> None:

        '''This method will refresh the width and height of the board.'''

        self._width = self._canvas.winfo_width()

        self._height = self._canvas.winfo_height()

        self._refresh_lines_info()





    def _from_pixel_to_rate(self, pixel: tuple) -> tuple:

        '''This method will take a position represented by pixel and return it by its rate.'''

        return (pixel[0] / self._width, pixel[1] / self._height)





    def _from_rate_to_pixel(self, rate: tuple) -> tuple:

        '''This method will take a position represented by rate and return it by its pixel.'''

        return (rate[0] * self._width, rate[1] * self._height)





    def _refresh_lines_info(self) -> None:

        '''This method will refresh the line info by rate.'''

        self._interval_of_column = 1 / self.gamestate.num_of_columns

        self._interval_of_row = 1 / self.gamestate.num_of_rows

        self._columns_rates = [((column + 1) * self._interval_of_column, 0, (column + 1) * self._interval_of_column, 1 )

                               for column in range(self.gamestate.num_of_columns)]

        self._rows_rates = [(0, (row + 1) * self._interval_of_row, 1, (row + 1) * self._interval_of_row)

                               for row in range(self.gamestate.num_of_rows)]





    def _draw_lines(self) -> None:

        '''This method will draw all the lines.'''

        for column in self._columns_rates:

            self._canvas.create_line(*self._from_rate_to_pixel(column[:2]), *self._from_rate_to_pixel(column[2:]))

        for row in self._rows_rates:

            self._canvas.create_line(*self._from_rate_to_pixel(row[:2]), *self._from_rate_to_pixel(row[2:]))





    def _draw_point(self, piece_and_position: list) -> None:

        '''This method will draw one point.'''

        color = '#FFFFFF' if piece_and_position[0] == self.gamestate.WHITE else '#000000'

        self._canvas.create_oval(piece_and_position[1][1] * self._interval_of_column * self._width,

                                 piece_and_position[1][0] * self._interval_of_row * self._height,

                                 (piece_and_position[1][1] + 1) * self._interval_of_column * self._width,

                                 (piece_and_position[1][0] + 1) * self._interval_of_row * self._height, fill=color)





    def _draw_hint_points(self) -> None:

        '''This method will draw one hint point.'''

        color = '#75FF6B'

        for position in self._hints:

            self._canvas.create_oval(position[1] * self._interval_of_column * self._width,

                                     position[0] * self._interval_of_row * self._height,

                                     (position[1] + 1) * self._interval_of_column * self._width,

                                     (position[0] + 1) * self._interval_of_row * self._height, fill=color)





    def _draw_points(self) -> None:

        '''This method will draw all the points.'''

        pieces_and_positions = []

        for row in range(len(self.gamestate.board)):

            for column in range(len(self.gamestate.board[row])):

                piece = self.gamestate.board[row][column]

                if piece != self.gamestate.EMPTY:

                    pieces_and_positions.append([piece, (row, column)])

        for piece_and_posiition in pieces_and_positions:

            self._draw_point(piece_and_posiition)





    def redraw_the_board(self) -> None:

        '''This method will redraw the board.'''

        self._canvas.delete(tkinter.ALL)

        self._refresh_info()

        self._canvas.create_image(self._width / 2, self._height / 2, anchor='center', image=self._bg_image)

        self._draw_lines()

        self._draw_points()

        if self._have_hint and self.state_of_game == self._playing_state:

            self._refresh_hints()

            self._draw_hint_points()





# Info Bar





    def _init_infobar(self, wait_for_display: str) -> None:

        '''This method will initialize the infobar.'''

        self._init_infobar_label_(wait_for_display)

        self._init_infobar_button_ok('START')





    def _init_infobar_button_ok(self, button_text: str) -> None:

        '''This method will initialize the button OK.'''

        self._infobar_ok_button = tkinter.Button(master=self._root_window, text=button_text, font=get_default_font(),

                                  command=self._start_game)

        self._infobar_ok_button.grid(row=0, column=1, padx=10, pady=10)





    def _change_player_or_start(self) -> None:

        '''This method will change the current prepare player or start the game.'''

        if self._current_prepare_player == self.gamestate.BLACK:

            self._current_prepare_player = self.gamestate.WHITE

            self._refresh_infobar('Placing:' + _get_str_of_player(self._current_prepare_player, self.gamestate) +

                                  '   Current State: BLACK ' + self._num_of_black + ' VS WHITE ' + self._num_of_white)

            self._infobar_ok_button.destroy()

            self._init_infobar_button_ok('START')

        else:

            self._start_game()





    def _init_infobar_label_(self, wait_for_display: str) -> None:

        '''This method will initialize a label for displaying information.'''

        self._label_info = tkinter.Label(master=self._root_window, text=wait_for_display, font=get_default_font())

        self._label_info.grid(row=0, column=0, padx=10, pady=10)





    def _refresh_infobar(self, wait_for_display: str) -> None:

        '''This method will refresh the whole bar.'''

        self._label_info.destroy()

        self._init_infobar_label_(wait_for_display)





    def _refresh_infobar_playing(self) -> None:

        '''This method is used to refresh the infobar while playing.'''

        self._refresh_infobar('BLACK ' + self._num_of_black

                              + ' VS WHITE ' + self._num_of_white +

                              '   Current Player: ' +

                              _get_str_of_player(self.gamestate.current_player, self.gamestate) +

                              '  Game Rule: ' + _get_str_of_rule(self.gamestate.rule, self.gamestate))





# Menu Bar





    def _init_menubar(self) -> None:

        '''This method will initialize the menubar.'''

        self._menubar = tkinter.Menu(master=self._root_window)

        self._init_menu_1()

        self._init_menu_2()

        self._init_menu_3()





    def _init_menu_1(self) -> None:

        '''This method will initialize the menu 1.'''

        menu_1 = tkinter.Menu(master=self._menubar, tearoff=0)

        menu_1.add_command(label='New Game', command=self._set_game)

        menu_1.add_command(label='Restart Game', command=self._restart_game)

        menu_1.add_command(label='Restart Game from Preparing', command=self._restart_game_from_prepare)

        menu_1.add_separator()

        menu_1.add_command(label='Exit', command=self._root_window.quit)

        self._menubar.add_cascade(label='File', menu=menu_1)





    def _init_menu_2(self) -> None:

        '''This method will initialize the menu 2.'''

        menu_2 = tkinter.Menu(master=self._menubar, tearoff=0)

        menu_2.add_command(label='Undo', command=self._undo)

        menu_2.add_command(label='Cheat', command=self._cheat_make_move)

        menu_2.add_separator()

        menu_2.add_command(label='State', command=self._show_state)

        self._menubar.add_cascade(label='Edit', menu=menu_2)





    def _init_menu_3(self) -> None:

        '''This method will initialize the menu 3.'''

        menu_3 = tkinter.Menu(master=self._menubar, tearoff=0)

        menu_3.add_command(label='Help', command=self._show_help)

        menu_3.add_command(label='About', command=self._show_about)

        self._menubar.add_cascade(label='Other', menu=menu_3)





# Other





    def _show_about(self) -> None:

        '''This method will show the about window.'''

        about = About(self._root_window)

        about.show()





    def _show_help(self) -> None:

        '''This method will show the help window.'''

        help = Help(self._root_window)

        help.show()





    def _get_state_of_game_str(self) -> str:

        '''This method will return the state of game in str.'''

        if self.state_of_game == self._not_start_state:

            return 'Not Yet Start'

        elif self.state_of_game == self._initializing_state:

            return 'Preparing'

        elif self.state_of_game == self._playing_state:

            return 'Playing'

        elif self.state_of_game == self._is_end_state:

            return 'End'





    def _show_state(self) -> None:

        '''This method will be used when the player click the State button in the menubar.'''

        try:

            state_of_game_str = 'State: ' + self._get_state_of_game_str() + '\n'

            mode_of_game = 'Mode: Playing with ' + ('human' if self._mode_of_game == 0 else 'AI') + '\n'

            current_nums = 'Current Nums: Black: ' + str(self._num_of_black) + ' White: ' + str(self._num_of_white) + '\n'

            undo_count = 'Undo Count: ' + str(self._undo_count) + '\n'

            cheat_count = 'Cheat Count: ' + str(self._cheat_count) + '\n'

            current_player = 'Current Player: ' + _get_str_of_player(self.gamestate.current_player, self.gamestate) + '\n'

            rule = 'Rule: ' + _get_str_of_rule(self.gamestate.rule, self.gamestate) + '\n'

            hint = 'Hint: ' + ('ON' if self._have_hint else 'OFF')

            _show_notification('State', state_of_game_str + mode_of_game + current_nums + current_player + undo_count + cheat_count + rule + hint)

        except:

            _show_start_game_warning()


class Settings:
    '''This is the class for Settings which is used to set the game.'''

    def __init__(self, root_window: tkinter.Tk) -> None:
        '''This method will initialize the window for settings.'''
        self._root_window = root_window
        self._settings = tkinter.Toplevel(master=self._root_window)
        self._settings.iconbitmap('moe_icon.ico')
        self._init_all_labels()
        self._init_all_entries()
        self._init_all_buttons()
        self._config_all()


    def _config_all(self) -> None:
        '''This method is used to config all the layout.'''
        for row in range(9):
            self._settings.rowconfigure(row, weight=1)
        for column in range(2):
            self._settings.columnconfigure(column, weight=1)


    def get_rows(self) -> int:
        '''This method will return the rows.'''
        return self._rows


    def get_columns(self) -> int:
        '''This method will return the columns.'''
        return self._columns


    def get_player(self) -> int:
        '''This method will return the player who goes first.'''
        return self._player


    def get_rule(self) -> int:
        '''This method will return the game rule.'''
        return self._rule


    def get_hint(self) -> int:
        '''This method will return whether the hint is turned on.'''
        return self._hint


    def get_ok_clicked(self) -> bool:
        '''This method will return the _ok_clicked.'''
        return self._ok_clicked


    def get_ai_clicked(self) -> bool:
        '''This method will return the _ai_clicked.'''
        return self._ai_clicked


    def show(self) -> None:
        '''This method will display the Settings.'''
        self._settings.grab_set()
        self._settings.wait_window()


    def _init_all_labels(self) -> None:
        '''This method will initialize all the labels.'''
        self._init_label_top()
        self._init_label_rows()
        self._init_label_colunms()
        self._init_label_player()
        self._init_label_rule()
        self._init_label_hint()


    def _init_all_entries(self) -> None:
        '''This method will initialize all the entries.'''
        self._rows = 0
        self._columns = 0
        self._init_entry_rows()
        self._init_entry_columns()


    def _init_all_buttons(self) -> None:
        '''This method will initialize all the buttons.'''
        self._ok_clicked = False
        self._cancel_clicked = False
        self._ai_clicked = False
        self._init_radiobutton_player()
        self._init_radiobutton_rule()
        self._init_radiobutton_hint()
        self._init_button_frame()
        self._init_button_ai()
        self._init_button_ok()
        self._init_button_cancel()


    def _init_label_top(self) -> None:
        '''This method is used to initialize the top label.'''
        label_main = tkinter.Label(master=self._settings,
                                   text='Please Enter the Following Information:',
                                   font=get_default_font())
        label_main.grid(row=0, column=0, columnspan=2, padx=10, pady=10,
                        sticky=tkinter.W)


    def _init_label_rows(self) -> None:
        '''This method is used to initialize the rows label.'''
        self.label_rows = tkinter.Label(master=self._settings,
                                   text='Rows(4-16 and even):',
                                   font=get_default_font())
        self.label_rows.grid(row=1, column=0, padx=10, pady=10,
                                  sticky=tkinter.W)


    def _init_label_colunms(self) -> None:
        '''This method is used to initialize the columns label.'''
        self.label_columns = tkinter.Label(master=self._settings,
                                   text='Columns(4-16 and even):',
                                   font=get_default_font())
        self.label_columns.grid(row=2, column=0, padx=10, pady=10,
                        sticky=tkinter.W)


    def _init_label_player(self) -> None:
        '''This method is used to initialize the choose player label.'''
        self.label_rule = tkinter.Label(master=self._settings,
                                           text='Who goes first:',
                                           font=get_default_font())
        self.label_rule.grid(row=3, column=0, rowspan=2, padx=10, pady=10,
                                sticky=tkinter.W)


    def _init_label_rule(self) -> None:
        '''This method is used to initialize the rule label.'''
        self.label_rule = tkinter.Label(master=self._settings,
                                           text='Rule:',
                                           font=get_default_font())
        self.label_rule.grid(row=5, column=0, rowspan=2, padx=10, pady=10,
                                sticky=tkinter.W)


    def _init_label_hint(self) -> None:
        '''This method is uesd to initialize the hint label.'''
        self.label_hint = tkinter.Label(master=self._settings, text='Hint:', font=get_default_font())
        self.label_hint.grid(row=7, column=0, rowspan=2, padx=10, pady=10, sticky=tkinter.W)


    def _init_entry_rows(self) -> None:
        '''This method will initialize the entry for rows.'''
        self._entry_rows = tkinter.Entry(master=self._settings)
        self._entry_rows.grid(row=1, column=1, padx=10, pady=10,
                             sticky=tkinter.W + tkinter.E)


    def _init_entry_columns(self) -> None:
        '''This method will initialize the entry for columns.'''
        self._entry_columns = tkinter.Entry(master=self._settings)
        self._entry_columns.grid(row=2, column=1, padx=10, pady=10,
                              sticky=tkinter.W + tkinter.E)


    def _init_radiobutton_player(self) -> None:
        '''This method will initialize the raidobutton for choosing the player who goes first. 1 is black, 2 is white.'''
        self._player_p = tkinter.IntVar()
        r1 = tkinter.Radiobutton(master=self._settings, text='BLACK', variable=self._player_p, value=1)
        r2 = tkinter.Radiobutton(master=self._settings, text='WHITE', variable=self._player_p, value=2)
        r1.grid(row=3, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)
        r2.grid(row=4, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)


    def _init_radiobutton_rule(self) -> None:
        '''This method will initialize the raidobutton for the rule. > is 1, < is 2.'''
        self._rule_p = tkinter.IntVar()
        r1 = tkinter.Radiobutton(master=self._settings, text='More Discs to Win', variable=self._rule_p, value=1)
        r2 = tkinter.Radiobutton(master=self._settings, text='Less Discs to Win', variable=self._rule_p, value=2)
        r1.grid(row=5, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)
        r2.grid(row=6, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)


    def _init_radiobutton_hint(self) -> None:
        '''This method will initialize the radiobutton for the hint. Show hint is 1, otherwise is 2.'''
        self._hint_p = tkinter.IntVar()
        r1 = tkinter.Radiobutton(master=self._settings, text='On', variable=self._hint_p, value=1)
        r2 = tkinter.Radiobutton(master=self._settings, text='Off', variable=self._hint_p, value=2)
        r1.grid(row=7, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)
        r2.grid(row=8, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)


    def _init_button_frame(self) -> None:
        '''This method will initialize the frame of the button for OK and CANCEL.'''
        self._button_frame = tkinter.Frame(master=self._settings)
        self._button_frame.grid(
            row=9, column=0, columnspan=2, padx=10, pady=10,
            sticky=tkinter.E + tkinter.S)


    def _on_ok_button(self) -> None:
        '''This method will be run if the ok button is clicked.'''
        try:
            self._rows = int(self._entry_rows.get())
            self._columns = int(self._entry_columns.get())
            self._rule = self._rule_p.get()
            self._hint = self._hint_p.get()
            self._player = self._player_p.get()
            if not self._judge_values():
                self._ok_clicked = True
                self._settings.destroy()
        except:
            pass
        if not self._ok_clicked:
            _show_notification('Warning', 'Plase give valid information!')


    def _judge_values(self) -> bool:
        '''This method will make sure whether all the values are legal.'''
        return (self._rows == '' or self._columns == '' or self._rule == 0 or self._hint == 0
                or self._rows < 4 or self._rows > 16 or self._rows % 2 != 0
                or self._columns < 4 or self._columns > 16 or self._columns % 2 != 0
                or self._player == 0)


    def _on_cancel_button(self) -> None:
        '''This method will be run if the cancel button is clicked.'''
        self._cancel_clicked = True
        self._settings.destroy()


    def _on_ai_button(self) -> None:
        '''This method will be run if the ai button is clicked.'''
        self._ai_clicked = True
        self._settings.destroy()


    def _init_button_ai(self) -> None:
        '''This method will initialize the button AI.'''
        ai_button = tkinter.Button(master=self._button_frame, text='Play With AI', font=get_default_font(),
                                   command=self._on_ai_button, relief='groove')
        ai_button.grid(row=0, column=0, padx=10, pady=10)


    def _init_button_ok(self) -> None:
        '''This method will initialize the button OK.'''
        ok_button = tkinter.Button(master=self._button_frame, text='OK', font=get_default_font(),
                                   command=self._on_ok_button, relief='groove')
        ok_button.grid(row=0, column=1, padx=10, pady=10)


    def _init_button_cancel(self) -> None:
        '''This method will initialize the button CANCEL.'''
        cancel_button = tkinter.Button(master=self._button_frame, text='Cancel', font=get_default_font(),
                                       command=self._on_cancel_button, relief='groove')
        cancel_button.grid(row=0, column=2, padx=10, pady=10)


class Ai_Extra_Settings:
    '''This class is for the AI extra settings window.'''


    def __init__(self, root_window: tkinter.Tk) -> None:
        '''This is used to initialize the AI extra settings window.'''
        self._ai_settings = tkinter.Toplevel(master=root_window)
        self._ai_settings.iconbitmap('moe_icon.ico')
        self._is_ok_clicked = False
        self._init_label_level()
        self._init_label_hint()
        self._init_button_frame()
        self._init_ratiobutton_level()
        self._init_ratiobutton_hint()
        self._init_button_ok()
        self._init_button_cancel()
        self._config_all()


    def _config_all(self) -> None:
        '''This method is used to config all the layout.'''
        for row in range(5):
            self._ai_settings.rowconfigure(row, weight=1)
        for column in range(2):
            self._ai_settings.columnconfigure(column, weight=1)


    def show(self) -> None:
        '''This will show the about window on focus.'''
        self._ai_settings.grab_set()
        self._ai_settings.wait_window()


    def _close(self) -> None:
        '''This method will close the about window.'''
        self._ai_settings.destroy()


    def _ok_button_clicked(self) -> None:
        '''This method will be run if the ok button is clicked.'''
        level = self._level_p.get()
        self._is_ok_clicked = True
        self._close()


    def whether_ok_clicked(self) -> bool:
        '''This method will return whether the ok button is clicked.'''
        return self._is_ok_clicked


    def get_level(self) -> int:
        '''This method will return the level of the AI that being selected.'''
        return self._level_p.get()


    def get_hint(self) -> int:
        '''This method will return whether the user want hint.'''
        return self._hint_p.get()


    def _init_label_level(self) -> None:
        '''This method will initialize the label for the ratiobutton.'''
        self._label_level = tkinter.Label(master=self._ai_settings, text='Pick a Level:', font=get_default_font())
        self._label_level.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky=tkinter.W)


    def _init_label_hint(self) -> None:
        '''This method will initialize the label for whether turn on the hint.'''
        self._label_hint = tkinter.Label(master=self._ai_settings, text='Hint', font=get_default_font())
        self._label_hint.grid(row=2, column=0, rowspan=2, padx=10, pady=10, sticky=tkinter.W)


    def _init_ratiobutton_level(self) -> None:
        '''This method is used to initialize the level of the AI.0 is easy, 1 is normal.'''
        self._level_p = tkinter.IntVar()
        r1 = tkinter.Radiobutton(master=self._ai_settings, text='EASY', variable=self._level_p, value=0)
        r2 = tkinter.Radiobutton(master=self._ai_settings, text='NORMAL', variable=self._level_p, value=1)
        r1.grid(row=0, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)
        r2.grid(row=1, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)


    def _init_ratiobutton_hint(self) -> None:
        '''This method is used to initialize whether the user want hint.'''
        self._hint_p = tkinter.IntVar()
        r1 = tkinter.Radiobutton(master=self._ai_settings, text='ON', variable=self._hint_p, value=0)
        r2 = tkinter.Radiobutton(master=self._ai_settings, text='OFF', variable=self._hint_p, value=1)
        r1.grid(row=2, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)
        r2.grid(row=3, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)


    def _init_button_frame(self) -> None:
        '''This method will initialize the frame of the button for OK and CANCEL.'''
        self._button_frame = tkinter.Frame(master=self._ai_settings)
        self._button_frame.grid(
            row=4, column=0, columnspan=2, padx=10, pady=10,
            sticky=tkinter.E + tkinter.S)


    def _init_button_ok(self) -> None:
        '''This method will initialize the button OK.'''
        ok_button = tkinter.Button(master=self._button_frame, text='OK', font=get_default_font(),
                                   command=self._ok_button_clicked, relief='groove')
        ok_button.grid(row=0, column=0, padx=10, pady=10)


    def _init_button_cancel(self) -> None:
        '''This method will initialize the button CANCEL.'''
        cancel_button = tkinter.Button(master=self._button_frame, text='Cancel', font=get_default_font(),
                                       command=self._close, relief='groove')
        cancel_button.grid(row=0, column=1, padx=10, pady=10)


class Help:
    '''This class is for the help window.'''


    def __init__(self, root_window: tkinter.Tk) -> None:
        '''This is used to initialize the help window.'''
        self._help = tkinter.Toplevel(master=root_window)
        self._help.iconbitmap('moe_icon.ico')
        self._init_info_label()
        self._init_rule_link()
        self._init_button_ok()
        self._config_all()


    def _config_all(self) -> None:
        '''This method is used to config all the layout.'''
        for row in range(3):
            self._help.rowconfigure(row, weight=1)
        for column in range(1):
            self._help.columnconfigure(column, weight=1)


    def show(self) -> None:
        '''This will show the about window on focus.'''
        self._help.grab_set()
        self._help.wait_window()


    def _close(self) -> None:
        '''This method will close the about window.'''
        self._help.destroy()


    def _open_website(self) -> None:
        '''This method is used to open the rule website.'''
        _open_website('https://en.wikipedia.org/wiki/Reversi#Rules')


    def _init_info_label(self) -> None:
        '''This method will initialize the help window.'''
        text_to_show = 'Welcome to the Othello Game!\n'
        self._info_label = tkinter.Label(master=self._help, text=text_to_show, font=get_default_font())
        self._info_label.grid(row=0, column=0, padx=10, pady=10, sticky=tkinter.W + tkinter.E)


    def _init_rule_link(self) -> None:
        '''This method is used to display for the hyperlink of the rule.'''
        text_to_show = 'For rules, Please click me.'
        self._rule_label = tkinter.Label(master=self._help, text=text_to_show, font=get_default_font(), background='#FFA4FF')
        self._rule_label.grid(row=1, column=0, padx=10, pady=10, sticky=tkinter.W + tkinter.E)
        self._rule_label.bind('<Button-1>', self._open_website)

    def _init_button_ok(self) -> None:
        '''This method is used to initialize the ok button.'''
        self._ok_button = tkinter.Button(master=self._help, text='OK', command=self._close)
        self._ok_button.grid(row=2, column=0, padx=10, pady=10, sticky=tkinter.W + tkinter.E)


class About:
    '''This is the class for about.'''


    def __init__(self, root_window: tkinter.Tk) -> None:
        '''This is used to initialize the about.'''
        self._root_window = root_window
        self._about = tkinter.Toplevel(master=self._root_window)
        self._about.iconbitmap('moe_icon.ico')
        self._init_info_label()
        self._init_website_label()
        self._init_check_update_button()
        self._init_ok_button()
        self._config_all()


    def _config_all(self) -> None:
        '''This method is used to config all the layout.'''
        for row in range(3):
            self._about.rowconfigure(row, weight=1)
        for column in range(1):
            self._about.columnconfigure(column, weight=1)


    def show(self) -> None:
        '''This will show the about window on focus.'''
        self._about.grab_set()
        self._about.wait_window()


    def _close(self) -> None:
        '''This method will clost the about window.'''
        self._about.destroy()


    def _init_info_label(self) -> None:
        '''This will initialize the label for showing information.'''
        text_for_show = ('\nThank you for playing my Othello game!\nCurrent Version: ' + get_current_version() + '\n' +
                        'For bugs please email: lyx98mike@gmail.com\n\n\n\n' +
                        'All Rights reserved by @IcySakura')
        self._info_label = tkinter.Label(master=self._about, text=text_for_show, font=get_default_font())
        self._info_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tkinter.W + tkinter.E + tkinter.N + tkinter.S)


    def _open_website(self) -> None:
        '''This method is used to open my website.'''
        _open_website('http://blog.donkeyandperi.net')


    def _init_website_label(self) -> None:
        '''This method will init the label for showing the website.'''
        text_for_show = 'Click here to visit my website:\nhttp://blog.donkeyandperi.net'
        self._web_label = tkinter.Label(master=self._about, text=text_for_show, font=get_default_font(), background='#62B6FF')
        self._web_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tkinter.W + tkinter.E + tkinter.N + tkinter.S)
        self._web_label.bind('<Button-1>', self._open_website)


    def _init_check_update_button(self) -> None:
        '''This will initialize the check for update button.'''
        self._check_update_button = tkinter.Button(master=self._about, text='Check Update', command=self._is_updated)
        self._check_update_button.grid(row=2, column=0, padx=10, pady=10, sticky=tkinter.W + tkinter.E + tkinter.N + tkinter.S)


    def _is_updated(self) -> None:
        '''This method will ask the user to check for update.'''
        is_updated = main.check_for_update('http://donkeyandperi.net/download/othello/update/latest_version.txt')
        if is_updated == 1:
            update_info = main.get_update_info('http://donkeyandperi.net/download/othello/update/update_info.txt')
            if update_info == '':
                _show_network_error()
            else:
                if messagebox.askyesno(title='Update', message='Update Found!\n' + update_info + '\nDo you want to update?'):
                    self._root_window.destroy()
                    main.update()
        elif is_updated == 2:
            _show_network_error()
        else:
            _show_notification('Update', 'The program is already up to date!')


    def _init_ok_button(self) -> None:
        '''This will initialize the ok button.'''
        self._ok_button = tkinter.Button(master=self._about, text='OK', command=self._close)
        self._ok_button.grid(row=2, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E + tkinter.N + tkinter.S)


# Other Functions


def _show_notification(title: str, message: str) -> None:
    '''This function will open a messagebox to show a notification.'''
    messagebox.showinfo(title, message)


def _get_str_of_player(player: int, gamestate: module_othello.GameState) -> str:
    '''This method will get the int of the player and return the str of that player.'''
    if player == gamestate.BLACK:
        return 'BLACK'
    elif player == gamestate.WHITE:
        return 'WHITE'
    else:
        return 'EMPTY'


def _get_str_of_rule(rule: int, gamestate: module_othello.GameState) -> str:
    '''This method will get the int of the rule and return the str of the rule.'''
    if rule == gamestate.MORE_WIN_RULE:
        return 'More to win'
    elif rule == gamestate.LESS_WIN_RULE:
        return 'Less to win'


def _rotate_player(player: int, gamestate: module_othello.GameState) -> int:
    '''This method will rotate the player from black to white to empty.'''
    if player == gamestate.BLACK:
        return gamestate.WHITE
    elif player == gamestate.WHITE:
        return gamestate.EMPTY
    else:
        return gamestate.BLACK


def _open_website(url: str) -> None:
    '''This function will open the website using the url being input.'''
    webbrowser.open_new(url)


def get_current_version() -> str:
    '''This function will return the current version.'''
    return 'Beta D'


def _get_opposite_player(player: int, gamestate: module_othello.GameState) -> int:
    '''This function will return the opposite player.'''
    if player == gamestate.BLACK:
        return gamestate.WHITE
    else:
        return gamestate.BLACK


def _show_start_game_warning() -> None:
    '''This function will show a warning for not a valid game has been started.'''
    messagebox.showwarning(title='Warning', message='Please first start a game.')


def _show_network_error() -> None:
    '''This function will show an error about the connection.'''
    messagebox.showerror(title='Update', message='Please Check the Network Connection!')

