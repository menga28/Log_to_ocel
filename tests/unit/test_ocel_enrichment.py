import pytest
import time
import os
import pandas as pd
import random
import string
from tests.unit.utils import get_all_files, setup_logger
from tests.unit.config import test_configs, p_activity, p_timestamp
from app.services.data_service import DataService

# Configura il logger per salvare i log in un file CSV
logger = setup_logger("test_results", "validation/logs/test_results.csv")


@pytest.fixture(scope="module")
def data_service():
    """Utilizza una sola istanza di DataService per tutti i test del modulo."""
    return DataService()


def get_file_size_kb(file_path):
    """Restituisce la dimensione del file in KB o 0.00 se non esiste."""
    if os.path.exists(file_path):
        return round(os.path.getsize(file_path) / 1024, 2)
    logger.warning(f"File non trovato: {file_path}")
    return 0.00


def get_dataframe_size_kb(dataframe):
    """Restituisce la dimensione del DataFrame in KB o 0.00 se è vuoto o None."""
    return round(dataframe.memory_usage(deep=True).sum() / 1024, 2) if dataframe is not None else 0.00


def get_ocel_dataframes(ocel):
    """Restituisce un dizionario con i DataFrame contenuti nell'OCEL."""
    if ocel is None:
        return {}

    df_dict = {}

    for attr_name in dir(ocel):  # Scansiona tutti gli attributi dell'OCEL
        attr = getattr(ocel, attr_name)  # Ottieni il valore dell'attributo
        if isinstance(attr, pd.DataFrame):  # Se è un DataFrame, lo aggiunge
            df_dict[attr_name] = attr

    return df_dict  # Ritorna un dizionario { nome_dataframe: DataFrame }


def get_ocel_size_kb(ocel):
    """Restituisce la dimensione totale dell'OCEL sommando la memoria di tutti i suoi DataFrame."""

    if ocel is None:
        return 0.00

    df_dict = get_ocel_dataframes(ocel)  # Ottiene tutti i DataFrame
    total_size = sum(df.memory_usage(deep=True).sum(
    ) / 1024 for df in df_dict.values())  # Calcola la somma delle dimensioni

    return round(total_size, 2)  # Restituisce la dimensione totale


def generate_random_string(length=5):
    """Genera una stringa casuale alfanumerica di lunghezza specificata."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_e2o_mapping(data_service):
    """Genera dinamicamente la mappatura per le relazioni E2O basandosi sulle combinazioni presenti in OCEL."""
    if data_service.ocel is None or "relations" not in dir(data_service.ocel):
        return {}

    # Prendi tutte le combinazioni presenti nel log OCEL
    unique_pairs = data_service.ocel.relations[[
        'ocel:type', 'ocel:activity']].drop_duplicates()

    if unique_pairs.empty:
        logger.warning("Nessuna relazione E2O trovata!")
        return {}

    # Crea un mapping con chiavi 'tipo|attività' e valori stringhe casuali
    e2o_mapping = {
        f"{row['ocel:type']}|{row['ocel:activity']}": generate_random_string()
        for _, row in unique_pairs.iterrows()
    }

    logger.info(
        f"Mappatura E2O generata ({len(e2o_mapping)} relazioni): {e2o_mapping}")
    return e2o_mapping


def generate_o2o_mapping(data_service):
    """Genera dinamicamente la mappatura per le relazioni O2O basandosi sulle combinazioni presenti in OCEL."""
    if data_service.ocel_o2o is None or "o2o" not in dir(data_service.ocel_o2o):
        logger.warning(
            "O2O: OCEL O2O non trovato, nessuna mappatura creata.")
        return {}

    # Prendi tutte le combinazioni uniche di oggetti collegati tra loro
    unique_pairs = data_service.ocel_o2o.o2o[[
        'ocel:oid', 'ocel:oid_2']].drop_duplicates()

    if unique_pairs.empty:
        logger.warning("Nessuna relazione O2O trovata!")
        return {}

    # Crea un mapping con chiavi 'oggetto_1|oggetto_2' e valori stringhe casuali
    o2o_mapping = {
        f"{row['ocel:oid']}|{row['ocel:oid_2']}": generate_random_string()
        for _, row in unique_pairs.iterrows()
    }

    logger.info(
        f"Mappatura O2O generata ({len(o2o_mapping)} relazioni): {o2o_mapping}")
    return o2o_mapping


def log_step(step_name, start_time, file_path, config_name, file_size_kb, df_size_kb, ocel_size_kb, success=True, error_message=None):
    """Registra un passo nel file CSV con il tempo impiegato, dimensioni e configurazione usata."""
    elapsed_time = round(time.time() - start_time, 4)
    status = "PASS" if success else "FAIL"
    message = error_message if error_message else "OK"

    log_entry = f"{file_path},{config_name},{step_name},{status},{elapsed_time:.4f},{file_size_kb:.2f},{df_size_kb:.2f},{ocel_size_kb:.2f},{message}"
    logger.info(log_entry)


@pytest.mark.parametrize("file_path", get_all_files("tests/input_data/"))
def test_ocel_enrichment(data_service, file_path):
    """Test completo per OCEL enrichment su tutti i file di input, usando tutte le configurazioni una sola volta."""

    file_size_kb = get_file_size_kb(file_path)

    for config in test_configs:
        config_name = config["name"]
        logger.info(
            f"⚙️ DEBUG: Test con configurazione {config_name} per il file {file_path}")

        # 🟢 1. Caricamento del file
        start_time = time.time()
        data_service.load_dataframe(file_path)
        df_size_kb = get_dataframe_size_kb(data_service.df)
        log_step("Load DataFrame", start_time, file_path,
                 config_name, file_size_kb, df_size_kb, 0.00)

        # 🟢 2. Normalizzazione
        start_time = time.time()
        data_service.normalize_data([0])
        df_size_kb = get_dataframe_size_kb(data_service.df_normalized)
        log_step("Normalize Data", start_time, file_path,
                 config_name, file_size_kb, df_size_kb, 0.00)

        # 🟢 3. Conversione OCEL
        start_time = time.time()
        try:
            data_service.set_ocel_parameters(
                activity=p_activity,
                timestamp=p_timestamp,
                object_types=config["p_object_types"],
                events_attrs=config["p_additional_event_attributes"],
                object_attrs=config["p_additional_object_attributes"]
            )
            ocel_size_kb = get_ocel_size_kb(data_service.ocel)
            log_step("Set OCEL Parameters", start_time, file_path,
                     config_name, file_size_kb, df_size_kb, ocel_size_kb)
        except Exception as e:
            pytest.fail(f"Errore nella conversione OCEL: {str(e)}")

        # 🟢 4. Creazione delle relazioni E2O
        start_time = time.time()
        try:
            e2o_mapping = generate_e2o_mapping(data_service)
            data_service.set_e2o_relationship_qualifiers(e2o_mapping)
            log_step("Set E2O Relationships", start_time, file_path, config_name,
                     file_size_kb, df_size_kb, get_ocel_size_kb(data_service.ocel))
        except Exception as e:
            pytest.fail(
                f"Errore nella creazione delle relazioni E2O: {str(e)}")

        # 🟢 5. Creazione delle relazioni O2O
        start_time = time.time()
        try:
            data_service.o2o_enrichment()

            if data_service.ocel_o2o is None:
                logger.error(
                    "OCEL O2O enrichment non riuscito, `ocel_o2o` è None.")
                pytest.fail("Errore: OCEL O2O non è stato creato.")

            o2o_mapping = generate_o2o_mapping(data_service)
            if not o2o_mapping:
                logger.warning(
                    "Nessuna relazione O2O trovata, salto il mapping.")

            data_service.set_o2o_relationship_qualifiers(o2o_mapping)
            log_step("Set O2O Relationships", start_time, file_path, config_name,
                     file_size_kb, df_size_kb, get_ocel_size_kb(data_service.ocel))
        except Exception as e:
            pytest.fail(
                f"Errore nella creazione delle relazioni O2O: {str(e)}")
