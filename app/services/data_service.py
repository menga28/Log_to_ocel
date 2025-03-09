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
        self.ocel_o2o = None

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

            logger.info(f"✅ DEBUG: Caricamento riuscito per {filepath}.")
            logger.info(f"📊 DEBUG: Anteprima DataFrame:\n{self.df.head()}")
            return self.df

        except Exception as e:
            self.error = str(e)
            logger.error(f"❌ ERRORE: Caricamento di {filepath} fallito - {e}")
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
        if self.df is None or self.df.empty:
            logger.error("❌ DEBUG: DataFrame vuoto o non valido.")
            return None

        if not self.nested_columns:
            logger.error(
                "⚠️ DEBUG: Nessuna colonna nidificata trovata nel DataFrame.")
            logger.error(f"Colonne disponibili: {self.df.columns.tolist()}")
            return None

        columns_to_normalize = [self.nested_columns[i]
                                for i in indexes_to_normalize if i < len(self.nested_columns)]
        meta_fields = self.not_nested_columns

        if not columns_to_normalize:
            logger.error("⚠️ DEBUG: Nessuna colonna valida da normalizzare.")
            return None

        logger.info(
            f"🔄 DEBUG: Normalizzazione in corso per le colonne: {columns_to_normalize}")

        normalized_dfs = []

        for col in columns_to_normalize:
            if col in self.df.columns:
                try:
                    logger.info(f"📊 DEBUG: Normalizzando colonna {col}...")
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
                    logger.info(
                        f"✅ DEBUG: Colonna {col} normalizzata con {len(normalized_df)} righe.")

                except Exception as e:
                    logger.error(
                        f"❌ ERRORE durante la normalizzazione della colonna {col}: {str(e)}")

            else:
                logger.warning(
                    f"⚠️ DEBUG: Colonna {col} non trovata nel DataFrame.")

        if not normalized_dfs:
            logger.error(
                "❌ DEBUG: Nessuna colonna è stata normalizzata, restituisco None.")
            return None

        self.df_normalized = pd.concat(normalized_dfs, ignore_index=True)
        self.df_size_normalized = self.df_normalized.memory_usage(
            deep=True).sum() / 1024
        logger.info(
            f"✅ DEBUG: DataFrame normalizzato con {len(self.df_normalized)} righe e colonne: {self.df_normalized.columns.tolist()}")
        return self.df_normalized

    def set_ocel_parameters(self, activity, timestamp, object_types, events_attrs, object_attrs):
        logger.info(f"📌 set_ocel_parameters called with: "
                    f"activity={activity}, timestamp={timestamp}, object_types={object_types}, "
                    f"events_attrs={events_attrs}, object_attrs={object_attrs}")

        if self.df_normalized is None:
            logger.error("❌ Error: Normalized DataFrame is not available.")
            raise ValueError("Normalized DataFrame is not available.")

        # **Controllo se le colonne esistono**
        if activity not in self.df_normalized.columns:
            logger.error(
                f"❌ Error: Activity column '{activity}' not found in DataFrame.")
            raise ValueError(
                f"Activity column '{activity}' not found in DataFrame.")

        if timestamp not in self.df_normalized.columns:
            logger.error(
                f"❌ Error: Timestamp column '{timestamp}' not found in DataFrame.")
            raise ValueError(
                f"Timestamp column '{timestamp}' not found in DataFrame.")

        logger.info(f"🔍 DEBUG: Object types passati a OCEL: {object_types}")
        logger.info(f"🔍 DEBUG: Colonne disponibili nel DataFrame normalizzato: {self.df_normalized.columns.tolist()}")


        try:
            self.ocel = pm4py.convert.convert_log_to_ocel(
                log=self.df_normalized,
                activity_column=activity,
                timestamp_column=timestamp,
                object_types=object_types,
                additional_event_attributes=events_attrs,
                additional_object_attributes=object_attrs
            )
            logger.info("✅ OCEL log created successfully!")

        except Exception as e:
            logger.error(f"❌ Error converting log to OCEL: {str(e)}")
            raise e

        self.ocel_info_extraction()
        self.get_stats()
        self.save_file(self.ocel, "ocel_created")

    def set_e2o_relationship_qualifiers(self, qualifier_map):
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
            self.save_file(self.ocel, "ocel_e2o_qualifiers")
        except Exception as e:
            logger.error("Error setting relationship qualifiers: %s", str(e))
            raise e

    def o2o_enrichment(self, included_graphs=["object_interaction_graph"]):
        if self.ocel is None:
            raise ValueError(
                "OCEL log has not been created. Please run set_ocel_parameters first.")
        try:
            # Enrich the existing OCEL with O2O relations.
            self.ocel_o2o = pm4py.ocel_o2o_enrichment(
                self.ocel, included_graphs=included_graphs)
            # Initialize the 'ocel:qualifier' field to None.
            self.ocel_o2o.o2o["ocel:qualifier"] = None
            logger.info("O2O enrichment completed. OCEL_o2o created.")
            self.save_file(self.ocel_o2o, "ocel_o2o")
        except Exception as e:
            logger.error("Error during O2O enrichment: %s", str(e))
            raise e

    def set_o2o_relationship_qualifiers(self, qualifier_map):
        # Convert keys from string "oid|oid_2" to tuple.
        converted_map = {}
        for key, value in qualifier_map.items():
            converted_key = tuple(key.split("|"))
            converted_map[converted_key] = value
        try:
            # Apply the mapping: update the qualifier with the provided value; if the qualifier remains empty, it will be dropped.
            self.ocel_o2o.o2o['ocel:qualifier'] = self.ocel_o2o.o2o.apply(
                lambda row: converted_map.get(
                    (row['ocel:oid'], row['ocel:oid_2']), row['ocel:qualifier']),
                axis=1
            )
            # Drop rows where qualifier is null or an empty string.
            self.ocel_o2o.o2o = self.ocel_o2o.o2o[
                self.ocel_o2o.o2o['ocel:qualifier'].notnull() &
                (self.ocel_o2o.o2o['ocel:qualifier'] != "")
            ]
            logger.info(
                "Updated O2O relationship qualifiers and dropped rows with null qualifier.")
            self.save_file(self.ocel_o2o, "ocel_o2o_qualifiers")
        except Exception as e:
            logger.error(
                "Error setting O2O relationship qualifiers: %s", str(e))
            raise e

    # TODO
    def ocel_info_extraction(self):
        pass

    # TODO
    def get_stats(self):
        pass

    def save_file(self, obj, file_name: str):
        try:
            logger.info(f"📂 Saving OCEL log to {file_name}.jsonocel")
            pm4py.write.write_ocel2_json(obj, file_name + ".jsonocel")
            logger.info("✅ OCEL log saved successfully!")
        except Exception as e:
            logger.error(f"❌ Error saving OCEL log: {str(e)}")
            raise e
