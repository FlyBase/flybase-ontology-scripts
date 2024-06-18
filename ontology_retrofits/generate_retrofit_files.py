# add (one) unzipped report folder to this directory
# add one obo file to this directory (file needs to have replaced_by/consider annotations)
# check for lists in output New_id and New_name columns - these indicate that there was no single replaced_by term

import os
import re
import pandas as pd
from oaklib import get_adapter

dir_pattern = r'fb_([0-9]{4}_[0-9]{2})_([A-z]+)_reports'
working_directory = os.getcwd()

# Identify the ontology file (must only be one)
obo_files = [file for file in os.listdir(working_directory) if file.endswith(".obo")]
if len(obo_files) == 1:
    ontology_file = obo_files[0]
else:
    raise FileNotFoundError(f'Single obo file must be in present in {working_directory}')

# Identify the report folder and obsoletion reports
obsoletion_reports = []
report_folder = ''
for root, dirs, files in os.walk(working_directory):
    report_folder_match = re.match(dir_pattern, os.path.basename(root))
    if report_folder_match:
        report_folder = report_folder_match.group(0)
        retrofit_folder = f'fb_{report_folder_match.group(1)}_{report_folder_match.group(2).lower()}_rf'
        for file in files:
            if re.match(r'.*_new_obsoletes.lst', file):
                obsoletion_reports.append(file)

if not report_folder:
    raise FileNotFoundError(f'No report folder found in {working_directory}')
else:
    try:
        os.mkdir(retrofit_folder)
    except FileExistsError:
        pass

ontology = get_adapter(ontology_file)


def lookup_replacements(term_id):
    """
   Looks up replacements for a given term_id.
   It checks for 'oio:consider' and 'oio:replaced_by' relationships,
   and returns a single replacement term with its label if available.
   If no or multiple replacements are found, it prints a warning message
   and returns a list of all possible replacements with their labels.
   Returns (term, label) or ([terms], [labels]).
   """
    consider = []
    replace = []
    for sub, rel, obj in ontology.obsoletes_migration_relationships([term_id]):
        if rel == 'oio:consider':
            consider.append(obj)
        elif rel == 'IAO:0100001':
            replace.append(obj)
    if (len(consider) == 0) and len(replace) == 1:
        return replace[0], ontology.label(replace[0])
    else:
        print(f'Warning: No single replacement for {term_id}')
        consider.extend(replace)
        labels = [ontology.label(c) for c in consider]
        return consider, labels


def filename_sub(lst_filename):
    """
    Returns a new filename by replacing the '.lst' extension with '_rf.tsv'.
    """
    if lst_filename[-4:] == '.lst':
        new_filename = lst_filename[:-4] + '_rf.tsv'
    return new_filename


for report in obsoletion_reports:
    rep_df = pd.read_csv(os.path.join(report_folder, report), sep='\t', dtype=str)
    if len(rep_df) > 0:
        rep_df[['New_id', 'New_name']] = rep_df.apply(lambda row: lookup_replacements(row.Chado_DBxref),
                                                      axis='columns', result_type='expand')
        rep_df.to_csv(os.path.join(retrofit_folder, filename_sub(report)), sep='\t', index=False)
