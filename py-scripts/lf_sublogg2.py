#!/usr/bin/env python3

import logging

logger = logging.getLogger(__name__)


def sublogg():
    logger.debug("A DEBUG message from " + __name__)
    logger.info("An INFO message from " + __name__)
    logger.warning("An WARNING message from " + __name__)
    logger.error("An ERROR message from + " + __name__)
    logger.critical("An CRITICAL message from + " + __name__)


def sublogg2a():
    logger.debug("A DEBUG message from " + __name__)
    logger.info("An INFO message from " + __name__)
    logger.warning("An WARNING message from " + __name__)
    logger.error("An ERROR message from + " + __name__)
    logger.critical("An CRITICAL message from + " + __name__)
