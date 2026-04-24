#!/usr/bin/env python3

import sys  # noqa F401
import os
import logging
import importlib  # noqa F401

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lf_sublogg2 = importlib.import_module("py-scripts.lf_sublogg2")


logger = logging.getLogger(__name__)


def sublogg():
    logger.debug("A DEBUG message from " + __name__)
    logger.info("An INFO message from " + __name__)
    logger.warning("An WARNING message from " + __name__)
    logger.error("An ERROR message from + " + __name__)
    logger.critical("An CRITICAL message from + " + __name__)
    lf_sublogg2.sublogg()
    logger.error("An ERROR message from + " + __name__)
    lf_sublogg2.sublogg2a()
