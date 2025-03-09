import pytest
import time
from validation.tests.utils import get_all_files, setup_logger
from validation.tests.config import test_configs, p_activity, p_timestamp
from app.services.data_service import DataService

# 📌 Configura il logger per salvare i log in un file CSV
logger = setup_logger("test_results", "validation/logs/test_results.csv")

@pytest.fixture(scope="module")
def data_service():
    """Utilizza una sola istanza di DataService per tutti i test del modulo."""
    global_data_service = DataService()
    return global_data_service

def log_step(step_name, start_time, file_path, config_name, success=True, error_message=None):
    """Registra un passo nel file CSV con il tempo impiegato e il set di parametri usato."""
    elapsed_time = time.time() - start_time
    status = "PASS" if success else "FAIL"
    message = error_message if error_message else "OK"
    logger.info(f"{file_path},{config_name},{step_name},{status},{elapsed_time:.4f},{message}")

@pytest.mark.parametrize("file_path", get_all_files("validation/input_data/"))
def test_ocel_processing(data_service, file_path):
    """Test completo per OCEL processing su tutti i file di input, usando tutte le configurazioni"""

    for config in test_configs:  # 🔁 Ciclo su tutte le configurazioni
        config_name = config["name"]
        logger.info(f"⚙️ DEBUG: Test con configurazione {config_name}")

        # 🟢 1. Caricamento del file
        start_time = time.time()
        data_service.load_dataframe(file_path)
        log_step("Load DataFrame", start_time, file_path, config_name)

        # 🟢 2. Normalizzazione
        start_time = time.time()
        data_service.normalize_data([0])
        log_step("Normalize Data", start_time, file_path, config_name)

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
            log_step("Set OCEL Parameters", start_time, file_path, config_name)
        except Exception as e:
            log_step("Set OCEL Parameters", start_time, file_path, config_name, success=False, error_message=str(e))
            pytest.fail(f"Errore nella conversione OCEL: {str(e)}")

        # 🟢 4. Creazione delle relazioni E2O
        start_time = time.time()
        try:
            data_service.set_e2o_relationship_qualifiers({"object_type|activity": "qualifier_value"})
            log_step("Set E2O Relationships", start_time, file_path, config_name)
        except Exception as e:
            log_step("Set E2O Relationships", start_time, file_path, config_name, success=False, error_message=str(e))
            pytest.fail(f"Errore nella creazione delle relazioni E2O: {str(e)}")

        # 🟢 5. Creazione delle relazioni O2O
        start_time = time.time()
        try:
            data_service.o2o_enrichment()
            assert data_service.ocel_o2o is not None, f"❌ O2O enrichment fallito per {file_path}"
            log_step("Set O2O Relationships", start_time, file_path, config_name)
        except Exception as e:
            log_step("Set O2O Relationships", start_time, file_path, config_name, success=False, error_message=str(e))
            pytest.fail(f"Errore nella creazione delle relazioni O2O: {str(e)}")
