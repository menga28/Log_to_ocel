from run_validation import run_validation
import logging
import json
import os
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

RESULTS_FILE = "validation/results.json"


def main():
    delta = 10
    log_pct_values = [20, 40, 60, 80, 100]
    combinations = []

    # Pre-computiamo tutte le combinazioni valide
    for event_attr_pct in range(0, 91, delta):  # da 0 a 90 inclusi
        object_pct = 100 - event_attr_pct
        for object_attr_pct in range(0, 101, delta):
            for log_pct in log_pct_values:
                combinations.append(
                    (event_attr_pct, object_pct, object_attr_pct, log_pct))

    total = len(combinations)
    start_all = time.perf_counter()

    for idx, (event_attr_pct, object_pct, object_attr_pct, log_pct) in enumerate(combinations, start=1):
        logger.info(
            f"🧪 Test {idx}/{total} | event_attr_pct={event_attr_pct}, object_pct={object_pct}, object_attr_pct={object_attr_pct}, log_pct={log_pct}")

        start = time.perf_counter()
        try:
            run_validation(
                event_attr_pct,
                object_pct,
                object_attr_pct,
                log_pct
            )
        except Exception as e:
            logger.error(
                f"Errore per combinazione {event_attr_pct}-{object_pct}-{object_attr_pct}-{log_pct}: {str(e)}")
        end = time.perf_counter()

        elapsed_test = end - start
        logger.info(f"⏱️ Tempo per questo test: {elapsed_test:.2f}s")

        elapsed_total = end - start_all
        avg_time = elapsed_total / idx
        remaining = avg_time * (total - idx)

        logger.info(
            f"Completati {idx}/{total} - Tempo stimato rimanente: {remaining:.2f}s ({remaining/60:.1f} min)")


if __name__ == "__main__":
    main()

