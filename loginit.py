'''
    Initialize log.
'''
import logging
import logging.handlers
from pathlib import Path

log_file_path = Path(__file__).parent.joinpath('logger.conf')
logging.config.fileConfig(log_file_path)
