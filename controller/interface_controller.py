# controller/interface_controller.py
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.gui import Gui
    from model import DataModel
from pathlib import Path

class InterfaceController:
    """Coordina la logica tra view, model e operazioni di business"""
    
    def __init__(self, gui: Gui, model: DataModel):
        self.gui = gui
        self.model = model
        self._bind_commands()
        self._init_view_data()

    def _bind_commands(self):
        """Collega gli eventi UI alla logica corrispondente"""
        # Home View
        self.gui.get_view('home').bind(
            'btn_select_file', self.load_file
        )
        
        # Row Info View
        self.gui.get_view('row_info').bind(
            'btn_normalize', self.normalize_data
        )
        
        # Subkey Norm View
        self.gui.get_view('subkey_norm').bind(
            'btn_apply', self.apply_normalization
        )

    def _init_view_data(self):
        """Inizializza i dati nelle view"""
        self.gui.get_view('row_info').update_columns(
            self.model.get_available_keys()
        )

    def load_file(self):
        """Gestisce il caricamento file e aggiorna il model"""
        file_path = self.gui.show_file_dialog()
        if file_path:
            self.model.load_data(file_path)
            self.gui.switch('row_info')
            self._refresh_data_views()

    def normalize_data(self, selected_key: str):
        """Avvia il processo di normalizzazione"""
        normalized = self.model.normalize_key(selected_key)
        self.gui.get_view('subkey_norm').display_data(normalized)
        self.gui.switch('subkey_norm')

    def apply_normalization(self):
        """Applica le normalizzazioni e torna alla vista precedente"""
        rules = self.gui.get_view('subkey_norm').get_rules()
        self.model.apply_normalization_rules(rules)
        self.gui.switch('row_info')

    def _refresh_data_views(self):
        """Aggiorna tutte le view con i nuovi dati"""
        for view in ['row_info', 'subkey_norm']:
            self.gui.get_view(view).refresh(
                self.model.get_processed_data()
            )