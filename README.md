# SumUpTools
### Copyright © 2019 Max Stevens <maxstev@uw.edu>
### Distributed under terms of the MIT license.

Tools to work with the .nc-formatted SumUp database.

This is a work in development. I created it to make working with the sumup database easy for my own needs. If there is a feature you want me to add, or you want to add yourself, let me know. 

Currently, there are two files: sumup.py and SumUpTools.ipynb, which is a jupyter notebook. 

## Workflow

The workflow should be:


This script processes the sumup netCDF-formatted database of firn cores and puts them into pandas dataframes, saved in pickles (.pkl files). If the script has already been run, then the .pkl files are just loaded into the workspace (you need to be working in ipython to do this).

If the .pkl files do not exist in the directory, then the script generates them by assigning each unique core a number. It puts the data into two pandas dataframes (one for Antarctica and one for Greenland). The data is saved in a pickle for easy reloading (the processing is slow because the script needs to find unique values.) 

This may be of use in other scripts as an easy way to pull in data from the
sumup database.

The changes that I make from the original sumup database are:
- There is a core from the 1950's (likely a Benson core from Greeland) that has the lat/lon listed as -9999. I set the coordinates of the core to 75N, 60W.
- For cores that do not have a specific date, Lynn put 00 for the month and day. I use January 1 for all of those cores so that I can create a datetime object.

Optionally, you can choose to write metadata to a csv file that can be imported into google earth to see the locations of each core.

I have not done this, but it should be easy to do a csv write with only cores meeting some criteria, e.g. deeper than some depth.
