import logging

def setup_logger():
    # Create a custom logger
    logger = logging.getLogger("AIsql_analytics_agent")
    
    # Check if handlers are already configured to avoid duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create handlers
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        
        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        
        # Add handlers to the logger
        logger.addHandler(c_handler)
        
    return logger

logger = setup_logger()

def log_warning(exc: Exception, context: str = ""):
    logger.warning(f"Warning in {context}: {str(exc)}")

def log_error(exc: Exception, context: str = ""):
    logger.error(f"Error in {context}: {str(exc)}")
