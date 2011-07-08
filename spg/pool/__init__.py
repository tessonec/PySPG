from ensemble import ParameterEnsemble, WeightedParameterEnsemble, ParameterEnsembleExecutor

from process import ProcessPool

from exchange import DataExchanger

from atom import ParameterAtom, ParameterAtomExecutor


import os.path
from spg.params import CONFIG_DIR

VAR_PATH = os.path.abspath(CONFIG_DIR+"/../var/spg")
BINARY_PATH = os.path.abspath(CONFIG_DIR+"/../bin")
