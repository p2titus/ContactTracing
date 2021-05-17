# ContactTracing

## Installation/setup

Requirements:
- this project
- pip dependencies - i.e. run `pip install -r requirements.txt` (in a venv)
- PostgreSQL - the version doesn't really matter but 12 or higher works
- PostGIS extension for PostgreSQL, as well as the libraries that requires
    - on Ubuntu/Debian, use the ppa repository for PostgreSQL, which includes a package for PostGIS with all its requirements


Data:
- recent population data is included, in the `ukmidyearestimates20192020ladcodes.xlsx` file, which is sourced from the ONS, [here](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland). Note it needs to be converted to `.xlsx` first.
- UK region/county/etc. boundaries - again included, but also sourced from the [ONS geoportal](https://geoportal.statistics.gov.uk/search?collection=Dataset&sort=name&tags=all(BDY_ADM))
    - use the BUC borders - i.e. generalised to 500m and clipped to the coast, as anything more detailed makes the maps unnecessarily slow, for little gain.
    - you should download the shapefile option, and place all the files in the appropriate folder.

Geocoding:
- at the moment, the code only uses basic geocoding using the postcode.io API - so necessarily it only geocodes to within a postcode.
This is because geocoding is expensive and can be sourced from lots of different APIs. You should change the `get_coords`
  function in `government/hooks/hooks.py` if you want to use a different API.

Database setup:
- create a database and a user, and ensure these are in the `settings.py` file.
- run `create extension postgis` in the PostgreSQL prompt, to enable the geography extensions
- run `python manage.py migrate` in the venv, to create the tables
- run `python manage.py --shps --pops` to import the population and area data as described above. Change the paths in settings.py if you change/move the data files.

## Run
`python manage.py runserver`, and run it behind a reverse proxy (that deals with HTTPS/etc.)