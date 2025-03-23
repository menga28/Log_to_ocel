import pytest
import time
import os
import pandas as pd
from tests.unit.utils import setup_logger
from app.services.data_service import DataService

logger = setup_logger("test_results", "validation/logs/test_results.csv")


@pytest.fixture
def data_service():
    return DataService()


def get_all_files(directory, extensions=[".json", ".csv"]):
    """Restituisce una lista di tutti i file con le estensioni specificate nella cartella."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files


def log_step(step_name, start_time, file_path, success=True, error_message=None):
    """Registra il passaggio nel file CSV con tempo e stato."""
    elapsed_time = time.time() - start_time
    status = "PASS" if success else "FAIL"
    message = error_message if error_message else "OK"

    log_entry = f"{file_path},{step_name},{status},{elapsed_time:.4f},{message}"
    logger.info(log_entry)


@pytest.mark.parametrize("file_path", list(set(get_all_files("tests/input_data/"))))
def test_load_files(data_service, file_path):
    """Test per caricare tutti i file di input (JSON/CSV) e verificarne la validità."""
    start_time = time.time()
    df = data_service.load_dataframe(file_path)

    assert df is not None, f"Errore nel caricamento del file {file_path}"
    assert isinstance(
        df, pd.DataFrame), f"Il file {file_path} non è un DataFrame"

    log_step("Load DataFrame", start_time, file_path)


@pytest.mark.parametrize("file_path", list(set(get_all_files("tests/input_data/"))))
def test_normalization(data_service, file_path):
    """Test per verificare la normalizzazione delle colonne nidificate nei file JSON."""
    start_time = time.time()
    data_service.load_dataframe(file_path)
    nested_columns = data_service.nested_keys()

    if nested_columns:
        normalized_df = data_service.normalize_data(
            [0])  # Normalizza la prima colonna nidificata
        assert normalized_df is not None, f"Normalizzazione fallita per {file_path}"
        assert isinstance(
            normalized_df, pd.DataFrame), f"Normalizzazione non riuscita per {file_path}"
        log_step("Normalize Data", start_time, file_path)
    else:
        logger.warning(
            f"test_normalization: SKIPPED ({file_path}, nessuna colonna nidificata)")
