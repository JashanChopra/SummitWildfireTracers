from fireFuncs import fireData
from dateConv import createDatetime
from datetime import timedelta

import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import shapely.geometry as sgeom
import pandas as pd
import os
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import matplotlib as mpl


def trajPlot(root, grids=True, title=None, zscores=None, viirs=True, summer=True):
    """

    :param root: Directory location of trajectory files
    :param grids: Default True, displays gridlines on graph
    :param title: Default None, displays plot title
    :param zscores: Dataframe of atmospheric info with z scores or just z scores by date
    :param viirs: Default True, uses viirs NASA data instead of MODIS for fire counts
    :return:
    """

    fig = plt.figure(figsize=[10, 8])                                               # setup fig
    ax = fig.add_subplot(projection=ccrs.NearsidePerspective(-38, 72))              # subplots
    fig.subplots_adjust(top=0.970,                                                  # adjust sizing
                        bottom=0.012,
                        left=.002,
                        right=.981,
                        hspace=0.27,
                        wspace=0.02)
    ax.coastlines(zorder=3)                                                         # add coastlines
    ax.stock_img()                                                                  # stock background
    if grids is True:
        ax.gridlines()                                                              # gridlines

    ax.set_title(title)

    # plot summit ----
    ax.plot(-38.4592, 72.5796, marker='*', color='green', markersize=10, alpha=0.9,
            transform=ccrs.Geodetic(), label='Summit')
    print('-- Plot Setup Finished')

    # create colormap
    cmap = cm.seismic                                                               # cmap
    colors = cmap(np.arange(256))                                                   # color linspace
    zs = zscores['zscores'].values                                                  # all z values
    minz = min(zs)                                                                  # max and min z scores
    maxz = max(zs)
    zscorechart = np.linspace(minz, maxz, num=256)                                  # equal z score linspace to match

    # plot trajectories ----
    frame = []
    for filename in os.listdir(root):

        colnames = ['recep', 'v2', 'yr', 'mo', 'dy', 'hr', 'na', 'na1', 'backhrs', 'lat', 'long', 'alt', 'pres']
        data = pd.read_csv(root + '\\' + filename,
                           header=None,                                             # read trajectories
                           delim_whitespace=True,
                           error_bad_lines=False,
                           names=colnames)

        data.dropna(axis=0, how='any', inplace=True)                                # drop NaNs
        badcols = ['recep', 'v2', 'na', 'na1']                                      # drop poor columns
        data.drop(badcols, axis=1, inplace=True)
        data.reset_index(drop=True, inplace=True)

        createdtimes = createDatetime(data['yr'].values,                            # create datetimes
                                      data['mo'].values,
                                      data['dy'].values,
                                      data['hr'].values)
        data['datetime'] = pd.Series(createdtimes).to_numpy()
        data.drop(['yr', 'mo', 'dy', 'hr'], axis=1, inplace=True)                   # drop old dates

        # summer / winter removal
        dates = data['datetime'].tolist()                                           # put datetimes in list
        julian = []                                                                 # preallocate
        for d in dates:                                                             # loop over each date
            tt = d.timetuple()                                                      # create a timetuple from date
            jul = tt.tm_yday                                                        # get the julian year
            julian.append(jul)                                                      # append that to a list
        data['julian'] = julian                                                     # add to dataframe

        cutoffs = (120, 305)
        if summer:
            keep = np.logical_and(data['julian'] >= cutoffs[0],                     # find just summer values
                                  data['julian'] <= cutoffs[1])
        else:
            keep = ~(np.logical_and(data['julian'] >= cutoffs[0],                   # find just winter values
                                    data['julian'] <= cutoffs[1]))
        data = data[keep]

        if len(data.index) != 0:                                                    # skip over empty dataframes
            zscores['datetime'] = [pd.Timestamp(x) for x in zscores['datetime']]
            merged = pd.merge_asof(data.sort_values('datetime'), zscores,           # merge with zscores
                                   on='datetime',
                                   direction='nearest',
                                   tolerance=pd.Timedelta('1 hours'))

            frame.append(merged)

            track = sgeom.LineString(zip(data['long'].values, data['lat'].values))      # create trajectory

            currentz = merged['zscores'].iloc[-1]                                       # identify z value of trajectory
            merged['zscores'] = currentz                                                # set all traj zscores as curr
            nearmatch = zscorechart.flat[np.abs(zscorechart - currentz).argmin()]       # identify nearest match
            index = np.where(zscorechart == nearmatch)[0][0]                            # identify index in zscorechart
            z_color = tuple(colors[index].tolist())                                     # backsearch for color tuple

            ax.add_geometries([track], ccrs.PlateCarree(),                              # add to plot
                              facecolor='none', edgecolor=z_color,
                              linewidth=0.5, label='Trajectories')

    traj = pd.concat(frame, axis=0, ignore_index=True)                              # concat plots
    print('-- Trajectories Plotted')

    # plot fires -----
    fire = fireData(viirs=viirs, summer=summer)                                     # import fire data
    print('-- Fire Data Imported')
    print(len(fire))

    matchlongs, matchlats = [], []                                                  # matches preallocated
    notlongs, notlats = [], []                                                      # non matches preallocated
    matchzscores = []

    decplace = 0                                                                    # num of decimal places to match to
    timed = 24                                                                      # number of hours for a match

    f_lats = fire['latitude'].values.tolist()                                       # create lists for faster looping
    f_longs = fire['longitude'].values.tolist()
    firedates = fire['datetime']

    for i in range(len(f_lats)):                                                    # i = index, looping thru each row

        # identify if fire is in a back trajectory path at same times
        lats = np.in1d(np.around(traj['lat'].values, decplace),                     # identify similar latitudes
                       np.around(f_lats[i], decplace))
        longs = np.in1d(np.around(traj['long'].values, decplace),                   # identify similar longitudes
                        np.around(f_longs[i], decplace))
        cross = traj[lats & longs].values.tolist()                                  # double boolean means a cross

        if cross:
            trajdate = cross[0][5]                                                  # date of traj at cross
            match = timedelta(hours=timed) >= abs(firedates[i]-trajdate)            # are dates within timed var
            trajz = cross[0][9]                                                     # the current traj zscore

            if match:                                                               # if a match is found, append
                matchlongs.append(f_longs[i])
                matchlats.append(f_lats[i])
                matchzscores.append(trajz)
                print(f'Fire Match {i} Identified')

            else:
                notlongs.append(f_longs[i])                                         # else, append elsewhere
                notlats.append(f_lats[i])

        else:
            notlongs.append(f_longs[i])                                             # same for the back loop
            notlats.append(f_lats[i])


    print('-- All Fires Tagged')
    projection = ccrs.Geodetic()  # fire projection to use

    # plot the fires as scatterplots --
    ax.scatter(matchlongs, matchlats,
               marker='*', color='purple',
               transform=projection, s=75, zorder=6)

    ax.scatter(notlongs, notlats,
               marker='.', color='orange',
               alpha=0.7, s=4, transform=projection)

    print('-- All Fires Mapped')

    # create colorbar
    cbar_ax = fig.add_axes([.88, 0.15, 0.05, 0.7])                                  # add fig axes
    norm = mpl.colors.Normalize(vmin=minz, vmax=maxz)                               # normalize units
    cb = mpl.colorbar.ColorbarBase(cbar_ax, cmap=cmap,                              # create the colorbar
                                   orientation='vertical',
                                   norm=norm)
    cb.set_label('Z-Score Magnitude')                                               # give title

    legend_elements = [mpatches.Rectangle((0, 0), 1, 1, facecolor='green'),        # create legend elements
                       mpatches.Rectangle((0, 0), 1, 1, facecolor='orange'),
                       mpatches.Rectangle((0, 0), 1, 1, facecolor='purple'),
                       mpatches.Rectangle((0, 0), 1, 1,
                                          facecolor=tuple(colors[0].tolist()))]

    labels = ['Summit', 'VIIRS Fires', 'Intersected Fire',                          # label creation
              'Trajectory']

    ax.legend(handles=legend_elements, loc='lower left',                            # create legend
              fancybox=True, labels=labels,
              bbox_to_anchor=(-0.1, 0.01))

    print('-- Plot Finished')

    print('*------------*')
    print('STATISTICS')
    print(f'Number of trajectories: {len(traj) / 72}')
    print(f'Number of matches: {len(matchlongs)}')
    print(f'Percentage of matches: {(len(matchlongs) / len(fire)) * 100}')
    print(f'Average z-score of trajectories: {np.average(zs)}')
    print(f'Average z-score of matches: {np.average(matchzscores)}')

    plt.show()
