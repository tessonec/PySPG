version_number   = '4.0.1'
database_version = '2.0'
release_date = '04 Jul 2016'

from base.iterator import *
from base.parser   import *


import os.path

#SPG_HOME = os.path.expanduser("~/opt/lib")


ROOT_DIR = os.path.expanduser("~/opt")

CONFIG_DIR = os.path.expanduser("~/.pyspg")
VAR_PATH = os.path.abspath(CONFIG_DIR+"/spool")
BINARY_PATH = os.path.abspath(ROOT_DIR+"/bin")
# RUN_DIR = os.path.expanduser("~/run")

TIMEOUT = 120


