from views.gui import Gui
from controller.controller import Controller
import tkinter as tk

def main():
    root = tk.Tk()
    view = Gui(root)
    controller = Controller(view)
    controller.start()
    root.mainloop()

if __name__ == '__main__':
    main()