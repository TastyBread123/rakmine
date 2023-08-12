from customtkinter import CTk
from windows.rakmine_join import RakMineJoin

# Начало
if __name__ == "__main__":
    window = CTk()
    window.title("RakMine")
    window.geometry('300x400')
    RakMineJoin(window=window)
    #RakMineMain(window=window).log("текст")
