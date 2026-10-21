import logging
import sys

LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"


def get_logger(module_name: str) -> logging.Logger:
    """
    Instantiates and configures a standardized logger instance.
    """
    logger = logging.getLogger(module_name)
    
    # set the threshold level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.INFO)
    
    # avoid duplicate logs if parent handlers are already active
    logger.propagate = False
    
    # prevent adding redundant handlers if get_logger is called multiple times
    if not logger.handlers:
        # direct logs to stdout (Standard Output) for cloud/container monitoring
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # apply the structured format blueprint
        formatter = logging.Formatter(LOG_FORMAT)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    return logger


# instantiate the logger using the current module context
logger = get_logger(__name__)
