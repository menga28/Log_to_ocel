import pytest
import time
import os
import pandas as pd
from validation.tests.utils import get_all_files, setup_logger
from validation.tests.config import test_configs, p_activity, p_timestamp
from app.services.data_service import DataService

# 📌 Configura il logger per salvare i log in un file CSV
logger = setup_logger("test_results", "validation/logs/test_results.csv")


@pytest.fixture(scope="module")
def data_service():
    """Utilizza una sola istanza di DataService per tutti i test del modulo."""
    return DataService()


def get_file_size_kb(file_path):
    """Restituisce la dimensione del file in KB o 0.00 se non esiste."""
    if os.path.exists(file_path):
        return round(os.path.getsize(file_path) / 1024, 2)
    logger.warning(f"⚠️ File non trovato: {file_path}")
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
        return 0.00, {}  # OCEL non esiste, ritorna size 0 e nessuna informazione sui DataFrame

    df_dict = get_ocel_dataframes(ocel)  # Ottiene tutti i DataFrame
    total_size = sum(df.memory_usage(deep=True).sum(
    ) / 1024 for df in df_dict.values())  # Calcola la somma delle dimensioni

    # Creiamo un dizionario con i dettagli di ogni DataFrame
    df_sizes = {df_name: round(df.memory_usage(
        deep=True).sum() / 1024, 2) for df_name, df in df_dict.items()}

    # Restituisce la dimensione totale e il dettaglio dei singoli DataFrame
    return round(total_size, 2), df_sizes


def log_step(step_name, start_time, file_path, config_name, file_size_kb, df_size_kb, ocel_size_kb, ocel_df_sizes, success=True, error_message=None):
    """Registra un passo nel file CSV con il tempo impiegato, dimensioni e configurazione usata."""
    elapsed_time = round(time.time() - start_time, 4)
    status = "PASS" if success else "FAIL"
    message = error_message if error_message else "OK"

    # Convertiamo il dizionario dei DataFrame OCEL in una stringa leggibile
    ocel_df_sizes_str = "; ".join(
        [f"{k}: {v} KB" for k, v in ocel_df_sizes.items()]) if ocel_df_sizes else "None"

    log_entry = f"{file_path},{config_name},{step_name},{status},{elapsed_time:.4f},{file_size_kb:.2f},{df_size_kb:.2f},{ocel_size_kb:.2f},{ocel_df_sizes_str},{message}"
    logger.info(log_entry)


@pytest.mark.parametrize("file_path", get_all_files("validation/input_data/"))
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
                 config_name, file_size_kb, df_size_kb, 0.00, {})

        # 🟢 2. Normalizzazione
        start_time = time.time()
        data_service.normalize_data([0])
        df_size_kb = get_dataframe_size_kb(data_service.df_normalized)
        log_step("Normalize Data", start_time, file_path,
                 config_name, file_size_kb, df_size_kb, 0.00, {})

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
            ocel_size_kb, ocel_df_sizes = get_ocel_size_kb(data_service.ocel)
            log_step("Set OCEL Parameters", start_time, file_path, config_name,
                     file_size_kb, df_size_kb, ocel_size_kb, ocel_df_sizes)
        except Exception as e:
            log_step("Set OCEL Parameters", start_time, file_path, config_name,
                     file_size_kb, df_size_kb, 0.00, {}, success=False, error_message=str(e))
            pytest.fail(f"Errore nella conversione OCEL: {str(e)}")

        # 🟢 4. Creazione delle relazioni E2O
        start_time = time.time()
        try:
            data_service.set_e2o_relationship_qualifiers(
                {"object_type|activity": "qualifier_value"})
            ocel_size_kb, ocel_df_sizes = get_ocel_size_kb(data_service.ocel)
            log_step("Set E2O Relationships", start_time, file_path, config_name,
                     file_size_kb, df_size_kb, ocel_size_kb, ocel_df_sizes)
        except Exception as e:
            log_step("Set E2O Relationships", start_time, file_path, config_name, file_size_kb,
                     df_size_kb, ocel_size_kb, ocel_df_sizes, success=False, error_message=str(e))
            pytest.fail(
                f"Errore nella creazione delle relazioni E2O: {str(e)}")

        # 🟢 5. Creazione delle relazioni O2O
        start_time = time.time()
        try:
            data_service.o2o_enrichment()
            ocel_size_kb, ocel_df_sizes = get_ocel_size_kb(data_service.ocel)
            assert data_service.ocel_o2o is not None, f"❌ O2O enrichment fallito per {file_path}"
            log_step("Set O2O Relationships", start_time, file_path, config_name,
                     file_size_kb, df_size_kb, ocel_size_kb, ocel_df_sizes)
        except Exception as e:
            log_step("Set O2O Relationships", start_time, file_path, config_name, file_size_kb,
                     df_size_kb, ocel_size_kb, ocel_df_sizes, success=False, error_message=str(e))
            pytest.fail(
                f"Errore nella creazione delle relazioni O2O: {str(e)}")
