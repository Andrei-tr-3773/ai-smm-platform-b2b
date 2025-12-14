import logging
import sys

from dotenv import load_dotenv, find_dotenv

print("Setup logger...")
logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO
)

logging.info("Init common module...")
load_dotenv(find_dotenv(), override=True)
