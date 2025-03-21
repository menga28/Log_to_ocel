from run_validation import run_validation
import logging
import json
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

RESULTS_FILE = "validation/results.json"


def main():
    delta = 10
    for event_attr_pct in range(0, 101, delta):
        object_pct = 100 - event_attr_pct
        for object_attr_pct in range(0, 101, delta):
            for log_pct in [10, 50, 10]:
                logger.info(
                    f"🧪 Test: event_attr_pct={event_attr_pct}, object_pct={object_pct}, object_attr_pct={object_attr_pct}, log_pct={log_pct}")
                try:
                    run_validation(
                        event_attr_pct,
                        object_pct,
                        object_attr_pct,
                        log_pct
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Errore per combinazione {event_attr_pct}-{object_pct}-{object_attr_pct}-{log_pct}: {str(e)}")


if __name__ == "__main__":
    main()
