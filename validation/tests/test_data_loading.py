import pytest
import os
import pandas as pd
from validation.tests.utils import setup_logger
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

@pytest.mark.parametrize("file_path", get_all_files("validation/input_data/"))
def test_load_files(data_service, file_path):
    """Test per caricare tutti i file di input (JSON/CSV) e verificarne la validità"""
    df = data_service.load_dataframe(file_path)
    assert df is not None, f"❌ Errore nel caricamento del file {file_path}"
    assert isinstance(df, pd.DataFrame), f"❌ Il file {file_path} non è un DataFrame"
    logger.info(f"✅ test_load_files: PASS ({file_path}, {len(df)} righe)")

@pytest.mark.parametrize("file_path", get_all_files("validation/input_data/"))
def test_normalization(data_service, file_path):
    """Test per verificare la normalizzazione delle colonne nidificate nei file JSON"""
    data_service.load_dataframe(file_path)
    nested_columns = data_service.nested_keys()
    if nested_columns:
        normalized_df = data_service.normalize_data([0])  # Normalizza la prima colonna nidificata
        assert normalized_df is not None, f"❌ Normalizzazione fallita per {file_path}"
        assert isinstance(normalized_df, pd.DataFrame), f"❌ Normalizzazione non riuscita per {file_path}"
        logger.info(f"✅ test_normalization: PASS ({file_path}, {len(normalized_df)} righe)")
    else:
        logger.warning(f"⚠️ test_normalization: SKIPPED ({file_path}, nessuna colonna nidificata)")