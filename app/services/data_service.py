import pandas as pd
import json
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataService:
    def __init__(self):
        self.df = None
        self.df_normalized = None
        self.nested_columns = []
        self.not_nested_columns = []
        self.start_time = None
        self.end_time = None
        self.error = None
        self.current_file = None
        self.df_size_normalized = 0

    def contains_nested_data(self, column):
        return any(isinstance(i, list) for i in column)

    def nested_keys(self):
        if self.df is None:
            return None
        self.nested_columns = [
            col for col in self.df.columns if self.contains_nested_data(self.df[col])]
        self.not_nested_columns = [
            col for col in self.df.columns if not self.contains_nested_data(self.df[col])]
        return self.nested_columns

    def load_dataframe(self, filepath):
        self.start_time = time.time()
        try:
            if filepath.endswith('.csv'):
                self.df = pd.read_csv(filepath)
            elif filepath.endswith('.json'):
                with open(filepath, "r") as file:
                    data = json.load(file)
                self.df = pd.DataFrame(data)
            self.nested_keys()
            self.end_time = time.time()
            self.current_file = filepath
            return self.df
        except Exception as e:
            self.error = str(e)
            return None

    def get_preview_data(self):
        if self.df is None:
            return None
        return {
            'data': self.df.head(10).to_dict('records'),
            'columns': list(self.df.columns),
            'nested_columns': self.nested_columns,
            'not_nested_columns': self.not_nested_columns
        }

    def normalize_data(self, indexes_to_normalize: list):
        if self.df is None or self.df.empty or not self.nested_columns:
            return None

        columns_to_normalize = [self.nested_columns[i]
                                for i in indexes_to_normalize if i < len(self.nested_columns)]
        meta_fields = self.not_nested_columns

        if not columns_to_normalize:
            return None

        normalized_dfs = []

        for col in columns_to_normalize:
            if col in self.df.columns:
                try:
                    normalized_df = pd.json_normalize(
                        self.df.to_dict(orient='records'),
                        record_path=col,
                        meta=meta_fields,
                        record_prefix=f"{col}_"
                    )

                    if meta_fields:
                        normalized_df[f"{col}__id"] = f"{col}_" + normalized_df[meta_fields[0]].astype(str) + "_" + (
                            normalized_df.groupby(meta_fields[0]).cumcount() + 1).astype(str)
                    else:
                        normalized_df[f"{col}__id"] = f"{col}_" + \
                            normalized_df.index.astype(str)

                    normalized_dfs.append(normalized_df)
                except Exception as e:
                    print(
                        f"Errore durante la normalizzazione della colonna {col}: {str(e)}")
            else:
                print(f"Colonna {col} non trovata nel DataFrame.")

        if not normalized_dfs:
            return None

        self.df_normalized = pd.concat(normalized_dfs, ignore_index=True)
        self.df_sie_normalized = self.df_normalized.memory_usage(
            deep=True).sum() / 1024
        logger.info(f"Head of normalized DataFrame:\n{self.df_normalized.columns.to_list}")

