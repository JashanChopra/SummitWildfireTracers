"""
This script serves to develop plots of each specific NHMC Compound from 2008-2018,
Each compound is plotted over the course of a single year with each line representing
a separate year

[note] This was one of the first real scripts I made for the project, it is a poor coding example, but it gives an
example of how much I've progressed since first learning Python
"""

# Import Libraries
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from fileLoading import loadExcel
import os

# import data
homedir = r'C:\Users\ARL\Desktop\Jashan\SummitWildfireTracers'
root = os.path.join(homedir, 'Data')

nmhcData = loadExcel(os.path.join(root, 'NMHC.XLSX'))
methaneData = loadExcel(os.path.join(root, 'Methane.XLSX'))

# Plotting NMHC
date = nmhcData.loc[:,'DecYear'] # Variable describing the decimal Year
numCompounds = np.linspace(0,11,num=12) # There are 12 compounds we want to plots
compounds = list(nmhcData.columns)[3:15] # List of the compound names
numYears = np.linspace(2008,2018,num=((2018 - 2008)+1)) # number of years total

for i in numCompounds:
    plt.figure(i) # Open a new fig for each compounds
    figure(num=None, figsize=(8, 6), dpi=160, facecolor='w', edgecolor='k')
    plt.xlabel('Day of Year',fontdict=None,labelpad=None, fontsize=14) # x labels all same
    plt.ylabel('Mixing Ratio [Parts per Billion]',fontsize=14,fontdict=None,labelpad=None) # y labels
    plt.title('Summit %s from 2008-2018' %compounds[int(i)],fontsize=18, fontdict=None,pad=None)
    plt.xticks(np.arange(0,361,30)) # 365 has no nice divsors

    for j in numYears:
        # The x axes are the dates of the given year (j) converted to a day decimal values
        x = (((nmhcData.loc[(date >= j) & (date < (j+1)),'DecYear'].values)-j) * 365) + 1
        # The y axes is the mixing ratio of that given day, for the specific compound
        y = nmhcData.loc[(date >= j) & (date < (j+1)),compounds[int(i)]].values
        nonzero = y > 0
        y = y[nonzero]
        x = x[nonzero]
        plt.plot(x,y,'.',alpha=0.5,label='%i'%j)
        plt.legend(bbox_to_anchor=(1.04,1), loc="upper left") # puts legend outside of graph

## Plotting [CH4] - same method as NMHC
dateCH4 = methaneData.loc[:,'DecYear']
numYearsCH4 = np.linspace(2012,2018,num=((2018-2012)+1))

for k in numYearsCH4:
    x2 = (((methaneData.loc[(dateCH4 >= k) & (dateCH4 < (k+1)),'DecYear'].values)-k) * 365) + 1
    y2 = methaneData.loc[(dateCH4 >= k) & (dateCH4 < (k+1)),'MR'].values
    plt.figure(12)
    plt.plot(x2,y2,'.',alpha=0.5,label='%i'%k)
    plt.xlabel('Day of Year',fontdict=None,labelpad=None) # Plot Xlabel
    plt.ylabel('Mixing Ratio [Parts per Billion]',fontdict=None,labelpad=None) # Plot Ylabel
    plt.title('Summit Methane [CH4] from 2012-2018',fontdict=None,pad=None)
    plt.ylim(1750,2050) # Excludes a few  outliers from the picture
    plt.legend(bbox_to_anchor=(1.04,1),loc="upper left")
    figure(num=None, figsize=(8, 6), dpi=160, facecolor='w', edgecolor='k')

plt.show() # Displays all figures

