import asyncio
import sys

from motor import motor_asyncio
from odmantic import AIOEngine
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from Bestie_Robot.utils.logger import log
from Bestie_Robot.conf import get_int_key, get_str_key

MONGO_DB_URI = get_str_key("MONGO_DB_URI")
MONGO_PORT = get_int_key("MONGO_PORT")
MONGO_DB = get_str_key("MONGO_DB")

# Init MongoDB
mongodb = MongoClient(MONGO_DB_URI, MONGO_PORT)[MONGO_DB]
motor = motor_asyncio.AsyncIOMotorClient(MONGO_DB_URI, MONGO_PORT)
db = motor[MONGO_DB]

engine = AIOEngine(motor, MONGO_DB)

try:
    asyncio.get_event_loop().run_until_complete(motor.server_info())
except ServerSelectionTimeoutError:
    sys.exit(log.critical("[BESTIE ERROR] Can't Connect To Mongodb! Exiting..."))
