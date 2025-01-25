import pandas as pd
import json
import pm4py

class DataModel:
    def __init__(self):
        self.df = None

    def set_current_file(self, path):
        try:
            # Usa orient='columns' per JSON con struttura a colonne
            self.df = pd.read_json(path, orient='columns')  
            
            # Alternativa per JSON non strutturati
            # self.df = pd.json_normalize(pd.read_json(path))
            
        except ValueError as e:
            print(f"Errore di struttura JSON: {str(e)}")
            self.df = None
        except Exception as e:
            print(f"Errore generico: {str(e)}")
            self.df = None

    def get_stats(self):
        if self.df is None:
            return {
                'keys': "N/A",
                'subkeys': "N/A",
                'stats': "N/A"
            }

        return {
            'keys': f"{len(self.df)} chiavi rilevate",
            'subkeys': f"{len(self.df.columns)} sottochiavi",
            'stats': "Statistiche aggiornate"
        }

    def set_default_file(self):
        self.current_file = self.default_file

    def update_file(self, filename):
        self.current_file = filename

    def get_stats(self):
        # Esempio, implementa la logica reale
        return {
            'keys': "10 chiavi rilevate",
            'subkeys': "5 sottochiavi",
            'stats': "Statistiche aggiornate"
        }
