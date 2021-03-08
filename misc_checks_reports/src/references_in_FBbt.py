import wget
import re
import os

# get latest fbbt-edit.obo from github if not present
if not os.path.isfile('fbbt-edit.obo'):
    wget.download(
        'https://raw.githubusercontent.com/FlyBase/drosophila-anatomy-developmental-ontology/master/src/ontology/fbbt-edit.obo')

fbbt = open('fbbt-edit.obo', 'r').read()

# find dois
doi_pattern = re.compile('doi:[0-9a-zA-Z./\-()]+')
dois_raw = set(re.findall(doi_pattern, fbbt))
dois = [d.rstrip(').') for d in dois_raw]
dois = set(dois)

doi_file = open('dois.txt', 'w')
for d in dois:
    doi_file.write(d + '\n')


# find urls
url_pattern = re.compile('http[s]?://[a-zA-Z0-9./\-]*')
urls = set(re.findall(url_pattern, fbbt))

# filter to remove 'acceptable' urls
filtered_urls = [u for u in urls if not ('orcid' in u or 'flybase' in u or 'purl' in u)]

url_file = open('url.txt', 'w')
for u in filtered_urls:
    url_file.write(u + '\n')


# find PMIDs
pmid_pattern = re.compile('PMID:[0-9]+')
pmids = set(re.findall(pmid_pattern, fbbt))

pmid_file = open('pmid.txt', 'w')
for p in pmids:
    pmid_file.write(p + '\n')