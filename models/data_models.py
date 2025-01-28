import pandas as pd
import json
import pm4py
import time
from collections import Counter


class DataModel:
    def __init__(self):
        self.df = None
        self.df_size = None
        self.nested_columns = []
        self.df_normalized = None
        self.df_size_normalized = None
        self.start_time = None
        self.end_time = None
        self.ocel = None
        self.number_of_events = 0
        self.number_of_objects = 0
        self.number_of_activities = 0
        self.object_columns = 0
        self.unique_object_values = 0
        self.number_of_object_types = 0
        self.events_objects_relationships = 0
        self.activities_occurrences = 0

    def ocel_info_extraction(self):
        if self.ocel is None:
            print("Errore: self.ocel non è stato inizializzato correttamente.")
            return

        # Numero di eventi e oggetti
        self.number_of_events = len(self.ocel.events)
        self.number_of_objects = len(self.ocel.objects)

        # Numero di attività uniche
        self.number_of_activities = self.ocel.events['ocel:activity'].nunique()

        # Colonne degli oggetti e tipi unici
        self.object_columns = [
            col for col in self.ocel.events.columns
            if col.startswith('ocel:type:')
        ]
        self.number_of_object_types = self.ocel.objects['ocel:type'].nunique()
        self.unique_object_values = self.ocel.objects['ocel:type'].unique()

        # Relazioni evento-oggetto
        self.events_objects_relationships = len(self.ocel.relations)

        # Occorrenze delle attività
        self.activities_occurrences = Counter(
            self.ocel.events['ocel:activity'])

        # Stampa i valori per debug
        print(f"Number of events: {self.number_of_events}")
        print(f"Number of objects: {self.number_of_objects}")
        print(f"Number of activities: {self.number_of_activities}")
        print(f"Number of object types: {self.number_of_object_types}")
        print(
            f"Events-objects relationships: {self.events_objects_relationships}")
        print(f"Activities occurrences: {self.activities_occurrences}")

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
        execution_time = self.end_time - \
            self.start_time if self.start_time and self.end_time else "N/A"
        return {
            'keys': f"Keys: {str(self.df.columns.to_list()).strip('[]')}",
            'subkeys': f"Sub-keys: {str(self.nested_keys()).strip('[]')}",
            'statistics_df': f"Log length: {len(self.df)}, Memory: {self.get_memory_usage()}, Execution time: {execution_time:.5f} seconds",
            'subkeys_normalization': f"Columns to normalize: {str(self.nested_keys()).strip('[]')}",
            'statistics_ocel': f"Object-Centric Event Log statistics: Number of events: {self.number_of_events}, number of objects {self.number_of_objects}: number of activities: {self.number_of_activities}, number of object types: {self.number_of_object_types}, events-objects relationships: {self.events_objects_relationships}\n                                                             Activities occurrences: {self.activities_occurrences}",
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
            self.not_nested_columns = [
                col for col in self.df.columns if not self.contains_nested_data(self.df[col])]
            return self.nested_columns

    def set_default_file(self):
        self.current_file = self.default_file

    def update_file(self, filename):
        self.current_file = filename

    def normalize_data(self, indexes_to_normalize: list):
        # Verifica che il DataFrame non sia vuoto e che ci siano colonne nidificate
        if self.df is None or self.df.empty or not self.nested_columns:
            print("DataFrame non valido o nessuna colonna nidificata disponibile.")
            return None

        # Recupera i nomi delle colonne da normalizzare in base agli indici
        columns_to_normalize = [self.nested_columns[i]
                                for i in indexes_to_normalize if i < len(self.nested_columns)]
        meta_fields = self.not_nested_columns

        if not columns_to_normalize:
            print("Nessuna colonna valida trovata per normalizzare.")
            return None

        # Inizializza un DataFrame vuoto per i dati normalizzati
        normalized_dfs = []

        for col in columns_to_normalize:
            if col in self.df.columns:
                try:
                    # Usa pd.json_normalize per normalizzare i dati
                    normalized_df = pd.json_normalize(
                        self.df.to_dict(orient='records'),
                        record_path=col,  # Colonna da esplodere
                        meta=meta_fields,  # Campi meta
                        record_prefix=f"{col}_"
                    )

                    # Verifica se esiste almeno un campo meta per generare l'ID univoco
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
            print("Nessun DataFrame normalizzato generato.")
            return None

        # Combina tutti i DataFrame normalizzati in uno unico
        self.df_normalized = pd.concat(normalized_dfs, ignore_index=True)

        # Calcola la dimensione del DataFrame normalizzato
        self.df_size_normalized = self.df_normalized.memory_usage(
            deep=True).sum() / 1024
        print(self.df_normalized.head())
        print(str(self.df_normalized.columns.to_list()))
        return self.df_normalized

    def set_ocel_parameters(self, activity, timestamp, object_types, events_attrs, object_attrs):
        print("set_ocel_parameter: ", activity, timestamp,
              object_types, events_attrs, object_attrs)
        self.ocel = pm4py.convert.convert_log_to_ocel(
            log=self.df_normalized,
            activity_column=activity,
            timestamp_column=timestamp,
            object_types=object_types,
            additional_event_attributes=events_attrs,
            additional_object_attributes=object_attrs
        )
        self.ocel.relations["ocel:qualifier"] = self.ocel.relations["ocel:type"]
        print(self.ocel)
        self.ocel_info_extraction()
        self.get_stats()
