# rnc-code
## code to query the RNC for occurrences of inflections in the Clancy database
I converted the Inflection SQL database to CSV, and then split the CSV into 3 CSVs of 221,552 lines (inflection_split_0.csv, inflection_split_1.csv, inflection_split_2.csv). 

The rnc_form_scrape.py searches on each word in the csv, queries the RNC, and returns document and word occurrences.

I also included the code I used to split the CSV into 3 parts.
