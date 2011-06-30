from parameter import ParameterExtractor, ParameterDB, ParameterExecutor

from process import ProcessPool

from exchange import DataExchanger

from data import DataAtom, DataAtomExecutor


import os.path
from spg.params import CONFIG_DIR

VAR_PATH = os.path.abspath(CONFIG_DIR+"/../var/spg")

