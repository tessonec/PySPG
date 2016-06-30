version_number   = '3.2.4'
database_version = '1.1'
release_date = '15 Feb 2013'

from base.iterator import *
from base.parser   import *


import os.path

#SPG_HOME = os.path.expanduser("~/opt/lib")


ROOT_DIR = os.path.expanduser("~/opt")

CONFIG_DIR = os.path.expanduser("~/.pyspg")
#VAR_PATH = os.path.abspath(ROOT_DIR+"/var")
BINARY_PATH = os.path.abspath(ROOT_DIR+"/bin")
# RUN_DIR = os.path.expanduser("~/run")

TIMEOUT = 120


