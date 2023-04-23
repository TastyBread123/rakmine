import configparser
import tkinter

from javascript import require, On #pip install javascript
from customtkinter import *
from tkinter.messagebox import *
from functools import partial

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
maps = require('mineflayer-maps')

config = configparser.ConfigParser()
config.read('config.ini')
prefix = '$'
cmds = ['exit']

bot = None


# Получение статистики и возврат текта
def check_stat():
    if bot is None:
        return f'Ник: None\nЗдоровье: 0 | Сытость: 0 | Кол-во опыта: 0\nРежим игры: None | Coords: None'
    try:
        p = bot.entity.position.toString().replace(')', '').replace('(', '')
        text = f'Ник: {bot.username}\nЗдоровье: {int(bot.health)} | Сытость: {int(bot.food)} | Кол-во опыта: {bot.experience.points}\nРежим игры: {bot.game.gameMode} | Coords: {p}'
        return text
    except:
        return f'Ник: None\nЗдоровье: 0 | Сытость: 0 | Кол-во опыта: 0\nРежим игры: None | Coords: None'


# Настройки
class RakMineSettings:
    def __init__(self) -> None:
        def set_clear_log():
            config.set('Settings', 'clear_chatlog', str(clear_log_var.get()))
            with open('config.ini', "w") as config_file: config.write(config_file)
            return True
        
        window = CTk()
        window.title("RakMine | Настройки")
        window.geometry('700x420')
        
        #очистка лога
        clear_log_var = IntVar(window, value=int(config.get('Settings', 'clear_chatlog')))
        clear_log = CTkCheckBox(master=window, variable=clear_log_var, text='Очистка чатлога после реконнекта', command=set_clear_log)
        clear_log.place(relx=0.01, rely=0.01)

        # Loop
        window.mainloop()


class RakMineJoin:
    def __init__(self, window: CTk) -> None:
        nick_input = CTkEntry(master=window, width=213, placeholder_text='Ник бота')
        nick_input.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)
        nick_input.insert(INSERT, config.get('Main', 'username'))
        host_input = CTkEntry(master=window, width=250, placeholder_text='Адрес сервера формата ip:port / host')
        host_input.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)
        host_input.insert(INSERT, config.get('Main', 'host'))
        version_input = CTkEntry(master=window, width=70, placeholder_text='Версия')
        version_input.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
        version_input.insert(INSERT, config.get('Main', 'version'))

        def bot_join():            
            if nick_input.get() is None or nick_input.get() == '':
                return showerror('Ошибка RakMine', 'Вы не ввели имя пользователя!')
            elif host_input.get() is None or host_input.get() == '':
                return showerror('Ошибка RakMine', 'Вы не ввели адрес сервера!')
            elif version_input.get() is None or version_input.get() == '':
                return showerror('Ошибка RakMine', 'Вы не ввели версию игры!')
            
            window = CTk()
            window.title("RakMine")
            window.geometry('1000x620')
            RakMineMain(window, host_input.get(), nick_input.get(), version_input.get())
            
        join_button = CTkButton(master=window, text='Запустить', command=bot_join)
        join_button.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

        window.mainloop()


# Главное меню
class RakMineMain:
    def __init__(self, window: CTk, host: str, nick: str, version: str) -> None:
        def send_message():
            cmd_input.delete(0.0, END)
            return bot.chat(cmd_input.get())
        
        #bot.setControlState(control, state) | 'forward', 'back', 'left', 'right', # 'jump', 'sprint', 'sneak'
        def control_click(control: str, button: CTkButton):
            if bot is None: return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            if str(button._fg_color) == '#4CAF50':
                bot.setControlState(control, True)
                return button.configure(fg_color = '#eb1043')
            else:
                bot.setControlState(control, False)
                return button.configure(fg_color = '#4CAF50')
        
        global bot

        self.main_label = CTkLabel(master = window, text=str(check_stat()))
        self.main_label.place(relx=0.5, rely = 0.03, anchor=tkinter.N)

        cmd_input = CTkEntry(master=window, width=550, placeholder_text='Введите команду или текст для отправки от лица бота')
        cmd_input.place(relx=0.6, rely=0.90, anchor=tkinter.E)

        self.chat_log = CTkTextbox(master = window, width=750, height=420)
        self.chat_log.place(relx=0.4, rely=0.19, anchor=tkinter.N)

        send_button = CTkButton(master=window, text='Отправить', command=send_message)
        send_button.place(relx=0.62, rely=0.90, anchor=tkinter.W)

        #Клавиши управления
        w_button = CTkButton(master=window, text='W', width=50, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        w_button.configure(command = partial(control_click, 'forward', w_button))
        w_button.place(relx=0.85, rely=0.21, anchor=tkinter.W)
        a_button = CTkButton(master=window, text='A', width=50, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        a_button.configure(command = partial(control_click, 'left', a_button))
        a_button.place(relx=0.80, rely=0.3, anchor=tkinter.W)
        s_button = CTkButton(master=window, text='S', width=50, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        s_button.configure(command = partial(control_click, 'back', s_button))
        s_button.place(relx=0.85, rely=0.3, anchor=tkinter.W)
        d_button = CTkButton(master=window, text='D', width=50, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        d_button.configure(command = partial(control_click, 'right', d_button))
        d_button.place(relx=0.90, rely=0.3, anchor=tkinter.W)

        sprint_button = CTkButton(master=window, text='Sprint', width=100, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        sprint_button.configure(command = partial(control_click, 'sprint', sprint_button))
        sprint_button.place(relx=0.775, rely=0.45, anchor=tkinter.W)
        jump_button = CTkButton(master=window, text='Jump', width=100, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        jump_button.configure(command = partial(control_click, 'jump', jump_button))
        jump_button.place(relx=0.88, rely=0.45, anchor=tkinter.W)
        sneak_button = CTkButton(master=window, text='Sneak', width=100, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        sneak_button.configure(command = partial(control_click, 'sneak', sneak_button))
        sneak_button.place(relx=0.83, rely=0.55, anchor=tkinter.W)

        def open_settings(): return RakMineSettings()
        settings_button = CTkButton(master=window, text='Настройки', command=open_settings, width=80, height=35, fg_color='#ff5d00', hover_color="#ad4c13")
        settings_button.place(relx=0.065, rely=0.01, anchor=tkinter.N)

        if bot is not None: bot.quit()
        
        ip = host.split(':')
        try: port = ip[1]
        except IndexError: port = 25565

        # Настройки
        bot = mineflayer.createBot({
            'host': ip[0],
            'version': version,
            'port': port,
            'maps_outputDir': r"maps",
            'maps_saveToFile': True,
            'username': nick})

        bot.loadPlugin(maps.inject)
        bot.loadPlugin(pathfinder.pathfinder)

        config.set('Main', 'username', nick)
        config.set('Main', 'version', version)
        config.set('Main', 'host', host)
        with open('config.ini', "w") as config_file: config.write(config_file)
            
        if int(config.get('Settings', 'clear_chatlog')):
            try: self.main_label.configure(text = check_stat())
            except: pass

            self.chat_log.delete(0.0, END)
            window.title(f"{nick} | {ip[0]}:{port}")


        @On(bot, 'error')
        def error_handler(emittter, err): return self.log(f'| [BOT ERROR] {err}')


        @On(bot, 'message')
        def message_handler(emitter, message_info, *args):
            if message_info.extra is None: return False

            new_text = ''
            for i in message_info.extra: new_text+=str(i.text)
            return self.log(f'[MSG] {new_text}')


        @On(bot, 'chat')
        def message_handler(emitter, username, message, *args):
            if message is None: return False
            return self.log(f'[CHAT] {username}: {message}')


        @On(bot, 'spawn')
        def spawn_handle(*args):
            self.in_game = True
            try: return self.log(f"| [BOT INFO] Бот заспавнен на {bot.entity.position.toString()}!")
            except: pass
        

        @On(bot, 'death')
        def spawn_handle(*args):
            self.in_game = True
            try: return self.log(f"| [BOT INFO] Бот помер на {bot.entity.position.toString()}!")
            except: pass
        

        @On(bot, "end")
        def end_handle(emitter, reason):
            global bot
            self.in_game = False; bot = None
            self.log(f"| [BOT INFO] Бот отключен от сервера!\n| Причина: {reason}")
            return self.main_label.configure(text = check_stat())
        
        
        @On(bot, 'move')
        def move_handle(*args): return self.main_label.configure(text = check_stat())
            
        
        @On(bot, "kicked")
        def end_handle(emitter, reason, loddedin):
            global bot
            self.in_game = False; bot = None
                
            self.log(f"| [BOT INFO] Бот кикнут из сервера!\n| Причина: {reason}")
            return self.main_label.configure(text = check_stat())
            
        
        @On(bot, "health")
        def end_handle(*args):
            self.in_game = True
            return self.main_label.configure(text = check_stat())
            
        
        @On(bot, "forcedMove")
        def forcedMove(*args):
            self.in_game = True
            try:
                p = bot.entity.position
                return self.log(f"| [BOT INFO] Бот телепортирован на {p.toString()}")
            except: pass
            
        
        @On(bot, 'windowOpen')
        def window_handler(emitter, window): return print(window)
        
        window.mainloop()
    
    # Запись в chat log
    def log(self, message: str): return self.chat_log.insert(END, message + '\n')

# Начало
if __name__ == "__main__":
    window = CTk()
    window.title("RakMine")
    window.geometry('300x400')
    RakMineJoin(window=window)
    #RakMineMain(window=window).log("текст")
