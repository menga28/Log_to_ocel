import pytest
import sys
import os
from validation.tests.utils import setup_logger
from app.services.data_service import DataService
from validation.tests.utils import get_all_files
from validation.tests.config import test_configs, p_activity, p_timestamp

logger = setup_logger("test_results", "validation/logs/test_results.csv")


@pytest.fixture
def data_service():
    return DataService()


@pytest.mark.parametrize("config", test_configs)
def test_ocel_conversion(data_service, config):
    """Test per la conversione in OCEL con diverse configurazioni"""
    file_path = "validation/input_data/pancacke100txs.json"
    data_service.load_dataframe(file_path)
    data_service.normalize_data([0])

    try:
        data_service.set_ocel_parameters(
            activity=p_activity,
            timestamp=p_timestamp,
            object_types=config["p_object_types"],
            events_attrs=config["p_additional_event_attributes"],
            object_attrs=config["p_additional_object_attributes"]
        )
        assert data_service.ocel is not None, f"❌ OCEL non creato con configurazione: {config['name']}"
        logger.info(f"✅ test_ocel_conversion: PASS ({config['name']})")
    except Exception as e:
        logger.error(f"❌ test_ocel_conversion: FAIL ({config['name']}, {str(e)})")
        pytest.fail(f"Configurazione '{config['name']}' fallita: {str(e)}")