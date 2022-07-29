""" Logger settings """

import logging

Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename="archtabs_log.log",
                    filemode="w",
                    format=Log_Format,
                    level=logging.ERROR)
log = logging.getLogger()
