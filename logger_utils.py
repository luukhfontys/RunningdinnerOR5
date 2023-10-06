import logging
import time

logger = logging.getLogger(name='2opt-logger')

def configure_logger():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(message)s',
                        handlers=[logging.FileHandler(f'2-opt_debug{time.time()}.log')])

configure_logger()