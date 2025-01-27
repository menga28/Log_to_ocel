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
        self.activity_selection = [] 
        self.timestamp_selection = []  
        self.object_types_selection = []
        self.events_attrs_selection = []
        self.object_attrs_selection = {}

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
            if 'ocel_preview' in self.text_ids:
                canvas.itemconfig(
                    self.text_ids['ocel_preview']['statistics_ocel'],
                    text=stats['statistics_ocel']
                )

    def handle_view_parameter_selection(self):
        selected_indices = self.view.current_frame.listbox.curselection()
        selected_indices = list(map(int, selected_indices))
        self.model.normalize_data(selected_indices)
        self.view.show_parameter_selection(self)
        if hasattr(self, 'update_columns'):
            self.update_columns(self.model.df_normalized.columns)

    def handle_ocel_preview(self):
        self.view.show_ocel_preview(self)
        self._update_stats()

    def handle_ocel_export(self):
        print("Exporting to OCEL")

    def handle_show_ocel_preview(self):
        self.view.show_ocel_preview(self)
        self._update_stats()

        print("\nParametri selezionati: ")
        # Recupera le selezioni dagli dropdown
        activity = self.activity_selection[0] if self.activity_selection else None
        timestamp = self.timestamp_selection[0] if self.timestamp_selection else None
        object_types = self.object_types_selection
        events_attrs = self.events_attrs_selection
        object_attrs = self.object_attrs_selection
        print(activity, timestamp, object_types, events_attrs, object_attrs)

        self.model.set_ocel_parameters(
            activity, timestamp, object_types, events_attrs, object_attrs)
