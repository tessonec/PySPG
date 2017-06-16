'''
Created on 12 Apr 2014

@author: tessonec
'''

import pandas as pd
import numpy as np


import matplotlib as mpl
#  Useful but not here
mpl.use('Agg')
import matplotlib.pylab as plt
import matplotlib.lines as mlines


import matplotlib.backends.backend_pdf as mpl_b_pdf
import itertools


class DataFrameIterator:

    def __init__(self, df, filter = [] ):
        self.data = df
        self.filter = filter

    def __iter__(self):
#        print self.filter
        if len(self.filter) > 0:
            df_coalesced = self.data.groupby(self.filter)

            for minimal_gr in sorted(df_coalesced.groups):
                minimal_idx = df_coalesced.groups[minimal_gr]
                minimal_df = self.data.ix[minimal_idx]

                yield minimal_df

        else:
            yield self.data


