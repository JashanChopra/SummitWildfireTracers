"""
dateConv is a centralized script that contains a variety of functions useful for quickly and rapidly converting
datetimes. This is a common issue to a large number of datasets. The functions in here are used for analyses across
the entire root folder.

"""
from numba import njit
import numpy as np
import pandas as pd

def toYearFraction(date):
    """
    [old] This function takes datetimes and converts them to a decimal year, it only works on a single value

    :param date: a singular datetime value
    :return: returns a decimal year float value
    """
    from datetime import datetime as dt
    import time

    # returns seconds since epoch
    def sinceEpoch(datetime):
        return time.mktime(datetime.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction


def isleapyear(yr):
    """
    This function determines if a year is a leap year

    :param yr: an integer year value (i.e: 2019)
    :return: boolean, True if a leap year, False if not a leap year
    """
    import pandas as pd

    # Month and Day do not matter, just required. Converts to dataframe
    placeholder = pd.DataFrame({'year': [yr], 'month': [1], 'day': [1]})

    # Converts to the datetime format
    date = pd.to_datetime(placeholder)

    # Pandas function to tell if leap year
    leap = int(date.dt.is_leap_year)

    return leap


def decToDatetime(arr):
    """
    An approach to convert decyear values into datetime values with numpy vectorization to improve efficiency

    :param arr: a numpy array of decyear values
    :return: a numpy array of datetime values
    """

    import datetime as dt
    import calendar

    datetimes = []
    for i in range(len(arr)):

        year = int(arr[i])                                                  # get the year
        start = dt.datetime(year - 1, 12, 31)                               # create starting datetime
        numdays = (arr[i] - year) * (365 + calendar.isleap(year))           # calc number of days to current date
        result = start + dt.timedelta(days=numdays)                         # add timedelta of those days
        datetimes.append(result)                                            # append results

    return datetimes


def noaaDateConv(dataframe):
    """
    This function takes a dataframe with datetime values and converts it into a format that the NOAA ccg tool can
    easily read. It is specifically for working with the harmonic fitting tool.

    :param dataframe: A dataframe that has to have a column labeled 'datetime' which contains dt.datetime formatted
    items
    :return: the same dataframe with the datetime column replaced by year, month, day, hour, and minute
    """

    import pandas as pd

    year, month, day, hour, minute, cpd = [], [], [], [], [], []                        # preallocate lists
    cpd_name = dataframe.columns[1]                                                     # get the cpd name

    # iterate through rows and append lists, separating components of the datetime
    for index, value in dataframe.iterrows():
        year.append(value.datetime.year)
        month.append(value.datetime.month)
        day.append(value.datetime.day)
        hour.append(value.datetime.hour)
        minute.append(value.datetime.minute)
        cpd.append(value[cpd_name])

    # drop previous columns
    dataframe.drop(['datetime', cpd_name], axis=1, inplace=True)
    dataframe.reset_index(drop=True, inplace=True)

    # append each list to the new dataframe in appropriate order
    for item in [year, month, day, hour, minute, cpd]:
        item = pd.Series(item)
        dataframe = dataframe.merge(item.to_frame(), left_index=True, right_index=True, how='inner')

    # rename columns
    dataframe.columns = ['year', 'month', 'day', 'hour', 'minute', cpd_name]

    return dataframe


@njit
def convDatetime(yr, mo, dy, hr):
    """
    convDatetime takes values (likely from an array) and quickly converts them to decimal year format. Unfortunately
    it does not account for leap years but if a level of accuracy that high is not required using this function with
    numba's @njit provides nanosecond for looping of massive arrays.

    :param yr: year, numpy array
    :param mo: month, numpy array
    :param dy: day, numpy array
    :param hr: hour, numpy array
    :return: the decimal year, numpy array
    """
    date = np.empty(yr.shape)                                                   # preallocate date
    for i in range(len(yr)):                                                    # iterate through all values
        date[i] = ((yr[i]) +                                                    # year +
                   (mo[i] / 12) +                                               # month rem
                   (dy[i] / 365 / 12) +                                         # day rem
                   (hr[i] / 24 / 365 / 12))                                     # hr rem
    return date


def createDatetime(yr, mo, dy, hr):
    """
    Same thing as above function but converts to datetime format instead of decimal year. This function accounts for
    leap years assuming the day is specified as 366.
    """
    import datetime as dt

    datetime = []
    for i in range(len(yr)):

        if isinstance(yr[i], str):
            if len(yr[i]) == 2:
                yr[i] = '20' + yr[i]

        time = dt.datetime(int(yr[i]), int(mo[i]),
                           int(dy[i]), int(hr[i]))

        datetime.append(time)

    return datetime

