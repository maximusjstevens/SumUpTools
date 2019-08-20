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
import matplotlib.pyplot as plt
import sys


'''
This script processes the sumup netCDF-formatted database of firn cores and puts
them into pandas dataframes, saved in pickles (.pkl files). If the script has
has already been run, then the .pkl files are just loaded into the workspace 
(you need to be working in ipython to do this).

If the .pkl files do not exist in the directory, then the script generates them
by assigning each unique core a number. It puts the data into two pandas 
dataframes (one for Antarctica and one for Greenland). The data is saved in a 
pickle for easy reloading (the processing is slow because the script needs to 
find unique values.) 

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

def sumup(writer=False):

    try:
        dfg = pd.read_pickle('sumup_greenland.pkl')
        dfa = pd.read_pickle('sumup_antarctica.pkl')
        print('.pkl files for Anarctica and Greenland have been found; loading')

    except Exception: 
        print('.pkl files for Anarctica and Greenland have not been found, so they will be created.')
        print('This takes a little while! What a great time to grab a coffee.')
        ### Load the data.
        su = nc.Dataset('sumup_density_2019.nc','r+')
        lat=su['Latitude'][:]
        lon=su['Longitude'][:]
        date=su['Date'][:].astype(int).astype(str)
        for kk,dd in enumerate(date):
            yr=dd[0:4]
            mo=dd[4:6]
            dy=dd[6:]
            if mo=='00':
                mo='01'
            elif mo=='90':
                mo = '01'
            if dy == '00':
                dy='01'
            elif dy == '32':
                dy='31'
            date[kk]=yr+mo+dy
        density=su['Density'][:]
        top=su['Start_Depth'][:]
        bot=su['Stop_Depth'][:]
        mid=su['Midpoint'][:]
        elev=su['Elevation'][:]
        error=su['Error'][:]
        cite=su['Citation'][:]
        #############

        ### There is one entry that has no location, which is entered in sumup as -9999.
        ### Put the point at 75N, 60W. 
        mk = lat<-100
        lat[mk] = 75.0
        lon[mk] = -60.0
        ##############

        ### Find all of the unique cores (slow)
        llpair=np.array((lat,lon)).T
        xx=np.c_[lat,lon,cite,date]
        core_unique = np.unique(xx,axis=0)
        coreid = np.zeros(len(xx))

        for ii,features in enumerate(core_unique):
            inds = np.where((xx==features).all(axis=1))[0]
            coreid[inds]=ii+1
        coreid = coreid.astype(int)
        ##############

        ##############
        ### Antarctica
        amask = lat < 0
        unci_a = np.unique(cite[amask])
        acores = coreid[amask]
        uacores = np.unique(acores)
        lpa=list(zip(lat[amask], lon[amask]))

        da={}
        da['coreid'] = coreid[amask]
        da['lat'] = lat[amask]
        da['lon'] = lon[amask]      
        da['latlon'] = lpa
        da['date'] = date[amask]
        da['density'] = density[amask]
        da['top'] = top[amask]
        da['bot'] = bot[amask]
        da['mid'] = mid[amask]
        da['elev'] = elev[amask]
        da['error'] = error[amask]
        da['cite'] = cite[amask]

        dfa = pd.DataFrame(da)
        dfa.date = pd.to_datetime(dfa.date)
        dfa.set_index(['coreid','lat','lon','date','cite'],inplace=True)

        ### use the below code to create a csv with metadata, including lat lon 
        ### pairs, that can be imported into google earth pro. The other data is
        ### citation, date, coreid number, and maximum depth.
        if writer:
            ucid_a = np.zeros(len(uacores))
            uci_a = np.zeros(len(uacores))
            ubot_a = np.zeros(len(uacores))
            udate_a = np.zeros(len(uacores))
            ull_a = np.zeros((len(uacores),2))
            for jj in range(len(uacores)):
                idx = np.where(acores == uacores[jj])[0][0]
                idx2 = np.where(acores == uacores[jj])[0][-1]
                ucid_a[jj] = da['coreid'][idx]
                uci_a[jj] = da['cite'][idx]
                ubot_a[jj] = np.max((da['bot'][idx2],da['mid'][idx2]))
                udate_a[jj] = da['date'][idx]
                ull_a[jj] = da['latlon'][idx]
            a_out = np.c_[ull_a,uci_a,ucid_a,ubot_a,udate_a]
            np.savetxt('sumup_antarctica.csv',a_out,delimiter=',',fmt='%1.4f, %1.4f, %i, %i, %1.3f, %s',header='Latitude,Longitude,Citation,coreid,bot_depth,date')

        ##############
        ### Greenland
        gmask = lat>0
        unci_g = np.unique(cite[gmask])
        gcores = coreid[gmask]
        ugcores = np.unique(gcores)
        lpg=list(zip(lat[gmask], lon[gmask]))

        dg={}
        dg['coreid'] = coreid[gmask]
        dg['lat'] = lat[gmask]
        dg['lon'] = lon[gmask]
        dg['latlon'] = lpg
        dg['date'] = date[gmask]
        dg['density'] = density[gmask]
        dg['top'] = top[gmask]
        dg['bot'] = bot[gmask]
        dg['mid'] = mid[gmask]
        dg['elev'] = elev[gmask]
        dg['error'] = error[gmask]
        dg['cite'] = cite[gmask]

        dfg = pd.DataFrame(dg)
        dfg.date = pd.to_datetime(dfg.date)
        dfg.set_index(['coreid','lat','lon','date','cite'],inplace=True)

        ### use the below code to create a csv with metadata, including lat lon 
        ### pairs, that can be imported into google earth pro. The other data is
        ### citation, date, coreid number, and maximum depth.
        if writer:
            ucid_g = np.zeros(len(ugcores))
            uci_g = np.zeros(len(ugcores))
            ubot_g = np.zeros(len(ugcores))
            udate_g = np.zeros(len(ugcores))
            ull_g = np.zeros((len(ugcores),2))
            for jj in range(len(ugcores)):
                idx = np.where(gcores == ugcores[jj])[0][0]
                idx2 = np.where(gcores == ugcores[jj])[0][-1]
                ucid_g[jj] = dg['coreid'][idx]
                uci_g[jj] = dg['cite'][idx]
                ubot_g[jj] = np.max((dg['bot'][idx2],dg['mid'][idx2]))
                udate_g[jj] = dg['date'][idx]
                ull_g[jj] = dg['latlon'][idx]
            g_out = np.c_[ull_g,uci_g,ucid_g,ubot_g,udate_g]
            np.savetxt('sumup_greenland.csv',g_out,delimiter=',',fmt='%1.4f, %1.4f, %i, %i, %1.3f, %s',header='Latitude,Longitude,Citation,coreid,bot_depth,date')

        ### pickle the dataframes for future loading:
        dfa.to_pickle('sumup_antarctica.pkl')
        dfg.to_pickle('sumup_greenland.pkl')

    return dfa, dfg


if __name__ == '__main__':

    if '-w' in sys.argv:
        print('Writing metadata to .csv')
        wtr = True
    else:
        print('Not writing metadata to .csv')
        wtr = False
        
    dfa, dfg = sumup(wtr) #optional argument of True if you want to write csv files.

    ### The dataframes use a multi-index.
    ### dfa is for Antarctica, dfg is for Greenland.
    ### If you want to query the dataframes, use xs:
    ### Examples:
    # dfg.xs('1990-06-20',level='date')
    # core337 = dfg.xs(337,level='coreid') # this one is probably most useful You can find the core of interest in the google earth map and query it here. 
    # dfg.xs(15,level='cite') # this one is useful to see all the cores from a specific citation.


    # core337.to_csv('c337.csv') # Save the core data to a csv file.




