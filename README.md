# Scrape City of Milwaukee's MPROP Daily; Add WGS84 Lat/Long From City Parcelbase

A postprocess script in Github's Flat Data actions is used to fire a Python script that collects key property data from the City of Milwaukee.

## Execution :

- the Flat Data action is scheduled daily.

- the `postprocess.ts` script is then run, triggers the install of python packages (including geopandas!), and runs the main python script `postprocess.py`.

- `postprocess.py` prints out its received arguments, and then generates a CSV file `flat_mprop.csv`. This generates a cleaned, workable MPROP file with full land use descriptions and lat/long parcel centroids in WGS84.


## Next steps:
- add tax delinquency
- add neighborhood demographics

## Thanks

- Thanks to the Github Octo Team
- Thanks to [Pierre-Olivier Simonard](https://github.com/pierrotsmnrd/flat_data_py_example) for his repo on implementing Flat data as a Python postprocess file.

