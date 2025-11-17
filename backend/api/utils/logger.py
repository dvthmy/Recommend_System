import logging


logger = logging.getLogger("food-api")
if not logger.handlers:
    handler = logging.StreamHandler()
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s in %(name)s: %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)