# flory_fox_scraper
Program with scripts to:
1. scrape information on glass transition temperatures of polymers - 
        `scrape_polyinfo.py`, and
2. perform a Flory-Fox fit - `fit_flory_fox.py`.

Developed for case study in:  
>J.S. Peerless, N.J.B. Milliken, T.J. Oweida, M.D. Manning, Y.G. Yingling, Soft 
Matter Informatics: Current Progress and Challenges, Adv. Theory Simulations. 
0 (2018) 1800129. 
[doi:10.1002/adts.201800129](https://doi.org/10.1002/adts.201800129 "DOI").

Please cite paper above if used.

Author:  
James S Peerless  
Yingling Group  
North Carolina State University  

## `scrape_polyinfo.py`
This script will scrape the 
[NIMS PoLyInfo](http://polymer.nims.go.jp/index_en.html) database for glass 
transition temperatures (Tg) and number-averaged molecular weights (Mn) 
reported for a single polymer in each polymer class. Script will identify a 
polymer in each polymer class with the most Tg data reported, then scan samples
to extract Tg and Mn data. All data is then printed to a CSV file.

### Inputs
A valid PoLyInfo login email and password is required. User will also be
prompted for an output filename which will be the name of the output CSV file.

### Outputs
Script will output status updates and timing info to `stdout` and a CSV file
containing formatted information on data collected for each polymer targeted. 
CSV file includes:

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
* Tg Max +/- 2 sigma Interval
* K OLS Estimate in K mol/g
* K +/- 2 sigma Interval
* Number of Data Points Used for OLS Fit 
* Square Root of OLS Error Variance Estimate (sigma)
* OLS Covariance Matrix (V)

PNG file plotting fit, data, and residuals for each polymer class is saved to
a dedicated directory.
