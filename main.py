# Myles Liu, yuxil11@uci.edu, 50997122


# Import


import module_ui
import urllib.request
import importlib
import tkinter
from tkinter import messagebox
from tkinter import ttk
import time


# Classes


class UpdateWindow:
    '''This is the class for the Update Window.'''


    def __init__(self) -> None:
        '''This method is used to initialize the update window.'''
        self._root_window = tkinter.Tk()
        self._root_window.iconbitmap('moe_icon.ico')
        self._root_window.wm_title('Updating')
        self._is_just_started = True
        self._refresh_label_info('Initializing')
        self._init_progressbar()
        self._progressbar.after(1, self._start_update)
        self._root_window.mainloop()


    def _start_update(self) -> None:
        '''This method will start the update.'''
        fail_count_and_info = self._update()
        messagebox.showinfo(title='Update Completed', message='Error Count:' + str(fail_count_and_info[0]) + '\n' + fail_count_and_info[1])
        self._close()


    def _refresh_label_info(self, progress: str) -> None:
        '''This method will refresh the label info.'''
        if not self._is_just_started:
            self._info_label.destroy()
        self._info_label = tkinter.Label(master=self._root_window, text='Update Progress: ' + progress)
        self._info_label.grid(row=0, column=0, padx=10, pady=10, sticky=tkinter.NSEW)


    def _init_progressbar(self) -> None:
        '''This method will start the progressbar'''
        self._progressbar = ttk.Progressbar(master=self._root_window, length=100)
        self._progressbar.grid(row=1, column=0, padx=10, pady=10, sticky=tkinter.NSEW)


    def _refresh_all(self, progress: str, step: int) -> None:
        '''This method will refresh the whole things.'''
        self._is_just_started = False
        self._refresh_label_info(progress)
        self._progressbar.step(step)
        self._progressbar.update()


    def _update(self) -> tuple:
        '''This method will start the update.'''
        fail_count = 0
        self._continue_progressbar('Updating Game Logic...', 20)
        print(_update_module('module_othello.py'))
        if not _update_module('module_othello.py'):
            fail_count += 1
        self._continue_progressbar('Updating Game AI...', 20)
        if not _update_module('module_othello_ai.py'):
            fail_count += 1
        self._continue_progressbar('Updating Game UI...', 20)
        if not _update_module('module_ui.py'):
            fail_count += 1
        self._continue_progressbar('Updating Main Program...', 20)
        if not _update_module('main.py'):
            fail_count += 1
        self._continue_progressbar('Update Completing...', 20)
        importlib.reload(module_ui)
        message_from_server = download_content_from_url('http://donkeyandperi.net/download/othello/update/message.txt').read().decode('utf-8')
        time.sleep(2)
        return fail_count, message_from_server


    def _continue_progressbar(self, message: str, step: int) -> None:
        '''This method is ued to show the animation of the progressbar.'''
        for x in range(step):
            self._refresh_all(message, 1)
            time.sleep(0.08)


    def _close(self) -> None:
        '''This method will close the whole window.'''
        self._root_window.destroy()


# Core Function


def download_content_from_url(url: str) -> 'response':
    '''This function is used to download the content and return it.'''
    request = urllib.request.Request(url, headers={'User-Agent': 'Chrome/57.0'})
    response = urllib.request.urlopen(request)
    return response


def check_for_update(url: str) -> int:
    '''This function will check whether there is an update. return 0 if there is not, return 1 if there is, return 2 if there is error.'''
    try:
        response = download_content_from_url(url)
        if response.read().decode('utf-8') == module_ui.get_current_version():
            return 0
        else:
            return 1
    except:
        return 2


def get_update_info(url: str) -> str:
    '''This function will get the update info.'''
    try:
        response = download_content_from_url(url)
        return response.read().decode('utf-8')
    except:
        return ''


def _update_module(module_name: str) -> bool:
    '''Update the module, return True if success.'''
    try:
        module = open(module_name, 'w')
        module.write(
            download_content_from_url('http://donkeyandperi.net/download/othello/update/' + module_name).read().decode(
                'utf-8'))
        module.close()
        return True
    except:
        return False


def update() -> None:
    '''This function will update the program and rerun it.'''
    update_window = UpdateWindow()
    main()


# Main


def main() -> None:
    '''This is the main function.'''
    m = module_ui.MainWindow()
    m.run()


if __name__ == '__main__':
    main()
    # update()