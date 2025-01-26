from models.data_models import DataModel
from tkinter import filedialog
import os

class Controller:
    def __init__(self, view):
        self.view = view
        self.model = DataModel()
        self.default_file_path= os.path.join("Datasets","pancacke100txs.json")

    def start(self):
        self.view.show_home(self)

    # Handlers per Home
    def handle_home_button3(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.model.set_current_file(file_path)
            self.view.show_row_info(self)
            self._update_stats()

    def handle_home_button4(self):
        self.model.set_current_file(self.default_file_path)
        self.view.show_row_info(self)
        self._update_stats()

    # Handlers per Row Info
    def handle_row_button5(self):
        self.view.show_sub_key_norm(self)

    def handle_row_button6(self):
        self.model.update_file("nuovo_file.json")
        self._update_stats()

    def _update_stats(self):
        stats = self.model.get_stats()
        if hasattr(self.view.current_frame, 'canvas'):
            canvas = self.view.current_frame.canvas
            canvas.itemconfig(
                self.text_ids['keys'], 
                text=stats['keys']
            )
            canvas.itemconfig(
                self.text_ids['subkeys'],
                text=stats['subkeys']
            )
            canvas.itemconfig(
                self.text_ids['statistics_df'],
                text=stats['statistics_df']
            )

    def handle_subkey_button1(self):
        self.model.update_file("altro_file.json")
        self.view.show_row_info(self)

    def handle_subkey_button2(self):
        print("Navigazione non implementata")
