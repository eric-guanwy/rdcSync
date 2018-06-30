#!/usr/bin/evn python
# -*- coding: utf-8 -*-
import logging
import logging.handlers

LOG_LEVEL = logging.INFO

logging.basicConfig(level=LOG_LEVEL,
                    format='[%(asctime)s] %(filename)s %(threadName)s %(levelname)s %(message)s',
                    # filename='xmltxttransformer.log',
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(LOG_LEVEL)
formatter = logging.Formatter('[%(asctime)s] %(filename)s %(threadName)s [%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

filehandler = logging.handlers.TimedRotatingFileHandler("rdcsync.log", when='D', interval=1, backupCount=3)
filehandler.setLevel(LOG_LEVEL)
filehandler.setFormatter(formatter)
filehandler.suffix = "%Y-%m-%d.log"
logging.getLogger('').addHandler(filehandler)