import sys
from bs4 import BeautifulSoup
import requests
import csv
import time
import pandas as pd
import os

# usage: single argument of function is the name of the input csv file (inflection_split_x.csv)
input_path = sys.argv[1]

# check to see which word you left off on (rename output path if needed)
i = input_path[-5]
output_path = f'output/rnc_scrape_output{i}.csv'

output_columns = ['form','docs','occurrences']

try:
    previous_output_df = pd.read_csv(output_path, usecols=output_columns,delimiter="\t")
    previous_output_df = previous_output_df.dropna()  # dropping NA (forms with no data) so we can retry those
except pd.errors.EmptyDataError:
    previous_output_df = pd.DataFrame([], columns=output_columns)

# read in the forms of the Clancy database
names = ['id','lemma_id', 'form', 'stressed', 'type', 'frequency', 'sharoff_freq', 'sharoff_rank']
input_df = pd.read_csv(input_path, header=0, names=names, delimiter="\t", low_memory=False)

# get list of forms to query based on any previous output
input_forms = set(input_df['form'].values.tolist()) 
previous_output_forms = set(previous_output_df['form'].values.tolist())
forms = input_forms - previous_output_forms

RNC_URL = 'https://processing.ruscorpora.ru/search.xml?env=alpha&api=1.0&mycorp=&mysent=&mysize=&mysentsize=&dpp=&spp=&spd=&mydocsize=&mode=main&sort=i_grtagging&lang=ru&nodia=1&text=lexform&req={form}'

def make_request(form, retries=3):
    try:
        r = requests.get(RNC_URL.format(form=form))
    except requests.exceptions.ConnectionError as e:
        print(e)
        print("connection error - wait 60 seconds and then retry the request")
        time.sleep(60)
        r = requests.get(RNC_URL.format(form=form))

    if r.status_code != 200:
        print(r.status_code, form)
    if r.status_code == 429: 
        wait_time = int(10 + 60 * (1/retries))
        print(f"too many requests -- wait {wait_time} seconds before retrying ({retries} left)")
        time.sleep(10  + 60 * (1/retries))
        if retries > 0:
            return make_request(form, retries=retries-1)
    return r.content


def get_data(form, content):
    """get # of docs with and occurrences of a word in the full RNC"""
    soup = BeautifulSoup(content, 'html.parser')
    for d in soup.findAll('div', attrs={'class':'content'}):
        for p in soup.findAll('p', attrs={'class':'found'}):
            stats = [span.text.replace(' ','') for span in d.findAll('span', attrs={'class':'stat-number'})]
            if stats != []:
                docs, occurrences = stats[2], stats[3]
                return [form, docs, occurrences]
    return [form, None, None]


with open(output_path, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter='\t')
    csv_writer.writerows([output_columns] + previous_output_df.values.tolist())
    csvfile.flush()
    for i, form in enumerate(forms):
        time.sleep(1)
        content = make_request(form)
        current_row = get_data(form, content)
        try:
            csv_writer.writerow(current_row)
            csvfile.flush()
            print(current_row)
            if (i % 1000) == 0:
                print(f"{i}/{len(forms)} forms parsed.")
        except Exception as e:
            print('Error running get_data on', form)
            print(e)
