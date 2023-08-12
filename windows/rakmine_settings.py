from configparser import ConfigParser
from customtkinter import *

config = ConfigParser()
config.read('config.ini')

# Настройки
class RakMineSettings:
    def __init__(self) -> None:
        def set_clear_log():
            config.set('Settings', 'clear_chatlog', clear_log_var.get())
            with open('config.ini', "w") as config_file: config.write(config_file)
            return True
        
        window = CTkToplevel()
        window.title("RakMine | Настройки")
        window.geometry('700x420')
        
        #очистка лога
        clear_log_var = IntVar(window, value=int(config.get('Settings', 'clear_chatlog')))
        clear_log = CTkCheckBox(master=window, variable=clear_log_var, text='Очистка чатлога после реконнекта', command=set_clear_log)
        clear_log.place(relx=0.01, rely=0.01)
