from typing import TypedDict
from enum import Enum, auto
from .home import homegGui


class Guis(TypedDict):
    homegGui: homegGui


class Gui:
    def __init__(self):
        self.root = Root()
        self.guis: Guis = {}
        self.current_gui = None
        self.add_gui(homegGui, "homegGui")
        self.guis["homegGui"] = homegGui(self)

    def get_view(self, name: str) -> BaseView:
        return self.guis[name]

    def add_gui(self, Gui, name: str) -> None:
        self.guis[name] = Gui(self.root)


    def switch(self, name: str) -> None:
        if name not in self.guis:
            raise ValueError(f"Gui {name} not found")
        self.new_gui = self.guis[name]
        if self.current_gui is not None:
            self.current_gui.tkraise()
        self.current_gui = self.new_gui
        self.current_gui.place(x=0, y=0)


    def start_mainloop(self):
        self.root.mainloop()
