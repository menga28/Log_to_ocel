import logging
import os
import glob


def setup_logger(name, log_file, level=logging.INFO):
    """Configura un logger per salvare i risultati dei test su file CSV, prevenendo duplicati."""

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Rimuove gli handler solo se ce ne sono, evitando l'errore
    if logger.hasHandlers():
        # Copia la lista per evitare problemi durante la modifica
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # Evita di aggiungere duplicati
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(log_file) for h in logger.handlers):
        handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s,%(levelname)s,%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_all_files(directory, extensions=[".json", ".csv"]):
    """Restituisce una lista di tutti i file con le estensioni specificate nella cartella."""
    files = glob.glob(os.path.join(directory, "**/*"), recursive=True)
    return [f for f in files if f.endswith(tuple(extensions))]
