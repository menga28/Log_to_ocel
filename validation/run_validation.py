import sys
import os
from app.services.data_service import DataService
from tests.unit.utils import get_all_files
import time
import json
import pandas as pd
import argparse
import logging
import string
import random
import threading

p_activity = "activity"
p_timestamp = "timestamp"

# Configura il logger
os.makedirs("validation/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Directory per i risultati
RESULTS_FILE = "validation/results.json"
os.makedirs("validation", exist_ok=True)

# Definisci un lock globale
file_write_lock = threading.Lock()

# Funzioni di supporto


def generate_o2o_mapping(data_service):
    """Genera la mappatura per le relazioni O2O e restituisce anche il numero di relazioni totali."""
    if data_service.ocel_o2o is None or "o2o" not in dir(data_service.ocel_o2o):
        logger.warning("O2O: OCEL O2O non trovato.")
        return {}, 0

    df = data_service.ocel_o2o.o2o[['ocel:oid', 'ocel:oid_2']]
    total_relations = len(df)

    if df.empty:
        logger.warning("Nessuna relazione O2O trovata!")
        return {}, 0

    unique_pairs = df.drop_duplicates()
    o2o_mapping = {
        f"{row['ocel:oid']}|{row['ocel:oid_2']}": generate_random_string()
        for _, row in unique_pairs.iterrows()
    }

    logger.info(
        f"Mappatura O2O generata ({len(o2o_mapping)} mapping da {total_relations} relazioni totali)")
    return o2o_mapping, total_relations


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
    logger.info(f"DataFrames trovati nell'OCEL: {list(df_dict.keys())}")

    total_size = 0
    for name, df in df_dict.items():
        size_kb = df.memory_usage(deep=True).sum() / 1024
        logger.info(f"DataFrame '{name}' size: {size_kb:.2f} KB")
        total_size += size_kb

    return round(total_size, 2)


def generate_random_string(length=5):
    """Genera una stringa casuale alfanumerica di lunghezza specificata."""
    # return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return "aaaaa"


def generate_e2o_mapping(data_service):
    """Genera la mappatura per le relazioni E2O e restituisce anche il numero di relazioni totali."""
    if data_service.ocel is None or "relations" not in dir(data_service.ocel):
        return {}, 0

    df = data_service.ocel.relations[['ocel:type', 'ocel:activity']]
    total_relations = len(df)

    if df.empty:
        logger.warning("Nessuna relazione E2O trovata!")
        return {}, 0

    unique_pairs = df.drop_duplicates()
    e2o_mapping = {
        f"{row['ocel:type']}|{row['ocel:activity']}": generate_random_string()
        for _, row in unique_pairs.iterrows()
    }

    # LOG_DISABLED: logger.info(f"Mappatura E2O generata ({len(e2o_mapping)} mapping da {total_relations} relazioni totali)")
    return e2o_mapping, total_relations


def assign_columns_to_objects_and_events(df_columns, num_objects, num_event_attr):
    """
    Assegna le colonne del DataFrame normalizzato agli oggetti e agli eventi, 
    escludendo 'activity' e 'timestamp'.
    """
    # random.seed(1999)
    filtered_columns = [
        col for col in df_columns if col not in ["activity", "timestamp"]]

    random.shuffle(filtered_columns)  # 💥 Mischia le colonne ad ogni esecuzione

    object_types = filtered_columns[:num_objects]
    event_attrs = filtered_columns[num_objects:num_objects + num_event_attr]
    return object_types, event_attrs


def get_normalizable_columns(df):
    """
    Restituisce un elenco di colonne normalizzabili nel DataFrame.
    """
    normalizable_columns = []
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            normalizable_columns.append(col)
    # LOG_DISABLED: logger.info("Colonne normalizzabili:" + str(normalizable_columns))
    return normalizable_columns


def append_result(new_result):
    results_file = "validation/results.json"
    with file_write_lock:
        if os.path.exists(results_file):
            with open(results_file, "r") as f:
                try:
                    existing_results = json.load(f)
                except json.JSONDecodeError:
                    existing_results = []
        else:
            existing_results = []

        existing_results.append(new_result)

        with open(results_file, "w") as f:
            json.dump(existing_results, f, indent=4)


def run_validation(event_attr_pct, object_pct, object_attr_pct, log_pct):
    results = []

    logger.info("Inizio validazione...")

    file_path = "tests/input_data/Pancake1000.json"
    file_size_kb = get_file_size_kb(file_path)
    data_service = DataService()

    # 🟢 1. Caricamento del file
    start_time = time.perf_counter()
    data_service.load_dataframe(file_path)
    if 0 < log_pct < 100:
        original_len = len(data_service.df)
        data_service.df = data_service.df.head(
            int((log_pct / 100) * original_len))
        # LOG_DISABLED: logger.info(f"Dataset ridotto al {log_pct}%: da {original_len} a {len(data_service.df)} righe")
    df_size_kb = get_dataframe_size_kb(data_service.df)
    load_time = round(time.perf_counter() - start_time, 4)
    # LOG_DISABLED: logger.info(f"File caricato: {file_path} ({df_size_kb} KB) - Tempo: {load_time}s")

    # 🟢 2. Normalizzazione
    normalizable_columns = get_normalizable_columns(data_service.df)
    if normalizable_columns:
        normalizable_indexes = [data_service.nested_columns.index(
            col) for col in normalizable_columns if col in data_service.nested_columns]
        # LOG_DISABLED: logger.info(f"🛠 DEBUG: Indici per la normalizzazione: {normalizable_indexes}")
        # LOG_DISABLED: logger.info(f"🛠 DEBUG: Colonne effettive del DataFrame: {data_service.df.columns.tolist()}")
        start_time = time.perf_counter()
        data_service.normalize_data(normalizable_indexes)
        df_size_kb_norm = get_dataframe_size_kb(data_service.df_normalized)
        norm_time = round(time.perf_counter() - start_time, 4)
        # LOG_DISABLED: logger.info(f"🔄 Normalizzazione completata per colonne: {normalizable_columns} - Tempo: {norm_time}s")
    else:
        logger.warning("Nessuna colonna normalizzabile trovata.")

    if data_service.df_normalized is not None:
        normalized_columns = list(data_service.df_normalized.columns)
        # LOG_DISABLED: logger.info(f"Colonne dopo normalizzazione: {normalized_columns}")
        # LOG_DISABLED: logger.info(f"DEBUG: Prime 5 righe del DataFrame normalizzato:\n{data_service.df_normalized.head()}")
    else:
        logger.error("Errore: df_normalized è None dopo la normalizzazione.")
        normalized_columns = []

    num_objects = min(
        int((object_pct / 100) * len(normalized_columns)), len(normalized_columns))
    num_event_attr = min(int((event_attr_pct / 100) *
                         len(normalized_columns)), len(normalized_columns) - num_objects)
    object_types, events_attrs = assign_columns_to_objects_and_events(
        normalized_columns, num_objects, num_event_attr)
    num_object_attr = min(int((object_attr_pct / 100) *
                          len(events_attrs)), len(events_attrs))
    object_attrs = {
        obj: [obj] + random.sample(events_attrs,
                                   num_object_attr) if num_object_attr > 0 else [obj]
        for obj in object_types
    }
    # LOG_DISABLED: logger.info(f"DEBUG: `object_attrs` costruito correttamente:\n{json.dumps(object_attrs, indent=4)}")
    # LOG_DISABLED: logger.info(f"Configurazione calcolata - Oggetti: {object_types}, Eventi: {events_attrs}, Attributi/Oggetto: {object_attrs}")

    # 🟢 3. Conversione OCEL
    start_time = time.perf_counter()
    try:
        data_service.set_ocel_parameters(
            activity=p_activity,
            timestamp=p_timestamp,
            object_types=object_types,
            events_attrs=events_attrs,
            object_attrs=object_attrs
        )
    except Exception as e:
        logger.error(f"Errore durante `set_ocel_parameters`: {str(e)}")
    ocel_size_kb_created = get_ocel_size_kb(data_service.ocel)
    ocel_time = round(time.perf_counter() - start_time, 4)
    # LOG_DISABLED: logger.info(f"🔀 OCEL creato - Dimensione: {ocel_size_kb_created} KB - Tempo: {ocel_time}s")

    # 🟢 4. Relazioni E2O
    start_time = time.perf_counter()
    e2o_mapping, num_e2o_relations = generate_e2o_mapping(data_service)
    data_service.set_e2o_relationship_qualifiers(e2o_mapping)
    ocel_size_kb_e2o = get_ocel_size_kb(data_service.ocel)
    e2o_time = round(time.perf_counter() - start_time, 4)
    # LOG_DISABLED: logger.info(f"🔗 Relazioni E2O impostate - Tempo: {e2o_time}s")

    # 🟢 5. Relazioni O2O
    start_time = time.perf_counter()
    try:
        data_service.o2o_enrichment()
        if data_service.ocel_o2o is None:
            logger.error(
                "OCEL O2O enrichment non riuscito, `ocel_o2o` è None.")
            raise RuntimeError("Errore: OCEL O2O non è stato creato.")
        o2o_mapping, num_o2o_relations = generate_o2o_mapping(data_service)
        if not o2o_mapping:
            logger.warning(
                "Nessuna relazione O2O trovata, salto il mapping.")
        data_service.set_o2o_relationship_qualifiers(o2o_mapping)
        ocel_size_kb_o2o = get_ocel_size_kb(data_service.ocel_o2o)
        o2o_time = round(time.perf_counter() - start_time, 4)
        # LOG_DISABLED: logger.info(f"🔁 Relazioni O2O impostate - Tempo: {o2o_time}s")
    except Exception as e:
        logger.error(f"Errore nella creazione delle relazioni O2O: {str(e)}")
        ocel_size_kb_o2o = 0
        o2o_time = 0.0

    results.append({
        "input": {
            "event_attr_pct": event_attr_pct,
            "object_pct": object_pct,
            "object_attr_pct": object_attr_pct,
            "log_pct": log_pct
        },
        "derived": {
            "file": file_path,
            "file_size_kb": file_size_kb,
            "df_size_kb": df_size_kb,
            "df_size_kb_norm": df_size_kb_norm,
            "num_total_columns": len(normalized_columns),
            "num_objects": num_objects,
            "num_event_attr": num_event_attr,
            "num_object_attr": num_object_attr,
            "num_e2o_relations": num_e2o_relations,
            "num_o2o_relations": num_o2o_relations,
            "ocel_size_kb_created": ocel_size_kb_created,
            "ocel_size_kb_e2o": ocel_size_kb_e2o,
            "ocel_size_kb_o2o": ocel_size_kb_o2o
        },
        "timings": {
            "load_time": load_time,
            "norm_time": norm_time,
            "ocel_time": ocel_time,
            "e2o_time": e2o_time,
            "o2o_time": o2o_time
        }
    })

    append_result(results[0])
    logger.info(
        f"Validazione completata! Risultati salvati in {RESULTS_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Esegui la validazione con parametri personalizzati")
    parser.add_argument("--event_attr_pct", type=int, required=True,
                        help="Numero di event attribute in % sul numero totale di colonne (max 100%)")
    parser.add_argument("--object_pct", type=int, required=True,
                        help="Numero di oggetti in % sul numero totale di colonne (max 100%)")
    parser.add_argument("--object_attr_pct", type=int, required=True,
                        help="Numero di attributi per oggetto in % sul numero totale di colonne + 1")
    parser.add_argument("--log_pct", type=int, default=100,
                        help="Percentuale del log da includere nel DataFrame (0-100)")
    args = parser.parse_args()

    if args.event_attr_pct > 100 or args.object_pct > 100 or args.object_attr_pct > 100:
        logger.error("Le percentuali non possono superare il 100%")
        exit(1)

    run_validation(args.event_attr_pct, args.object_pct,
                   args.object_attr_pct, args.log_pct)
