from javascript import require, On #pip install javascript
from time import sleep
from customtkinter import *
from tkinter.messagebox import *

import subprocess

import configparser
import tkinter

mineflayer = require('mineflayer')
pathfinder = require('mineflayer-pathfinder')
maps = require('mineflayer-maps')
pathfinder = require('mineflayer-pathfinder')

config = configparser.ConfigParser()
config.read('config.ini')
prefix = '$'
bot = None

cmds = ['exit', 'jump', 'crawl', 'bind', 'bind load', 'bind info', 'bind stop']
#gamemodes = {0: 'Survival', 1: 'Creative', 2: 'Adventure', 3: 'Spectator'}


# Получение статистики и возврат текта
def check_stat():
    if bot is None:
        return f'Ник: None | Режим игры: None | Coords: None\nЗдоровье: 0 | Сытость: 0 | Кол-во опыта: 0'
    try:
        p = bot.entity.position.toString().replace(')', '').replace('(', '')
        text = f'Ник: {bot.username}\nЗдоровье: {int(bot.health)} | Сытость: {int(bot.food)} | Кол-во опыта: {bot.experience.points}\nРежим игры: {bot.game.gameMode} | Coords: {p}'
        return text
    except TypeError:
        return f'Ник: None | Режим игры: None | Coords: None\nЗдоровье: 0 | Сытость: 0 | Кол-во опыта: 0'


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

        #////////
        window.mainloop()


# Главное меню
class RakMineMain:
    def __init__(self, window: CTk) -> None:
        self.in_game = False
        self.nick = 'None'
        self.health = 0
        self.satiety = 0
        self.gamemode = 'None'
        self.total_exp = 0

        def send_message():
            global bot
            if bot is None:
                cmd_input.delete(0, END)
                return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            
            if cmd_input.get().startswith(prefix):
                cmd = cmd_input.get().replace('$', '')
                #if cmd not in cmds: return log(f'| [CMD] Команда "{cmd}" не найдена!')
                if cmd == 'exit':
                    bot.quit(); bot = None; self.in_game = False
                    log('[CMD] Бот успешно вышел из игры!')
                    return cmd_input.delete(0, END)
                
                if cmd.startswith('move'):
                    pos = str(cmd.replace('move ', '')).split(' ')
                    if len(pos) != 3:
                        return log('[CMD] Использование: $move x y z')
                    bot.pathfinder.setMovements(pathfinder.Movements(bot))
                    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(int(pos[0]), int(pos[1]), int(pos[2]), 1))
                
                return True
            
            bot.chat(cmd_input.get())
            return cmd_input.delete(0, END)
        

        # Запись в chat log
        def log(message: str): return chat_log.insert(END, message + '\n')

        def bot_join():
            global bot
            
            if nick_input.get() is None or nick_input.get() == '':
                return showerror('Ошибка RakMine', 'Вы не ввели имя пользователя!')
            elif host_input.get() is None or host_input.get() == '':
                return showerror('Ошибка RakMine', 'Вы не ввели адрес сервера!')
            elif version_input.get() is None or version_input.get() == '':
                return showerror('Ошибка RakMine', 'Вы не ввели версию игры!')
            
            if bot is not None: bot.quit()
            
            ip = host_input.get().split(':')
            try: port = ip[1]
            except IndexError: port = 25565

            # Настройки
            bot = mineflayer.createBot({#для бота
                'host': ip[0],
                'version': version_input.get(),
                'port': port,
                'maps_outputDir': r"maps",
                'maps_saveToFile': True,
                'username': nick_input.get()})

            bot.loadPlugin(maps.inject)
            bot.loadPlugin(pathfinder.pathfinder)

            config.set('Main', 'username', nick_input.get())
            config.set('Main', 'version', version_input.get())
            config.set('Main', 'host', host_input.get())
            with open('config.ini', "w") as config_file: config.write(config_file)
            
            if int(config.get('Settings', 'clear_chatlog')):
                try: self.main_label.configure(text = check_stat())
                except: pass
                chat_log.delete(0.0, END)
                window.title(f"{nick_input.get()} | {host_input.get()}")


            @On(bot, 'error')
            def error_handler(emittter, err):
                return log(f'| [BOT ERROR] {err}')

            @On(bot, 'message')
            def message_handler(emitter, message_info, *args):
                if message_info.extra is None: return False

                new_text = ''
                for i in message_info.extra: new_text+=str(i.text)
                return log(f'[MSG] {new_text}')
            
            @On(bot, 'new_map_save')
            def map_handler(emitter, name, fullPath):
                log(f'[MAP] Новая карта: {fullPath}')
                subprocess.Popen(fullPath, shell=True)

            @On(bot, 'chat')
            def message_handler(emitter, username, message, *args):
                if message is None: return False
                return log(f'[CHAT] {username}: {message}')

            @On(bot, 'spawn')
            def spawn_handle(*args):
                self.in_game = True
                return log(f"| [BOT INFO] Бот заспавнен на {bot.entity.position.toString()}!")
            
            @On(bot, 'death')
            def spawn_handle(*args):
                self.in_game = True
                return log(f"| [BOT INFO] Бот помер на {bot.entity.position.toString()}!")
            
            @On(bot, "end")
            def end_handle(emitter, reason):
                global bot
                self.in_game = False; bot = None
                log(f"| [BOT INFO] Бот отключен от сервера!\n| Причина: {reason}")
                return self.main_label.configure(text = check_stat())
            
            @On(bot, 'move')
            def move_handle(*args):
                return self.main_label.configure(text = check_stat())
            
            @On(bot, "kicked")
            def end_handle(emitter, reason, loddedin):
                global bot
                self.in_game = False; bot = None
                
                log(f"| [BOT INFO] Бот кикнут из сервера!\n| Причина: {reason}")
                return self.main_label.configure(text = check_stat())
            
            @On(bot, "health")
            def end_handle(*args):
                self.in_game = True
                return self.main_label.configure(text = check_stat())
            
            @On(bot, "forcedMove")
            def forcedMove(*args):
                p = bot.entity.position
                self.in_game = True
                log(f"| [BOT INFO] Бот телепортирован на {p.toString()}")
            
            @On(bot, 'windowOpen')
            def window_handler(emitter, window):
                print(window)


        #bot.setControlState(control, state) | 'forward', 'back', 'left', 'right', # 'jump', 'sprint', 'sneak'
        def w_click():
            if bot is None: return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            if str(w_button._fg_color) == '#4CAF50':
                bot.setControlState('forward', True)
                return w_button.configure(fg_color = '#eb1043')
            else:
                bot.setControlState('forward', False)
                return w_button.configure(fg_color = '#4CAF50')
        def s_click():
            if bot is None: return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            if str(s_button._fg_color) == '#4CAF50':
                bot.setControlState('back', True)
                return s_button.configure(fg_color = '#eb1043')
            else:
                bot.setControlState('back', False)
                return s_button.configure(fg_color = '#4CAF50')

        def a_click():
            if bot is None: return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            if str(a_button._fg_color) == '#4CAF50':
                bot.setControlState('left', True)
                return a_button.configure(fg_color = '#eb1043')
            else:
                bot.setControlState('left', False)
                return a_button.configure(fg_color = '#4CAF50')
        def d_click():
            if bot is None: return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            if str(d_button._fg_color) == '#4CAF50': 
                bot.setControlState('right', True)
                return d_button.configure(fg_color = '#eb1043')
            else:
                bot.setControlState('right', False)
                return d_button.configure(fg_color = '#4CAF50')
        def sprint_click():
            if bot is None: return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            if str(sprint_button._fg_color) == '#4CAF50': 
                bot.setControlState('sprint', True)
                return sprint_button.configure(fg_color = '#eb1043')
            else:
                bot.setControlState('sprint', False)
                return sprint_button.configure(fg_color = '#4CAF50')
        def jump_click():
            if bot is None: return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            if str(jump_button._fg_color) == '#4CAF50': 
                bot.setControlState('jump', True)
                return jump_button.configure(fg_color = '#eb1043')
            else:
                bot.setControlState('jump', False)
                return jump_button.configure(fg_color = '#4CAF50')
        def sneak_click():
            if bot is None: return showerror('Ошибка RakMine', 'Бот не запущен на сервере!')
            if str(sneak_button._fg_color) == '#4CAF50': 
                bot.setControlState('sneak', True)
                return sneak_button.configure(fg_color = '#eb1043')
            else:
                bot.setControlState('sneak', False)
                return sneak_button.configure(fg_color = '#4CAF50')

        #Основа
        self.main_label = CTkLabel(master = window, text=str(check_stat()))
        self.main_label.place(relx=0.5, rely = 0.03, anchor=tkinter.N)

        nick_input = CTkEntry(master=window, width=213, placeholder_text='Ник бота')
        nick_input.place(relx=0.13, rely=0.12, anchor=tkinter.N)
        nick_input.insert(INSERT, config.get('Main', 'username'))
        host_input = CTkEntry(master=window, width=250, placeholder_text='Адрес сервера формата ip:port / host')
        host_input.place(relx=0.39, rely=0.12, anchor=tkinter.N)
        host_input.insert(INSERT, config.get('Main', 'host'))
        version_input = CTkEntry(master=window, width=70, placeholder_text='Версия')
        version_input.place(relx=0.56, rely=0.12, anchor=tkinter.N)
        version_input.insert(INSERT, config.get('Main', 'version'))
        cmd_input = CTkEntry(master=window, width=550, placeholder_text='Введите команду или текст для отправки от лица бота')
        cmd_input.place(relx=0.6, rely=0.90, anchor=tkinter.E)

        chat_log = CTkTextbox(master = window, width=750, height=420)
        chat_log.place(relx=0.4, rely=0.19, anchor=tkinter.N)

        join_button = CTkButton(master=window, text='Запустить', command=bot_join)
        join_button.place(relx=0.61, rely=0.14, anchor=tkinter.W)
        send_button = CTkButton(master=window, text='Отправить', command=send_message)
        send_button.place(relx=0.62, rely=0.90, anchor=tkinter.W)

        #Клавиши управления
        w_button = CTkButton(master=window, text='W', command=w_click, width=50, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        w_button.place(relx=0.85, rely=0.21, anchor=tkinter.W)
        a_button = CTkButton(master=window, text='A', command=a_click, width=50, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        a_button.place(relx=0.80, rely=0.3, anchor=tkinter.W)
        s_button = CTkButton(master=window, text='S', command=s_click, width=50, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        s_button.place(relx=0.85, rely=0.3, anchor=tkinter.W)
        d_button = CTkButton(master=window, text='D', command=d_click, width=50, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        d_button.place(relx=0.90, rely=0.3, anchor=tkinter.W)

        sprint_button = CTkButton(master=window, text='Sprint', command=sprint_click, width=100, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        sprint_button.place(relx=0.775, rely=0.45, anchor=tkinter.W)
        jump_button = CTkButton(master=window, text='Jump', command=jump_click, width=100, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        jump_button.place(relx=0.88, rely=0.45, anchor=tkinter.W)
        sneak_button = CTkButton(master=window, text='Sneak', command=sneak_click, width=100, height=50, fg_color='#4CAF50', hover_color='#eb1043')
        sneak_button.place(relx=0.83, rely=0.55, anchor=tkinter.W)

        def open_settings():
            return RakMineSettings()
        settings_button = CTkButton(master=window, text='Настройки', command=open_settings, width=80, height=35, fg_color='#ff5d00', hover_color="#ad4c13")
        settings_button.place(relx=0.065, rely=0.01, anchor=tkinter.N)

# Начало
if __name__ == "__main__":
    window = CTk()
    window.title("RakMine")
    window.geometry('1000x620')
    RakMineMain(window=window)
    window.mainloop()