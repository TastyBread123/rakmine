import sys

from javascript import require, On #pip install javascript
from tkinter.messagebox import showerror
from threading import Thread
from configparser import ConfigParser
from customtkinter import *

from windows.rakmine_settings import RakMineSettings

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
maps = require('mineflayer-maps')

config = ConfigParser()
config.read('config.ini')


def check_stat(bot):
    """Получение статистики бота и возврат текcта для Label"""
    if bot is None:
        return f'Ник: None\nЗдоровье: 0 | Сытость: 0 | Кол-во опыта: 0\nРежим игры: None | Coords: None'
    
    try:
        p = bot.entity.position.toString().replace(')', '').replace('(', '')
        text = f'Ник: {bot.username}\nЗдоровье: {int(bot.health)} | Сытость: {int(bot.food)} | Кол-во опыта: {bot.experience.points}\nРежим игры: {bot.game.gameMode} | Coords: {p}'
        return text
    except:
        return f'Ник: None\nЗдоровье: 0 | Сытость: 0 | Кол-во опыта: 0\nРежим игры: None | Coords: None'


class RakMineMain:
    def __init__(self, window: CTk, host: str, nick: str, version: str, thread: Thread) -> None:
        self.thread = thread
        self.window = window

        try: ip, port = host.split(':', maxsplit=1)
        except:
            ip = host 
            port = 25565

        # Настройки
        self.bot = mineflayer.createBot({
            'host': ip,
            'version': version,
            'port': port,
            'maps_outputDir': r"maps",
            'maps_saveToFile': True,
            'username': nick})

        self.bot.loadPlugin(maps.inject)
        self.bot.loadPlugin(pathfinder.pathfinder)
        self.window.title(f"{nick} | {ip}:{port}")

        #bot.setControlState(control, state) | 'forward', 'back', 'left', 'right', # 'jump', 'sprint', 'sneak'
        def control_click(control: str, button: CTkButton):
            if self.bot is None: return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            if str(button._fg_color) == '#4CAF50':
                try: self.bot.setControlState(control, True)
                except: showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
                return button.configure(fg_color = '#EB1043', hover_color = '#FF0000')
            else:
                try: self.bot.setControlState(control, False)
                except: showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
                return button.configure(fg_color = '#4CAF50', hover_color = '#00CC00')

        def send_message(self):
            self.bot.chat(cmd_input.get())
            return cmd_input.delete(0, END)

        self.main_label = CTkLabel(master = self.window, text=str(check_stat(self.bot)))
        self.main_label.place(relx=0.5, rely = 0.03, anchor=N)

        # Чат
        self.chat_log = CTkTextbox(master = self.window, width=750, height=450)
        self.chat_log.place(relx=0.4, rely=0.14, anchor=N)
        cmd_input = CTkEntry(master=self.window, width=550, placeholder_text='Введите команду или текст для отправки от лица бота')
        cmd_input.place(relx=0.6, rely=0.90, anchor=E)
        send_button = CTkButton(master=self.window, text='Отправить', command=lambda: send_message(self))
        send_button.place(relx=0.62, rely=0.90, anchor=W)

        #Клавиши управления
        w_button = CTkButton(master=self.window, text='W', width=50, height=50, fg_color='#4CAF50', hover_color='#00CC00')
        w_button.configure(command = lambda: control_click('forward', w_button))
        w_button.place(relx=0.85, rely=0.21, anchor=W)
        a_button = CTkButton(master=self.window, text='A', width=50, height=50, fg_color='#4CAF50', hover_color='#00CC00')
        a_button.configure(command = lambda: control_click('left', a_button))
        a_button.place(relx=0.80, rely=0.3, anchor=W)
        s_button = CTkButton(master=self.window, text='S', width=50, height=50, fg_color='#4CAF50', hover_color='#00CC00')
        s_button.configure(command = lambda: control_click('back', s_button))
        s_button.place(relx=0.85, rely=0.3, anchor=W)
        d_button = CTkButton(master=self.window, text='D', width=50, height=50, fg_color='#4CAF50', hover_color='#00CC00')
        d_button.configure(command = lambda: control_click('right', d_button))
        d_button.place(relx=0.90, rely=0.3, anchor=W)

        sprint_button = CTkButton(master=self.window, text='Sprint', width=100, height=50, fg_color='#4CAF50', hover_color='#00CC00')
        sprint_button.configure(command = lambda: control_click('sprint', sprint_button))
        sprint_button.place(relx=0.775, rely=0.45, anchor=W)
        jump_button = CTkButton(master=self.window, text='Jump', width=100, height=50, fg_color='#4CAF50', hover_color='#00CC00')
        jump_button.configure(command = lambda: control_click('jump', jump_button))
        jump_button.place(relx=0.88, rely=0.45, anchor=W)
        sneak_button = CTkButton(master=self.window, text='Sneak', width=100, height=50, fg_color='#4CAF50', hover_color='#00CC00')
        sneak_button.configure(command = lambda: control_click('sneak', sneak_button))
        sneak_button.place(relx=0.83, rely=0.55, anchor=W)
        
        settings_button = CTkButton(master=self.window, text='Настройки', command=lambda: RakMineSettings(), width=80, height=35, fg_color='#ff5d00', hover_color="#ad4c13")
        settings_button.place(relx=0.065, rely=0.01, anchor=N)

        config.set('Main', 'username', nick)
        config.set('Main', 'version', version)
        config.set('Main', 'host', host)
        with open('config.ini', "w") as config_file: config.write(config_file)
            
        if int(config.get('Settings', 'clear_chatlog')):
            try: 
                self.main_label.configure(text = check_stat(self.bot))
                self.chat_log.delete(0.0, END)
            except: 
                sys.exit(1)


        @On(self.bot, 'error')
        def error_handler(emittter, err): 
            """Событие при ошибки"""
            return self.log(f'| [BOT ERROR] {err}')

        @On(self.bot, 'message')
        def message_handler(emitter, message_info, *args):
            """Событие при получении любого сообщения"""
            if message_info.extra is None: return False

            message_text = ''
            for i in message_info.extra: message_text+=i.text
            print(f"[MSG] {message_text}")
            return self.log(f'[MSG] {message_text}')

        @On(self.bot, 'chat')
        def chat_handler(emitter, username, message, *args):
            """Событие при получении сообщения из чата ванилы"""
            if message is None: return False
            return self.log(f'[CHAT] {username}: {message}')

        @On(self.bot, 'spawn')
        def spawn_handle(*args):
            """Событие при спавне"""
            try: return self.log(f"| [BOT INFO] Бот заспавнен на {self.bot.entity.position.toString()}!")
            except: pass
        
        @On(self.bot, 'death')
        def death_handle(*args):
            """Событие при смерти"""
            try: return self.log(f"| [BOT INFO] Бот помер на {self.bot.entity.position.toString()}!")
            except: pass
        
        @On(self.bot, 'move')
        def move_handle(*args):
            """Событие при движении"""
            try: return self.main_label.configure(text = check_stat(self.bot))
            except: return sys.exit(1)
        
        @On(self.bot, "health")
        def health_handle(*args): 
            """Событие при изменении здоровья"""
            try: return self.main_label.configure(text = check_stat(self.bot))
            except: return sys.exit(1)
        
        @On(self.bot, "forcedMove")
        def forcedmove_handle(*args):
            """Событие при изменении позиции сервером"""
            try: 
                self.log(f"| [BOT INFO] Бот телепортирован на {self.bot.entity.position.toString()}")
                return self.main_label.configure(text = check_stat(self.bot))
            except: sys.exit(1)
        
        @On(self.bot, 'windowOpen')
        def windowopen_handler(emitter, window):
            """Событие при ошкрытии окна (Например: меню)"""
            return print(window)

        @On(self.bot, "kicked")
        def kicked_handle(emitter, reason, loddedin):
            """Событие при кике сервером"""
            self.bot = None
            try:
                self.log(f"| [BOT INFO] Бот кикнут из сервера!\n| Причина: {reason}")
                return self.main_label.configure(text = check_stat(self.bot))
            except: sys.exit(1)
        
        @On(self.bot, "end")
        def end_handle(emitter, reason):
            """Событие при любое дисконнекте с сервером"""
            self.bot = None
            try:
                self.log(f"| [BOT INFO] Бот отключен от сервера!\n| Причина: {reason}")
                return self.main_label.configure(text = check_stat(self.bot))
            except: sys.exit(1)

        def on_closing():
            self.bot.quit()
            self.window.destroy()  # Закрыть окно
            print("Вы успешно закрыли окно!")


        self.window.protocol("WM_DELETE_WINDOW", on_closing)
    

    def log(self, message: str):
        """Запись в chat log окна"""
        try: return self.chat_log.insert(END, message + '\n')
        except: return sys.exit(1)
        
    