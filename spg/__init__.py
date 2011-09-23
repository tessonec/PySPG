version_number = '3.0.2'
release_date = '23 Sep 2011'

from base.iterator import *
from base.parser   import *


import os.path

ROOT_DIR = os.path.expanduser("~/opt")
CONFIG_DIR = os.path.expanduser(ROOT_DIR+"/etc")
VAR_PATH = os.path.abspath(ROOT_DIR+"/var/spg")
BINARY_PATH = os.path.abspath(ROOT_DIR+"/bin")
RUN_DIR = os.path.expanduser("~/run")

TIMEOUT = 120


