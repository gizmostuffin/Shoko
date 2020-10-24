import logging
import time
import os
import sys
import spamwatch
from telethon import TelegramClient
from redis import StrictRedis
import telegram.ext as tg


# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

LOGGER = logging.getLogger(__name__)

LOGGER.info("Starting Shoko...")

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    )
    quit(1)


from Shoko.config import Development as Config

TOKEN = Config.BOT_TOKEN
try:
    OWNER_ID = int(Config.OWNER_ID)
except ValueError:
    raise Exception("Your OWNER_ID variable is not a valid integer.")

    
OWNER_USERNAME = Config.OWNER_USERNAME

try:
    SUDO_USERS = set(int(x) for x in Config.SUDO_USERS or [])
except ValueError:
    raise Exception("Your sudo users list does not contain valid integers.")

try:
    SUPPORT_USERS = set(int(x) for x in Config.SUPPORT_USERS or [])
except ValueError:
    raise Exception("Your support users list does not contain valid integers.")

try:
    WHITELIST_USERS = set(int(x) for x in Config.WHITELIST_USERS or [])
except ValueError:
    raise Exception("Your whitelisted users list does not contain valid integers.")
try:
    WHITELIST_CHATS = set(int(x) for x in Config.WHITELIST_CHATS or [])
except ValueError:
    raise Exception("Your whitelisted users list does not contain valid integers.")
try:
    BLACKLIST_CHATS = set(int(x) for x in Config.BLACKLIST_CHATS or [])
except ValueError:
    raise Exception("Your whitelisted users list does not contain valid integers.")

WEBHOOK = Config.WEBHOOK
URL = Config.URL
PORT = Config.PORT
CERT_PATH = Config.CERT_PATH

MESSAGE_DUMP = Config.MESSAGE_DUMP
GBAN_DUMP = Config.GBAN_DUMP
ERROR_DUMP = Config.ERROR_DUMP
DB_URI = Config.SQLALCHEMY_DATABASE_URI
LOAD = Config.LOAD
NO_LOAD = Config.NO_LOAD
DEL_CMDS = Config.DEL_CMDS
STRICT_GBAN = Config.STRICT_GBAN
WORKERS = Config.WORKERS
CUSTOM_CMD = Config.CUSTOM_CMD
API_WEATHER = Config.API_OPENWEATHER
TELETHON_HASH = Config.TELETHON_HASH
TELETHON_ID = Config.TELETHON_ID
SPAMWATCH = Config.SPAMWATCH_API

SUDO_USERS.add(OWNER_ID)

# Pass if SpamWatch token not set.
if SPAMWATCH == None:
    spamwtc = None
    LOGGER.warning("Invalid spamwatch api")
else:
    spamwtc = spamwatch.Client(SPAMWATCH)

REDIS_URL = Config.REDIS_URI
REDIS = StrictRedis.from_url(REDIS_URL,decode_responses=True)

try:
    REDIS.ping()
    LOGGER.info("Your redis server is now alive!")
    
except BaseException:
    raise Exception("Your redis server is not alive, please check again.")

 
# Telethon
api_id = TELETHON_ID
api_hash = TELETHON_HASH
client = TelegramClient("Shoko", api_id, api_hash)

updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)

dispatcher = updater.dispatcher

# init time
since_time_start = time.time()
SUDO_USERS = list(SUDO_USERS)
WHITELIST_USERS = list(WHITELIST_USERS)
SUPPORT_USERS = list(SUPPORT_USERS)

# Load at end to ensure all prev variables have been set
from Shoko.modules.helper_funcs.handlers import CustomCommandHandler

if CUSTOM_CMD and len(CUSTOM_CMD) >= 1:
    tg.CommandHandler = CustomCommandHandler
