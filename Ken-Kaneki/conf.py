import os
import sys

import yaml
from envparse import env

from Bestie_Robot.utils.logger import log

DEFAULTS = {
    "LOAD_MODULES": True,
    "DEBUG_MODE": True,
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_DB_FSM": 1,
    "MONGODB_URI": "localhost",
    "MONGO_DB": "AllMight",
    "API_PORT": 8080,
    "JOIN_CONFIRM_DURATION": "30m",
}

CONF_PATH = "data/bot_conf.yaml"
if os.name == "nt":
    log.debug("Detected Windows, changing config path...")
    CONF_PATH = os.getcwd() + "\\data\\bot_conf.yaml"

if os.path.isfile(CONF_PATH):
    log.info(CONF_PATH)
    for item in (
        data := yaml.load(open("data/bot_conf.yaml", "r"), Loader=yaml.CLoader)
    ):
        DEFAULTS[item.upper()] = data[item]
else:
    log.info("Using env vars")


def get_str_key(name, required=False):
    if name in DEFAULTS:
        default = DEFAULTS[name]
    else:
        default = None
    if not (data := env.str(name, default=default)) and not required:
        log.warning("No str key: " + name)
        return None
    elif not data:
        log.critical("No str key: " + name)
        exit(2)
    else:
        return data


def get_int_key(name, required=False):
    if name in DEFAULTS:
        default = DEFAULTS[name]
    else:
        default = None
    if not (data := env.int(name, default=default)) and not required:
        log.warning("No int key: " + name)
        return None
    elif not data:
        log.critical("No int key: " + name)
        exit(2)
    else:
        return data


def get_list_key(name, required=False):
    if name in DEFAULTS:
        default = DEFAULTS[name]
    else:
        default = None
    if not (data := env.list(name, default=default)) and not required:
        log.warning("No list key: " + name)
        return []
    elif not data:
        log.critical("No list key: " + name)
        exit(2)
    else:
        return data


def get_bool_key(name, required=False):
    if name in DEFAULTS:
        default = DEFAULTS[name]
    else:
        default = None
    if not (data := env.bool(name, default=default)) and not required:
        log.warning("No bool key: " + name)
        return False
    elif not data:
        log.critical("No bool key: " + name)
        exit(2)
    else:
        return data
