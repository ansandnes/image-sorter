from pathlib import Path
import logging

def set_logger(
    name: str,
    logfilename: str,
    log_path: str,
    mode: str,
    level: int = logging.INFO,
):
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

    # Make sure the log directory exists.
    logfile_path = Path(log_path) / "logs" / logfilename
    logfile_path.parent.mkdir(parents=True, exist_ok=True)

    # Define logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Reuse existing file handler for this logfile when available.
    for existing_handler in logger.handlers:
        if isinstance(existing_handler, logging.FileHandler):
            if Path(existing_handler.baseFilename) == logfile_path:
                existing_handler.setLevel(level)
                return logger

    # Define filehandler
    handler = logging.FileHandler(logfile_path, mode=mode)
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)
    logger.propagate = False

    return logger