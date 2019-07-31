import numpy as np
from trajectoryPlotting import trajPlot
from fileLoading import readCsv
from dateConv import decToDatetime
from metRemoval import metRemove
from scipy import stats
import os
import pandas as pd


def plotratios(hours, ethane=True, all=True, summer=True, viirs=True):
    """
    plotratios is a function that imports either the acetylene/methane ratio or the ethane/methane ratio data and
    plots it, various conditions can be set.

    :param hours: Number of back trajectory hours ran with Hysplit, used for plot titles
    :param ethane: Default True. Set to false for acetylene data.
    :param all: Default True, uses all data. Set to false to cut z scores below 3.
    :param summer: Default True, cuts winter data. Set to false to use only winter data and cut summer data
    :param viirs: Default True, uses viirs fire data. Set to false to use MODIS C6 data

    :return: nothing, displays plot with plt.show()
    """

    # Create titles and set data path depending on options
    dataroot = r'C:\Users\ARL\Desktop\Jashan\Summit\analyses\Data'                     # data directory
    trajroot = r'C:\Users\ARL\Desktop\Jashan\Jashan PySplit\pysplitprocessor-master\pysplitprocessor\messeduptime_notUTC'
    if ethane:
        if all:
            root = os.path.join(trajroot, 'ethane_methane_all')
            title = f'{hours}h Back Trajectories of Ethane/Methane Ratio, 2012-2019'
            sheet = readCsv(dataroot + r'\ethaneRatioNoaa.txt')
        else:
            title = f'{hours}h Back Trajectories of Ethane/Methane Ratio Outliers, 2012-2019'
            sheet = readCsv(dataroot + r'\ethaneRatioNoaa.txt')
    else:
        if all:
            root = r'C:\Users\ARL\Desktop\Jashan\Jashan ' \
                   r'PySplit\pysplitprocessor-master\pysplitprocessor\aceTraj'
            title = f'{hours}h Back Trajectories of Acetylene/Methane Ratio, 2012-2018'
            sheet = readCsv(dataroot + r'\aceRatioNoaa.txt')
        else:
            title = f'{hours}h Back Trajectories of Acetylene/Methane Ratio Outliers, 2012-2019'
            root = r'C:\Users\ARL\Desktop\Jashan ' \
                   r'PySplit\pysplitprocessor-master\pysplitprocessor\ace_methane_traj_highz'
            sheet = readCsv(dataroot + r'\aceRatioNoaa.txt')

    header = ['decyear', 'value', 'function', 'resid', 'residsmooth']           # create header
    sheet.columns = header                                                      # assign column names
    sheet = sheet[sheet['value'] >= 0.000001]                                   # remove zero values

    sheet['datetime'] = decToDatetime(sheet['decyear'].values)                  # create datetimes from decyear
    sheet['datetime'] = sheet['datetime'] + pd.Timedelta('3 hours')             # convert tz to UTC

    dates = sheet['datetime'].tolist()                                          # put datetimes in list
    julian = []                                                                 # preallocate
    for d in dates:                                                             # loop over each date
        tt = d.timetuple()                                                      # create a timetuple from date
        jul = tt.tm_yday                                                        # get the julian year
        julian.append(jul)                                                      # append that to a list
    sheet['julian'] = julian                                                    # add to dataframe

    cutoffs = (120, 305)
    if summer:
        keep = np.logical_and(sheet['julian'] >= cutoffs[0],                    # find just summer values
                              sheet['julian'] <= cutoffs[1])
        print('-- Winter Data Removed')
    else:
        keep = ~(np.logical_and(sheet['julian'] >= cutoffs[0],                  # find just winter values
                                sheet['julian'] <= cutoffs[1]))
        print('-- Summer Data Removed')
    sheet = sheet[keep]

    dropcols = ['decyear', 'function', 'residsmooth']                           # columns to drop
    sheet.drop(dropcols, axis=1, inplace=True)                                  # drop unused columns

    # remove slow data or data above 342, below 72 degrees at Summit camp due to possible pollution
    sheetClean = metRemove(sheet, 1, dropMet=True)

    residuals = sheetClean['resid'].values                                      # numpy array of resid
    z = np.abs(stats.zscore(residuals))                                         # calculate z scores
    sheetClean['zscores'] = z                                                   # assign as column
    if all:
        thresh = 0                                                              # z score threshold
    else:
        thresh = 3
    sheetZ = sheetClean[z > thresh]                                             # remove non outliers
    sheetZ.reset_index(drop=True, inplace=True)

    trajPlot(root, title=title, zscores=sheetZ, viirs=viirs, summer=summer)


if __name__ == '__main__':
    plotratios(72, ethane=False, all=True, viirs=True, summer=True)
