import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)
        
    # Console Handler
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    # File Handler
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler("app.log", maxBytes=5*1024*1024, backupCount=3) # 5MB per file, 3 backups
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.ERROR)
    
    # Set level for specific loggers if needed
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False # Prevent access logs from propagating
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("uvicorn.error").propagate = True
