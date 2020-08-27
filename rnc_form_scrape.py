import sys
from bs4 import BeautifulSoup
import requests
import csv
import time

# read in the forms of the Clancy database
columns = []

# change filepath if needed!
inflection_csv_path = 'inflection0.csv'
with open(inflection_csv_path,'r') as f: 
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if columns != []:
            for i, value in enumerate(row):
                columns[i].append(value)
        else:
            # first row
            columns = [[value] for value in row]

inflection_dict = {c[0] : c[1:] for c in columns}
forms = inflection_dict['form']

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
                return {'form' : form, 'docs' : docs, 'occurrences' : occurrences}
    return {'form' : form, 'docs' : None, 'occurrences' : None}

# write form data to csv
csv_columns = ['form','docs','occurrences']


# rename output path if needed
# (index in order to not overwrite any csv file)
i = inflection_csv_path[-5]
csv_file_path = f'rnc_freq_output{i}.csv'

try:
    with open(csv_file_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        # get number docs with word and number total word occurrences
        for form in forms:
            time.sleep(0.500)
            writer.writerow(get_data(form))
        print('Successful parsing of RNC.')

except IOError:
    print("I/O error")