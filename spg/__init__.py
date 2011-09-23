version_number = '3.0.1'
release_date = '24 Ago 2011'

from base.iterator import *
from base.parser   import *

from utils import get_root_directory

import os.path
ROOT_DIR = get_root_directory()
CONFIG_DIR = os.path.expanduser(ROOT_DIR+"/etc")
VAR_PATH = os.path.abspath(ROOT_DIR+"/var/spg")
BINARY_PATH = os.path.abspath(ROOT_DIR+"/bin")
RUN_DIR = os.path.expanduser("~/run")

TIMEOUT = 120


