import logging

logger = logging.getLogger(name='2opt-logger')

def configure_logger():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(message)s',
                        handlers=[logging.FileHandler("2-opt_debug202306101757.log")])

configure_logger()