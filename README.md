# rnc-code
## code to query the RNC for occurrences of inflections in the Clancy database
I converted the Inflection SQL database to CSV, and then split the CSV into 3 CSVs of 221,552 lines (```input/inflection_split_0.csv```, ```input/inflection_split_1.csv```, ```input/inflection_split_2.csv```). 

The ```rnc_form_scrape.py``` searches on each word in the csv, queries the RNC, and returns document and word occurrences. It takes one argument, an input CSV like ```input/inflection_split_0.csv```. 

I also included ```split_inflection_csv.ipynb```, the code I used to split the original CSV into 3 parts.
