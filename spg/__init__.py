
import os.path

version_number = '2.9.9'
release_date = '09 Ago 2011'

from base.iterator import *
from base.parser   import *

ROOT_DIR = os.path.expanduser("~/opt")
CONFIG_DIR = os.path.expanduser(ROOT_DIR+"/etc")
VAR_PATH = os.path.abspath(ROOT_DIR+"/var/spg")
BINARY_PATH = os.path.abspath(ROOT_DIR+"/bin")

TIMEOUT = 120
