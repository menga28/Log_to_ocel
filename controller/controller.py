from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.gui import Gui
from controller.interface_controller import InterfaceController

class Controller:
    def __init__(self, gui: Gui) -> None:
        self.gui = gui
        self.interface_controller = InterfaceController(self)
        
    def start(self) -> None:
        self.view.start_mainloop()