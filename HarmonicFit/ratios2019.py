"""
Created June 17th, 2019. This file imports ethane, acetylene, and methane data to create ratios to be used with the
NOAA CCG Harmonic Fitting Tool. This file is similar to trimData.py, but it incorporates newer 2019 data as well as
more efficient and optimized coding procedures.
"""

# import libraries
import pandas as pd
import numpy as np

from calendar import isleap
from dateConv import noaaDateConv, decToDatetime


def ratioCreator(tolerance, cpd, bottom):
    """
    This function creates a ratio from two compounds

    :param tolerance: number of hours to average bottom values around (above and below) a single compound value
    :param cpd: the primary compound you want a ratio of, i.e the numerator
    :param bottom: the denominator value, should have more data points, creates the ratio
    :return:
    """

    ratio = []                                                                                  # preallocate array
    dates = []
    for date in cpd['DecYear'].values:                                                          # loop over numpy dates
        year = int(str(date)[:4])                                                               # get year
        rem = tolerance / 24 / (365 + isleap(year))                                             # date remainder
        high = date + rem                                                                       # high and lo tolerance
        low = date - rem
        indices = (bottom['DecYear'].values <= high) & (bottom['DecYear'].values >= low)        # index between
        values = bottom['val'][indices].values                                                  # get bot value
        if values.any():                                                                        # if not empty
            average = np.mean(values)                                                           # take mean
            ratio.append((cpd['val'][cpd['DecYear'] == date].values[0]) / average)              # append ratio
            dates.append(date)

    return ratio, dates


def ratios():
    """
    This function creates the ethane/methane and acetylene/methane ratios
    """

    # import data sets
    root = r'C:\Users\ARL\Desktop\J_Summit\analyses\Data'
    ethane = pd.read_csv(root + r'\ethaneFIT.txt', delim_whitespace=True, error_bad_lines=False, header=None)
    ace = pd.read_csv(root + r'\acetyleneFIT.txt', delim_whitespace=True, error_bad_lines=False, header=None)
    methane = pd.read_csv(root + r'\methane.txt', delim_whitespace=True, error_bad_lines=False, header=None)

    cols = ['DecYear', 'val', 'func', 'resid']                                          # column names

    # cleaning up data
    for sheet in [ethane, ace, methane]:
        # reassign col names
        if np.logical_or(sheet.iloc[0][0] == ethane.iloc[0][0], sheet.iloc[0][0] == ace.iloc[0][0]):
            sheet.columns = cols
            sheet.drop(['func', 'resid'], axis=1, inplace=True)                         # drop misc cols
        else:
            sheet.columns = cols + ['smooth']
            sheet.drop(['func', 'resid', 'smooth'], axis=1, inplace=True)

        sheet = sheet[sheet['DecYear'] >= 2012]                                         # remove pre 2012 vals
        sheet.dropna(axis=0, how='any', inplace=True)                                   # remove NaN rows

    # create ratios
    tolerance = 3                                                                       # tolerance in hours
    ethane.name = 'ethane'
    ace.name = 'ace'
    for sheet in [ethane, ace]:
        ratiosheet, datesheet = ratioCreator(tolerance, sheet, methane)
        datesheet = decToDatetime(datesheet)
        df = pd.DataFrame(columns=['datetime', 'val'])
        df['datetime'], df['val'] = datesheet, ratiosheet
        df = noaaDateConv(df)
        df.to_csv(f'{sheet.name}Ratio.txt', header=None, index=None, sep=' ', mode='w+')


if __name__ == '__main__':
    ratios()

