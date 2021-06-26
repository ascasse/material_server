'''
    Initialize log.
'''
import logging
import logging.config as loggingconfig
import logging.handlers
from pathlib import Path

log_file_path = Path(__file__).parent.joinpath('logger.conf')
loggingconfig.fileConfig(log_file_path)

logger = logging.getLogger('learning')
