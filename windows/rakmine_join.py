from threading import Thread
from configparser import ConfigParser
from customtkinter import *
from tkinter.messagebox import showerror

from windows.rakmine_main import RakMineMain

config = ConfigParser()
config.read('config.ini')


class RakMineJoin:
    def __init__(self, window: CTk) -> None:
        nick_input = CTkEntry(master=window, width=213, placeholder_text='Ник бота')
        nick_input.place(relx=0.5, rely=0.2, anchor=CENTER)
        nick_input.insert(INSERT, config.get('Main', 'username'))
        host_input = CTkEntry(master=window, width=250, placeholder_text='Адрес сервера формата ip:port / host')
        host_input.place(relx=0.5, rely=0.3, anchor=CENTER)
        host_input.insert(INSERT, config.get('Main', 'host'))
        version_input = CTkEntry(master=window, width=70, placeholder_text='Версия')
        version_input.place(relx=0.5, rely=0.4, anchor=CENTER)
        version_input.insert(INSERT, config.get('Main', 'version'))


        def bot_join():
            """Заход бота """      
            if nick_input.get() is None or nick_input.get() == '': return showerror('Ошибка RakMine', 'Вы не ввели имя пользователя!')
            elif host_input.get() is None or host_input.get() == '': return showerror('Ошибка RakMine', 'Вы не ввели адрес сервера!')
            elif version_input.get() is None or version_input.get() == '': return showerror('Ошибка RakMine', 'Вы не ввели версию игры!')
            
            window = CTkToplevel()
            window.title("RakMine")
            window.geometry('1000x620')
            thread = None
            thread = Thread(target=RakMineMain, args=(window, host_input.get(), nick_input.get(), version_input.get(), thread))
            thread.start()

            
        join_button = CTkButton(master=window, text='Запустить', command=bot_join)
        join_button.place(relx=0.5, rely=0.6, anchor=CENTER)

        window.mainloop()