#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2019 Max Stevens <maxstev@uw.edu>
#
# Distributed under terms of the MIT license.

import netCDF4 as nc
import numpy as np
from datetime import datetime
import pandas as pd
import sys

'''
This script processes the sumup netCDF-formatted database of firn cores and puts
them into pandas dataframes, saved in pickles (.pkl files). 

It puts the data into two pandas dataframes (one for Antarctica and one for 
Greenland). The data is saved in a pickle for easy reloading (the processing is 
slow because the script needs to find unique values.) 

This may be of use in other scripts as an easy way to pull in data from the
sumup database.

The changes that I make from the original sumup database are:
- There is a core from the 1950's (likely a Benson core from Greeland) that has
the lat/lon listed as -9999. I set the coordinates of the core to 75N, 60W.
- For cores that do not have a specific date, Lynn put 00 for the month and day.
I use January 1 for all of those cores so that I can create a datetime object.

Optionally, you can choose to write metadata to a csv file that can be imported
into google earth to see the locations of each core.

I have not done this, but it should be easy to do a csv write with only cores 
e.g. deeper than some depth.
'''

def sumup(writer):

    print('Creating dataframes with sumup data!')
    print('This takes a little while! What a great time to grab a coffee.')
    ### Load the data.
    su = nc.Dataset('sumup_density_2020.nc','r')
    lat=su['Latitude'][:].data
    lon=su['Longitude'][:].data
    # The lat/lon are entered backwards in SumUp for the 180 citation.
    i180 = np.where(su['Citation'][:].data==180)[0]
    lat[i180] = su['Longitude'][i180].data
    lon[i180] = su['Latitude'][i180].data
    date=su['Date'][:].data.astype(int).astype(str)
    for kk,dd in enumerate(date):
        yr=dd[0:4]
        mo=dd[4:6]
        dy=dd[6:]
        if mo=='00':
            mo='01'
        elif mo=='90':
            mo = '01'
        elif int(mo)>12:
            mo = '01'
            dy = '01'
        if dy == '00':
            dy='01'
        elif dy == '32':
            dy='31'
        date[kk]=yr+mo+dy
    density=su['Density'][:].data
    top=su['Start_Depth'][:].data
    bot=su['Stop_Depth'][:].data
    mid=su['Midpoint'][:].data
    elev=su['Elevation'][:].data
    error=su['Error'][:].data
    cite=su['Citation'][:].data
    su.close()
    #############

    ### There is one entry that has no location, which is entered in sumup as -9999.
    ### Put the point at 75N, 60W. 
    mk = lat<-100
    lat[mk] = 75.0
    lon[mk] = -60.0
    ##############

    ### Find all of the unique cores (not as slow as before)
    ### and put into a dataframe
    ### faster than previously b/c I now use pandas unique

    d_all={}
    d_all['lat'] = lat 
    d_all['lon'] = lon       
    lpa=list(zip(lat, lon))
    d_all['latlon'] = lpa
    d_all['date'] = date 
    d_all['density'] = density 
    d_all['top'] = top 
    d_all['bot'] = bot 
    d_all['mid'] = mid 
    d_all['elev'] = elev 
    d_all['error'] = error 
    d_all['cite'] = cite.astype(int)

    df_all = pd.DataFrame(d_all)
    df_all.date = pd.to_datetime(df_all.date)
    df_all.set_index(['lat','lon','date','cite'],inplace=True)
    df_all['maxdepth'] = -9999.0
    df_all['coreid'] = -9999
    id_un = df_all.index.unique()
    for kk,ID in enumerate(id_un):
        df_all.loc[ID,'coreid'] = kk
        df_all.loc[ID,'maxdepth'] = np.max((df_all.loc[ID].bot,df_all.loc[ID].mid))
    df_all.set_index('coreid', append=True, inplace=True)
    df_all = df_all.reorder_levels(['coreid', 'lat', 'lon','date','cite'])

    ##############
    ### Separate for Greenland and Antarctica
    df_G = df_all.loc[df_all.index.get_level_values(1) > 0]
    df_A = df_all.loc[df_all.index.get_level_values(1) < 0]

    uAi = df_A.index.unique()
    df_A_meta = pd.DataFrame({'depth':np.zeros(len(uAi))},index = uAi)
    for core in df_A_meta.index.get_level_values('coreid'):
        df_A_meta.loc[core,'depth'] = df_A.loc[core].maxdepth.values[0]

    uGi = df_G.index.unique()
    df_G_meta = pd.DataFrame({'depth':np.zeros(len(uGi))},index = uGi)
    for core in df_G_meta.index.get_level_values('coreid'):
        df_G_meta.loc[core,'depth'] = df_G.loc[core].maxdepth.values[0]

    if writer:
        df_A_meta.to_csv('sumup_antarctica_2020.csv')
        df_G_meta.to_csv('sumup_greenland_2020.csv')

    ### pickle the dataframes for future loading:
    df_A.to_pickle('sumup_antarctica_2020.pkl')
    df_G.to_pickle('sumup_greenland_2020.pkl')
    df_all.to_pickle('sumup_all_2020.pkl')
    return df_A, df_G

if __name__ == '__main__':

    wtr = True #Can set to false if you do not want the metadata .csv files.
        
    dfa, dfg = sumup(wtr)

    ### The dataframes use a multi-index.
    ### dfa is for Antarctica, dfg is for Greenland.






