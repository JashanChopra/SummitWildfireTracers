# Importing Libraries
import pandas as pd
import numpy as np
from dateConv import createDatetime


def metTrim():
    """
    This function imports met data and trims it for further usage
    :return: met data
    """
    # ---- initial reading of data
    root = r'C:\Users\ARL\Desktop\Jashan\MetData'
    ext = list(range(12, 20))                                                           # yearly extensions

    colnames = ['na', 'yr', 'mo', 'dy', 'hr', 'dir', 'spd', 'steady', 'na', 'na', 'na', 'na', 'na', 'na']
    met = pd.DataFrame(columns=colnames)                                                # preallocate df
    for yr in ext:
        # read in data
        data = pd.read_csv(root + r'\met_sum_insitu_1_obop_hour_20{}.txt'.format(yr), delim_whitespace=True,
                           header=None)
        data.columns = colnames                                                         # apply col names
        met = met.append(data)                                                          # append to list
    print('Data Imported')

    # ---- trimming data
    met = met.drop('na', axis=1)                                                        # drop na cols
    met = met.replace(-999.9, np.nan)                                                   # turn missing val to nan
    met = met.replace(-9, np.nan)
    met = met.replace(-999, np.nan)
    met = met.replace(-99.9, np.nan)
    met = met.dropna(axis=0, how='any')                                                 # remove rows with nan vals

    # ---- convert date to datetime
    metInt = met.applymap(int)                                                          # make sure values are ints
    dates = createDatetime(metInt['yr'].values,
                           metInt['mo'].values,
                           metInt['dy'].values,
                           metInt['hr'].values)

    met['datetime'] = dates                                                             # add it as a new column
    met = met.drop(['yr', 'mo', 'dy', 'hr'], axis=1)                                    # drop old date columns

    return met


if __name__ == '__main__':
    metTrim()



