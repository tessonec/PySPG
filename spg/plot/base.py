'''
Created on 12 Apr 2014

@author: tessonec
'''




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
                minimal_df = self.data.loc[minimal_idx]

                yield minimal_df

        else:
            yield self.data


