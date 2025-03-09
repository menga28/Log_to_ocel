import pytest
import time
from validation.tests.utils import setup_logger
from app.services.data_service import DataService
from validation.tests.config import test_configs, p_activity, p_timestamp

logger = setup_logger("test_results", "validation/logs/test_results.csv")


@pytest.fixture
def data_service():
    return DataService()


def log_step(step_name, start_time, config_name, success=True, error_message=None):
    """Registra il passaggio nel file CSV con tempo e configurazione usata."""
    elapsed_time = time.time() - start_time
    status = "PASS" if success else "FAIL"
    message = error_message if error_message else "OK"
    
    log_entry = f"{config_name},{step_name},{status},{elapsed_time:.4f},{message}"
    logger.info(log_entry)


@pytest.mark.parametrize("config", test_configs)
def test_ocel_conversion(data_service, config):
    """Test per la conversione in OCEL con diverse configurazioni."""
    file_path = "validation/input_data/pancacke100txs.json"

    # 🟢 1. Caricamento del file
    start_time = time.time()
    data_service.load_dataframe(file_path)
    log_step("Load DataFrame", start_time, config["name"])

    # 🟢 2. Normalizzazione
    start_time = time.time()
    data_service.normalize_data([0])
    log_step("Normalize Data", start_time, config["name"])

    # 🟢 3. Conversione in OCEL
    start_time = time.time()
    try:
        data_service.set_ocel_parameters(
            activity=p_activity,
            timestamp=p_timestamp,
            object_types=config["p_object_types"],
            events_attrs=config["p_additional_event_attributes"],
            object_attrs=config["p_additional_object_attributes"]
        )
        assert data_service.ocel is not None, f"❌ OCEL non creato con configurazione: {config['name']}"
        log_step("Set OCEL Parameters", start_time, config["name"])
    except Exception as e:
        log_step("Set OCEL Parameters", start_time, config["name"], success=False, error_message=str(e))
        pytest.fail(f"Configurazione '{config['name']}' fallita: {str(e)}")
