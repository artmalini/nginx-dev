from datetime import datetime, timedelta
import logging
import os

ENABLE_TESTING = False
ENABLE_LOGGING = True

#setup the logger
try:
   os.makedirs("{path}/logs/{date}".format(path=os.path.dirname(os.path.abspath(__file__)),date=datetime.today().strftime('%Y-%m-%d')))
except FileExistsError:
   # directory already exists
   pass

try:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)-5.5s] %(message)s",
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler("{path}/logs/{date}/{fname}.log".format(path=os.path.dirname(os.path.abspath(__file__)), date=datetime.today().strftime('%Y-%m-%d'), fname="logs")),
            logging.StreamHandler()
        ])
    logger = logging.getLogger()
    if ENABLE_LOGGING == True :
        logger.setLevel(logging.INFO)  # Set the logger's level to All
    if ENABLE_LOGGING == False :
        logger.setLevel(logging.WARNING)  # Set the logger's level to WARNING
except:
    pass