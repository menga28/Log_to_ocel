import pandas as pd
import json
import time
import logging
import pm4py

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
        self.ocel = None

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
                    logging.error(
                        f"Errore durante la normalizzazione della colonna {col}: {str(e)}")
            else:
                logging.info(f"Colonna {col} non trovata nel DataFrame.")

        if not normalized_dfs:
            return None

        self.df_normalized = pd.concat(normalized_dfs, ignore_index=True)
        self.df_sie_normalized = self.df_normalized.memory_usage(
            deep=True).sum() / 1024
        logger.info(
            f"Head of normalized DataFrame:\n{self.df_normalized.columns.to_list}")

    def set_ocel_parameters(self, activity, timestamp, object_types, events_attrs, object_attrs):
        print("set_ocel_parameters:", activity, timestamp,
              object_types, events_attrs, object_attrs)

        if self.df_normalized is None:
            raise ValueError("Normalized DataFrame is not available.")

        try:
            self.ocel = pm4py.convert.convert_log_to_ocel(
                log=self.df_normalized,
                activity_column=activity,
                timestamp_column=timestamp,
                object_types=object_types,
                additional_event_attributes=events_attrs,
                additional_object_attributes=object_attrs
            )
        except Exception as e:
            logger.error("Error converting log to OCEL: %s", str(e))
            raise e

        logger.info("OCEL created: %s", self.ocel)
        self.ocel_info_extraction()
        self.get_stats()
        self.save_file("ocel_created")

    def set_relationship_qualifiers(self, qualifier_map):
        converted_map = {}
        for key, value in qualifier_map.items():
            converted_key = tuple(key.split("|"))
            converted_map[converted_key] = value
        logger.info("OCEL created: %s", self.ocel)
        logger.info("Qualifier map: %s", converted_map)
        try:
            self.ocel.relations['ocel:qualifier'] = self.ocel.relations.apply(
                lambda row: converted_map.get((row['ocel:type'], row['ocel:activity']), row['ocel:qualifier']), axis=1
            )
            self.ocel.relations = self.ocel.relations[self.ocel.relations['ocel:qualifier'].notnull(
            )]
            logger.info("Updated relationship qualifiers.")
            self.save_file("ocel_e2o_qualifiers")
        except Exception as e:
            logger.error("Error setting relationship qualifiers: %s", str(e))
            raise e

    # TODO
    def ocel_info_extraction(self):
        pass

    # TODO
    def get_stats(self):
        pass

    def save_file(self, file_name: str):
        pm4py.write.write_ocel2_json(self.ocel, file_name + ".jsonocel")
