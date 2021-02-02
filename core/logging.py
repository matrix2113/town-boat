import math
import os

from datetime import datetime

from core.vylogger import VyLogger

logger = VyLogger("default")


def capitalize(string):
    return string[0].upper() + string[1:]


def strToDate(stringDate: str) -> datetime:
    return datetime.strptime(stringDate, '%m/%d/%Y %H:%M:%S')


def dateToStr(date: datetime) -> str:
    return datetime.strftime(date, '%m/%d/%Y %H:%M:%S')


def halve_string(s):
    middle = math.floor(len(s) / 2)
    before = s.rfind(" ", middle)
    after = s.rfind(" ", middle + 1)

    if (middle - before) < (after - middle):
        middle = after
    else:
        middle = before

    return {
        "first": s[0:middle],
        "second": s[middle + 1:]
    }


def log_message(level, shard, sender, source, msg):
    message = f"{dateToStr(date=datetime.utcnow())} [shard {str(shard)}] <{sender}@{source}> {msg}"

    if level == "warn":
        logger.warning(message)
    elif level == "err":
        logger.error(message)
    elif level == "info":
        logger.info(message)
    elif level == "debug":
        logger.debug(message)