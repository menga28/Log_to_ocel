import os
import time
import json
import random
import string
import logging
import pandas as pd
from app.services.data_service import DataService
from tests.unit.utils import get_all_files, setup_logger
from tests.unit.config import test_configs, p_activity, p_timestamp

# 📌 Configura il logger
os.makedirs("validation/logs", exist_ok=True)
logger = setup_logger("validation_logger", "validation/logs/validation.log")

# 📌 Directory per i risultati
RESULTS_FILE = "validation/results.json"
os.makedirs("validation", exist_ok=True)

# 📌 Funzioni di supporto
def get_file_size_kb(file_path):
    return round(os.path.getsize(file_path) / 1024, 2) if os.path.exists(file_path) else 0.00

def get_dataframe_size_kb(dataframe):
    return round(dataframe.memory_usage(deep=True).sum() / 1024, 2) if dataframe is not None else 0.00

def get_ocel_dataframes(ocel):
    """Restituisce un dizionario con i DataFrame contenuti nell'OCEL."""
    if ocel is None:
        return {}

    df_dict = {}
    for attr_name in dir(ocel):
        attr = getattr(ocel, attr_name)
        if isinstance(attr, pd.DataFrame):
            df_dict[attr_name] = attr

    return df_dict

def get_ocel_size_kb(ocel):
    """Restituisce la dimensione totale dell'OCEL sommando la memoria di tutti i suoi DataFrame."""
    if ocel is None:
        return 0.00

    df_dict = get_ocel_dataframes(ocel)
    total_size = sum(df.memory_usage(deep=True).sum() / 1024 for df in df_dict.values())
    return round(total_size, 2)

def generate_random_string(length=5):
    """Genera una stringa casuale alfanumerica di lunghezza specificata."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_e2o_mapping(data_service):
    """Genera dinamicamente la mappatura per le relazioni E2O basandosi sulle combinazioni presenti in OCEL."""
    if data_service.ocel is None or "relations" not in dir(data_service.ocel):
        return {}

    unique_pairs = data_service.ocel.relations[['ocel:type', 'ocel:activity']].drop_duplicates()

    if unique_pairs.empty:
        logger.warning("⚠️ Nessuna relazione E2O trovata!")
        return {}

    e2o_mapping = {
        f"{row['ocel:type']}|{row['ocel:activity']}": generate_random_string()
        for _, row in unique_pairs.iterrows()
    }

    logger.info(f"🔍 Mappatura E2O generata ({len(e2o_mapping)} relazioni)")
    return e2o_mapping

# 📌 Funzione principale per eseguire la validazione
def run_validation():
    results = []

    logger.info("🚀 Inizio validazione...")
    
    for file_path in get_all_files("tests/input_data/"):
        file_size_kb = get_file_size_kb(file_path)

        for config in test_configs:
            config_name = config["name"]
            data_service = DataService()

            logger.info(f"🔧 Test con configurazione {config_name} per il file {file_path}")

            # 🟢 1. Caricamento del file
            start_time = time.time()
            data_service.load_dataframe(file_path)
            df_size_kb = get_dataframe_size_kb(data_service.df)
            load_time = round(time.time() - start_time, 4)
            logger.info(f"📂 File caricato: {file_path} ({df_size_kb} KB) - Tempo: {load_time}s")

            # 🟢 2. Normalizzazione
            start_time = time.time()
            data_service.normalize_data([0])
            df_size_kb_norm = get_dataframe_size_kb(data_service.df_normalized)
            norm_time = round(time.time() - start_time, 4)
            logger.info(f"🔄 Normalizzazione completata - Tempo: {norm_time}s")

            # 🟢 3. Conversione OCEL
            start_time = time.time()
            data_service.set_ocel_parameters(
                activity=p_activity,
                timestamp=p_timestamp,
                object_types=config["p_object_types"],
                events_attrs=config["p_additional_event_attributes"],
                object_attrs=config["p_additional_object_attributes"]
            )
            ocel_size_kb = get_ocel_size_kb(data_service.ocel)
            ocel_time = round(time.time() - start_time, 4)
            logger.info(f"🔀 OCEL creato - Dimensione: {ocel_size_kb} KB - Tempo: {ocel_time}s")

            # 🟢 4. Creazione delle relazioni E2O
            start_time = time.time()
            e2o_mapping = generate_e2o_mapping(data_service)
            data_service.set_e2o_relationship_qualifiers(e2o_mapping)
            e2o_time = round(time.time() - start_time, 4)
            logger.info(f"🔗 Relazioni E2O impostate - Tempo: {e2o_time}s")

            # 📌 Salva il risultato
            results.append({
                "file": file_path,
                "config": config_name,
                "file_size_kb": file_size_kb,
                "df_size_kb": df_size_kb,
                "df_size_kb_norm": df_size_kb_norm,
                "ocel_size_kb": ocel_size_kb,
                "load_time": load_time,
                "norm_time": norm_time,
                "ocel_time": ocel_time,
                "e2o_time": e2o_time
            })

    # 📌 Salva i risultati in JSON
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)

    logger.info(f"✅ Validazione completata! Risultati salvati in {RESULTS_FILE}")

# 📌 Esegui la validazione
if __name__ == "__main__":
    run_validation()
