# Scrape City of Milwaukee's MPROP Daily; Add WGS84 Lat/Long From City Parcelbase

A postprocess script in Github's Flat Data actions is used to fire a Python script that collects key property data from the City of Milwaukee.

## Execution :

- the Flat Data action is scheduled daily.

- the `postprocess.ts` script is then run, triggers the install of python packages (including geopandas!), and runs the main python script `postprocess.py`.

- `postprocess.py` prints out its received arguments, and then generates a CSV file `flat_mprop.csv`. This generates a cleaned, workable MPROP file with full land use descriptions and lat/long parcel centroids in WGS84. The script then spatially joins imported census tract, Milwaukee Police Department, and Aldermanic boundaries per parcel.

## Data Notes

- [MPROP](https://data.milwaukee.gov/dataset/mprop)
- Census estimates are taken from the ACS 5-Year Estimates: 2015-2019 ACS 5-Year Estimates. 
- [MPD Police Boundaries](https://data.milwaukee.gov/dataset/mpd-stations)
- [Aldermanic Boundaries](https://data.milwaukee.gov/dataset/aldermanic-districts)


## Next steps:
- add tax delinquency


## Thanks

- Thanks to the Github Octo Team
- Thanks to [Pierre-Olivier Simonard](https://github.com/pierrotsmnrd/flat_data_py_example) for his repo on implementing Flat data as a Python postprocess file.

