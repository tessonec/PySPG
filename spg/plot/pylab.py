import numpy as np
import math as m
from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.pylab as plb


class PyplotWrapper:
    def __init__(self):
        rc('text', usetex=True)
        rc('font', family='serif')

        self.fig = plt.figure()
        