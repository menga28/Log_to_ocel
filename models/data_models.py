import pandas as pd
import json
import pm4py
import time


class DataModel:
    def __init__(self):
        self.df = None
        self.df_size = None
        self.nested_columns = []
        self.df_normalized = None
        self.df_size_normalized = None
        self.start_time = None
        self.end_time = None

    def set_current_file(self, path):
        try:
            self.start_time = time.time()
            with open(path, "r") as file:
                data = json.load(file)
            self.df = pd.DataFrame(data)
            self.end_time = time.time()
        except ValueError as e:
            print(f"Errore di struttura JSON: {str(e)}")
            self.df = None
        except Exception as e:
            print(f"Errore generico: {str(e)}")
            self.df = None

    def get_stats(self):
        execution_time = self.end_time - self.start_time if self.start_time and self.end_time else "N/A"
        return {
            'keys': f"Keys: {str(self.df.columns.to_list()).strip('[]')}",
            'subkeys': f"Sub-keys: {str(self.nested_keys()).strip('[]')}",
            'statistics_df': f"Log length: {len(self.df)}, Memory: {self.get_memory_usage()}, Execution time: {execution_time:.5f} seconds",
            'subkeys_normalization': f"Columns to normalize: {str(self.nested_keys()).strip('[]')}"
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
