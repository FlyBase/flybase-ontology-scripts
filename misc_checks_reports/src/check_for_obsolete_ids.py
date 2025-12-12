import os
import pandas as pd
from oaklib import get_adapter

"""
Finds obsolete IDs used within tsv files in /files
"""

check_all_columns = False
id_column_names = ['FBbt_id']  # ignored if check_all_columns is True
update = True

try:
    ontology = get_adapter('fbbt-merged.db')
except(FileNotFoundError):
    ontology = get_adapter("sqlite:obo:fbbt")

all_obsoletes = [i for i in ontology.obsoletes()]
replacement_df = pd.DataFrame(ontology.obsoletes_migration_relationships(ontology.obsoletes()), columns=['old_id', 'rel', 'new_id'])
replacement_df = replacement_df[replacement_df['rel'] == 'IAO:0100001']
if replacement_df['old_id'].duplicated(keep=False).any():
    raise ValueError("Duplicate old IDs in replacement_df")
replacement_df.set_index('old_id', inplace=True)


def find_obsoletes_in_df(dataframe, id_col_names=['FBbt_id'], check_all_columns=False):
    """Checks whether FBbt IDs in a dataframe are obsolete (in replacement_df).
    Input is a dataframe - default for ID column to be 'FBbt_id'."""
    obsoletes = {}
    if check_all_columns:
        cols_to_check = dataframe.columns
    else:
        cols_to_check = id_col_names
    for i in cols_to_check:
        obsoletes[i] = [c for a in dataframe.loc[dataframe[i].notnull(), i].drop_duplicates()
                        for c in a.split('|') if c in all_obsoletes]

    if any(obsoletes.values()):
        print("Some obsolete terms in use:")
        print(obsoletes)
    else:
        print("No obsolete terms in use.")


def replace_obsoletes_in_df(dataframe, id_col_names=['FBbt_id'], check_all_columns=False):
    """Checks whether FBbt IDs in a dataframe are obsolete (in replacement_df).
    Input is a dataframe - default for ID column to be 'FBbt_id'."""
    if check_all_columns:
        cols_to_check = dataframe.columns
    else:
        cols_to_check = id_col_names

    obsoletes = {}
    for i in cols_to_check:
        dataframe[i] = dataframe[i].map(lambda x: '|'.join(
            y if y not in replacement_df.index else replacement_df.loc[y, 'new_id'] for y in x.split('|')),
                                        na_action='ignore')
        obsoletes[i] = [c for a in dataframe.loc[dataframe[i].notnull(), i].drop_duplicates()
                        for c in a.split('|') if c in all_obsoletes]

    if any(obsoletes.values()):
        print("Some obsolete terms could not be replaced:")
        print(obsoletes)
    else:
        print("No more obsolete terms in use.")

    return dataframe


def process_obsoletes_in_file(filename, id_col_names=['FBbt_id'], check_all_columns=False, update=False):
    """Checks whether FBbt IDs in a file are obsolete (in VFB).
    Input is a file - default for ID column to be 'FBbt_id'."""
    input_dataframe = pd.read_csv(filename, sep='\t', dtype='str')
    if update:
        updated_df = replace_obsoletes_in_df(input_dataframe, id_col_names, check_all_columns)
        updated_df.to_csv(filename, sep='\t', index=False)
    else:
        find_obsoletes_in_df(input_dataframe, id_col_names, check_all_columns)


if __name__ == "__main__":
    file_list = [f for f in os.listdir('files') if not f.startswith('.')]
    for file in file_list:
        process_obsoletes_in_file(f'files/{file}', id_column_names, check_all_columns, update)
