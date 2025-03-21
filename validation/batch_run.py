import concurrent.futures
from run_validation import run_validation
import logging
import json
import os
import time

# Setup logging (livello essenziale)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(filename)s - %(message)s"
)
logger = logging.getLogger(__name__)

def run_single_test(idx, total, event_attr_pct, object_pct, object_attr_pct, log_pct):
    logger.info(f"Test {idx}/{total} started")
    start = time.perf_counter()
    try:
        run_validation(event_attr_pct, object_pct, object_attr_pct, log_pct)
        status = "SUCCESS"
    except Exception as e:
        logger.error(f"Error in test {idx}: {str(e)}")
        status = "ERROR"
    elapsed = time.perf_counter() - start
    logger.info(f"Test {idx} finished in {elapsed:.2f} seconds")
    return (idx, elapsed, status)

def main():
    delta = 10
    log_pct_values = [20, 40, 60, 80, 100]
    combinations = []

    # Pre-calcolo di tutte le combinazioni valide
    for event_attr_pct in range(0, 101, delta):
        object_pct = 100 - event_attr_pct
        for object_attr_pct in range(0, 101, delta):
            for log_pct in log_pct_values:
                combinations.append((event_attr_pct, object_pct, object_attr_pct, log_pct))

    total = len(combinations)
    start_all = time.perf_counter()

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for idx, (event_attr_pct, object_pct, object_attr_pct, log_pct) in enumerate(combinations, start=1):
            futures.append(executor.submit(run_single_test, idx, total, event_attr_pct, object_pct, object_attr_pct, log_pct))
        
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    total_time = time.perf_counter() - start_all
    logger.info(f"All tests completed in {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
