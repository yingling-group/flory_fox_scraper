# flory_fox_scraper
Program with scripts to:
    (a) scrape information on glass transition temperatures of polymers - 
        `scrape_polyinfo.py`, and
    (b) perform a Flory-Fox fit - `fit_flory_fox.py`.

Author: James S Peerless

For use in evaluation as intern candidate for Citrine Informatics only.

## `scrape_polyinfo.py`
This script will scrape the 
[NIMS PoLyInfo](http://polymer.nims.go.jp/index_en.html) database for glass 
transition temperatures (Tg) and number-averaged molecular weights (Mn) 
reported for a single polymer in each polymer class. Script will identify a 
polymer in each polymer class with the most Tg data reported, then scan samples
to extract Tg and Mn data. All data is then printed to a CSV file.

### Inputs
No inputs required.  PoLyInfo login information and output csv filename 
(`polyinfo.csv`) is stored in the Initialization section of a script.
This can easily be changed to a user input but is left in to allow for easy
running in the background.

### Outputs
Script will output status updates and timing info to `stdout` and a CSV file
(default name `polyinfo.csv`) containing formatted information on data
collected for each polymer targeted. CSV file includes:

* Polymer Class Name
* Polymer Class Abbreviation
* Full Polymer Name
* PoLyInfo Polymer Identification Number (PID)
* PoLyInfo Sample ID (SID)
* Scraped Glass Transition Temperature in K (Tg)
* Scraped Number-Averaged Molecular Weight in g/mol (Mn)

### Notes
Test with wired 100 GB/s connection timed at 4h 10min. Bulk of this time is
waiting for responses from PoLyInfo database.

## `fit_flory_fox.py`
This script takes formatted CSV file from `scrape_polyinfo.py` and performs a 
ordinary least squares (OLS) fit of the 
[Flory-Fox Equation](https://en.wikipedia.org/wiki/Flory%E2%80%93Fox_equation)
to the data for each individual polymer class. Duplicate data and Tg and Mn
points more than two standard deviations from mean are ignored.

### Inputs
User will be asked to provide an input filename, which must be a CSV file of
the format as produced by the `scrape_polyinfo.py` script above. User will 
also be asked for a output file prefix. This will determine the location and 
name for the output text file as well as the fit plots.

### Outputs
Script will output a human-readable `.txt` file with information from each
polymer in the input CSV file. Output for each polymer includes:

* Polymer Class Name
* Polymer Name
* PID
* Tg Max OLS Estimate in K
* Tg Max 95% Confidence Interval OLS Estimate
* K OLS Estimate in K mol/g
* K 95% Confidence Interval OLS Estimate 
* Number of Data Points Used for OLS Fit 
* Square Root of OLS Error Variance Estimate (sigma)
* OLS Covariance Matrix (V)
