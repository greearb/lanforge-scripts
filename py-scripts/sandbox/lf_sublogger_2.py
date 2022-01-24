#!/usr/bin/env python3
import sys
import logging
import importlib

logger = logging.getLogger(__name__)

def sublogger():
    logger.debug("A DEBUG message from " + __name__)
    logger.info("An INFO message from " + __name__)
    logger.warning("An WARNING message from " + __name__)
    logger.error("An ERROR message from + " + __name__)
    logger.critical("An CRITICAL message from + " + __name__)


def sublogger_2a():
    logger.debug("A DEBUG message from " + __name__)
    logger.info("An INFO message from " + __name__)
    logger.warning("An WARNING message from " + __name__)
    logger.error("An ERROR message from + " + __name__)
    logger.critical("An CRITICAL message from + " + __name__)
