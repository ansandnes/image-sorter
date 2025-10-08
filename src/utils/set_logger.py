from pathlib import Path
import logging

def set_logger(name:str, logfilename:str, log_path:str, mode:str):
    """
        Set a logger to log messages to a file

        Parameters
        ----------
        name : str
            Name of the logger

        logfilename : str
            Name of the log file

        log_path : str
            Path to the log file

        mode : str
            Mode to open the log file
        
        Returns
        -------
        logger : logging.Logger
            Configured logger
    """

    # Make sure the log directory exist
    log_path = f"{log_path}/logs/{logfilename}"  # Add /logs to the log path to create the log directory
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)  # Creates parent directories if they don't exist

    # Define logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Safely clear existing handlers
    if logger.hasHandlers():
        for handler in logger.handlers:
            handler.close()
        logger.handlers.clear()
    
    # Define filehandler
    handler = logging.FileHandler(f"{log_path}", mode=mode)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger