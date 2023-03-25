'''
    Initialize log.
'''
import logging
import logging.config as loggingconfig
import logging.handlers
from pathlib import Path

def init_log():
    ''' Initialize log'''
    log_file_path = Path(__file__).parent.joinpath('logger.conf')
    loggingconfig.fileConfig(log_file_path)

    return logging.getLogger('learning')

logger = init_log()
