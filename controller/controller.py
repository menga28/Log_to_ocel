from models.data_models import DataModel
from tkinter import filedialog
import os
import pandas as pd


class Controller:
    def __init__(self, view):
        self.view = view
        self.model = DataModel()
        self.default_file_path = os.path.join(
            "Datasets", "pancacke100txs.json")
        self.text_ids = {}

    def start(self):
        self.view.show_home(self)

    def handle_set_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.model.set_current_file(file_path)
            self.view.show_row_info(self)
            self._update_stats()

    def handle_set_default_file(self):
        self.model.set_current_file(self.default_file_path)
        self.view.show_row_info(self)
        self._update_stats()

    # Handlers per Row Info
    def handle_row_button5(self):
        self.view.show_sub_key_norm(self)
        self._update_stats()

    def _update_stats(self):
        stats = self.model.get_stats()
        if hasattr(self.view.current_frame, 'canvas'):
            canvas = self.view.current_frame.canvas
            if 'row_info' in self.text_ids:
                canvas.itemconfig(
                    self.text_ids['row_info']['keys'],
                    text=stats['keys']
                )
                canvas.itemconfig(
                    self.text_ids['row_info']['subkeys'],
                    text=stats['subkeys']
                )
                canvas.itemconfig(
                    self.text_ids['row_info']['statistics_df'],
                    text=stats['statistics_df']
                )
            if 'sub_key_norm' in self.text_ids:
                canvas.itemconfig(
                    self.text_ids['sub_key_norm']['subkeys_normalization'],
                    text=stats['subkeys_normalization']
                )
                if hasattr(self, 'update_columns'):
                    self.update_columns(self.model.nested_keys())
                if hasattr(self, 'update_treeview') and self.model.df is not None:
                    self.update_treeview(self.model.df.head(25))

    def handle_subkey_button1(self):
        self.view.show_row_info(self)
        self._update_stats()
