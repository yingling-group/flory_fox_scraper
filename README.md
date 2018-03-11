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

### Required Packages
```python
re
requests
BeautifulSoup
pandas
```
### Notes
Test with wired 100 GB/s connection timed at 4h 10min. Bulk of this time is
waiting for responses from PoLyInfo database.

## `fit_flory_fox.py`


