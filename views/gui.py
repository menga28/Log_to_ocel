import tkinter as tk
from views.home import create_home
from views.row_info import create_row_info
from views.sub_key_norm import create_sub_key_norm
from views.parameter_selection import create_parameter_selection
from views.ocel_preview import create_ocel_preview

class Gui:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1440x1024")
        self.current_frame = None
        
    def show_frame(self, frame_func, controller):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = frame_func(self.root, controller)
        self.current_frame.pack_propagate(False)  # Disabilita l'auto-ridimensionamento
        self.current_frame.pack(fill="both", expand=True)
        self.root.update()  # Forza un refresh immediato

    def show_home(self, controller):
        self.show_frame(create_home, controller)

    def show_row_info(self, controller):
        self.show_frame(create_row_info, controller)

    def show_sub_key_norm(self, controller):
        self.show_frame(create_sub_key_norm, controller)
        
    def show_parameter_selection(self, controller):
        self.show_frame(create_parameter_selection, controller)
    
    def show_ocel_preview(self, controller):
        self.show_frame(create_ocel_preview, controller)