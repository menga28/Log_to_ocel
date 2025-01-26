import pandas as pd
import json
import pm4py


class DataModel:
    def __init__(self):
        self.df = None
        self.df_size = 0
        self.nested_columns = []
        self.df_normalized = None
        self.df_size_normalized = 0

    def set_current_file(self, path):
        try:
            with open(path, "r") as file:
                data = json.load(file)
            self.df = pd.DataFrame(data)
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
            'keys': f"Keys of the log: {(str(self.df.columns.to_list()))}",
            'subkeys': f"Sub-keys of the log: {self.nested_keys()}",
            'statistics_df': f"Length of the log: {len(self.df)}, memory usage: {self.get_memory_usage()}"
        }

    def get_memory_usage(self):
        if self.df is None:
            return "N/A"
        memory_usage_bytes = self.df.memory_usage(deep=True).sum()
        self.df_size = memory_usage_bytes / 1024
        return f"{self.df_size:.2f} KB"

    def contains_nested_data(self, column):
        return any(isinstance(i, list) for i in column)

    def nested_keys(self):
        if self.df is None:
            return None
        else:
            self.nested_columns = [
                col for col in self.df.columns if self.contains_nested_data(self.df[col])]
            return self.nested_columns

    def set_default_file(self):
        self.current_file = self.default_file

    def update_file(self, filename):
        self.current_file = filename
