"""
General functions used for fire tracing with the NASA VIIRS data
"""
import pandas as pd
import numpy as np

def fireData(viirs=True, summer=True):
    """
    Imports fire data and trims for use in trajectory plotting

    :param viirs: Default True condition, uses the VIIRS Data
    :return:
    """
    # import fire data
    viirs = True
    root = r'C:\Users\ARL\Desktop\Jashan\Data\FireData'
    if viirs:
        fire = pd.read_csv(root + r'\fire_archive_V1_60939.csv')
    else:
        fire = pd.read_csv(root + r'\fire_archive_M6_60938.csv')

    if viirs:
        # only keep high tolerance values for viirs
        cond = fire['confidence'] == 'h'
        fire = fire[cond]
        fire.reset_index(drop=True, inplace=True)
    else:
        # only keep high tolerance values for MODIS
        cond = fire['confidence'] > 70
        fire = fire[cond]
        fire.reset_index(drop=True, inplace=True)

    fire = firedt(fire)

    # winter/summer fire removal
    dates = fire['datetime'].tolist()                       # put datetimes in list
    julian = []                                             # preallocate
    for d in dates:                                         # loop over each date
        tt = d.timetuple()                                  # create a timetuple from date
        jul = tt.tm_yday                                    # get the julian year
        julian.append(jul)                                  # append that to a list
    fire['julian'] = julian                                 # add to dataframe

    cutoffs = (120, 305)
    if summer:
        keep = np.logical_and(fire['julian'] >= cutoffs[0],  # find just summer values
                              fire['julian'] <= cutoffs[1])
        print('-- Winter Data Removed')
    else:
        keep = ~(np.logical_and(fire['julian'] >= cutoffs[0],  # find just winter values
                                fire['julian'] <= cutoffs[1]))
        print('-- Summer Data Removed')
    fire = fire[keep]
    fire.reset_index(inplace=True, drop=True)

    return fire


def firedt(dataframe):
    """
    This function creates proper formatted datetimes from the very specific NASA VIIRS date columns

    :param dataframe: a dataframe of NASA VIIRS data, with their column titles
    :return: the same dataframe with a datetime column
    """

    import pandas as pd
    import numpy as np
    from dateConv import createDatetime

    # preallocate and define used columns of dataframe
    values = dataframe['acq_date']
    timedeltas = dataframe['acq_time']

    # separate datetime components
    sep = values.str.split('-')
    dataframe.insert(len(dataframe.columns), 'yr', sep.str[0].astype(int), True)
    dataframe.insert(len(dataframe.columns), 'mo', sep.str[1].astype(int), True)
    dataframe.insert(len(dataframe.columns), 'dy', sep.str[2].astype(int), True)
    dataframe.insert(len(dataframe.columns), 'hr', np.zeros(len(dataframe['dy'])).astype(int), True)

    # create datetimes
    dataframe.insert(len(dataframe.columns), 'dt',
                     createDatetime(dataframe['yr'].values,
                                    dataframe['mo'].values,
                                    dataframe['dy'].values,
                                    dataframe['hr'].values))

    # add timedelta of hour and minute from the acq_time column
    timedeltas = pd.to_timedelta(timedeltas, unit='m')
    dataframe.insert(len(dataframe.columns), 'datetime',
                     dataframe['dt'] + timedeltas)

    # remove other columns
    badcols = ['acq_time', 'acq_date', 'yr', 'mo', 'dy', 'hr', 'dt']
    df = dataframe.drop(badcols, axis=1)

    return df


def fireCombo(fireDF, otherDF, VIIRS=True):
    """
    This function combines a dataframe of fire information with an outside dataframe for comparison

    :param fireDF: The dataframe of fire information from either VIIRS or MODIS NASA products
    :param otherDF: Another dataframe to merge with
    :param viirs: Default true, uses VIIRS data. Set to false for MODIS specific dataframe
    :return:
    """
    from fireFuncs import firedt
    import numpy as np
    from scipy import stats
    import pandas as pd

    if VIIRS:
        # only keep high tolerance values for viirs
        cond = fireDF['confidence'] != 'l'
        fireDF = fireDF[cond]
        fireDF.reset_index(drop=True, inplace=True)

    # call datetime function to make datetimes
    fireDF = firedt(fireDF)

    if VIIRS:
        # remove some other columns for viirs Version
        badcols = ['scan', 'track', 'satellite', 'instrument', 'confidence', 'version', 'type', 'frp']
        fireDF.drop(badcols, axis=1, inplace=True)
        fireDF.reset_index(drop=True, inplace=True)
    else:
        badcols = ['scan', 'track', 'satellite', 'instrument', 'confidence', 'version', 'type', 'frp', 'daynight']
        fireDF.drop(badcols, axis=1, inplace=True)
        fireDF.reset_index(drop=True, inplace=True)

    # identify Z scores of other DF in value and normed Resid
    values = otherDF['value'].values
    z = np.abs(stats.zscore(values))
    otherDF['value_z'] = z

    normedvals = otherDF['normResid'].values
    z = np.abs(stats.zscore(normedvals))
    otherDF['normed_z'] = z

    # pd merge asof by datetime with the hour
    combo = pd.merge_asof(fireDF.sort_values('datetime'), otherDF,
                          on='datetime',
                          direction='nearest',
                          tolerance=pd.Timedelta('1 hours'))
    combo.dropna(axis=0, how='any', inplace=True)
    combo.reset_index(drop=True, inplace=True)

    # remove some other columns
    badcols = ['decyear', 'function', 'residsmooth']
    combo.drop(badcols, axis=1, inplace=True)

    return combo






