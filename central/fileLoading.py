"""
fileLoading is a centralized script that contains functions useful for quickly importing datasets. All
datasets are somewhat different, but the functions here often provide a useful starting point and are shared in
analyses.

"""


def loadExcel(filename):
    """
    loadExcel loads an excel file to a dataframe with a slightly cleaner look than the normal pd.read_excel, this
    was originally used as an introduction to creating functions

    :param filename: full filepath
    :return: dataframe
    """

    import pandas as pd
    data = pd.read_excel(filename)
    return data


def readCsv(filename):
    """
    Reads a csv with typical options used throughout these analyses

    :param filename: full filepath
    :return: dataframe
    """

    import pandas as pd
    data = pd.read_csv(filename,
                       delim_whitespace=True,
                       encoding='utf-8',
                       header=None,
                       error_bad_lines=False,
                       warn_bad_lines=True,
                       )

    return data
