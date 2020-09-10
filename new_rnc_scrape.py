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
output_path = f'rnc_scrape_output{i}.csv'
output_columns = ['form','docs','occurrences']

if os.stat(output_path).st_size == 0:
    previous_output_df = pd.DataFrame(columns=output_columns)
    next_index_to_parse = 0
else:
    previous_output_df = pd.read_csv(output_path,usecols=output_columns,delimiter="\t")
    previous_output_list = [row for row in previous_output_df.values.tolist()]
    next_index_to_parse = len(previous_output_list)

# read in the forms of the Clancy database
names = ['id','lemma_id', 'form', 'stressed', 'type', 'frequency', 'sharoff_freq', 'sharoff_rank']
input_df = pd.read_csv(input_path, header=0, names=names, delimiter="\t", skiprows=next_index_to_parse, low_memory=False)
forms = [f[2] for f in input_df.values.tolist()]

def get_data(form):
    """get # of docs with and occurrences of a word in the full RNC"""
    r = requests.get('https://processing.ruscorpora.ru/search.xml?env=alpha&api=1.0&mycorp=&mysent=&mysize=&mysentsize=&dpp=&spp=&spd=&mydocsize=&mode=main&sort=i_grtagging&lang=ru&nodia=1&text=lexform&req=' + form)
    content = r.content
    soup = BeautifulSoup(content, 'html.parser')

    for d in soup.findAll('div', attrs={'class':'content'}):
        for p in soup.findAll('p', attrs={'class':'found'}):
            stats = [span.text.replace(' ','') for span in d.findAll('span', attrs={'class':'stat-number'})]
            if stats != []:
                docs, occurrences = stats[2], stats[3]
                return {'form' : [form], 'docs' : [docs], 'occurrences' : [occurrences]}
    return {'form' : [form], 'docs' : [None], 'occurrences' : [None]}

# write form data to csv
current_output_df = pd.DataFrame(columns=output_columns)

for i,form in enumerate(forms):
    time.sleep(0.500)
    try:
        current_output_df = current_output_df.append(pd.DataFrame(get_data(form)),ignore_index=True)
        if (i % 1000) == 0:
            print(f"{i+1}/{len(forms)} forms parsed.")
    except:
        print('Error running get_data on', form)
        
# concatenate previous and current dfs
result_df = pd.concat([previous_output_df, current_output_df])

# write dataframe to csv
try:
    result_df.to_csv(output_path,sep="\t",columns=output_columns)
except IOError as e:
    print("I/O error:", e)
    