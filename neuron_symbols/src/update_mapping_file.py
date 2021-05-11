import pandas as pd
import re
import os

"""
This script updates the 'input.tsv' file from a provided file.
'input.tsv' is used by 'symbol_template.py to generate a robot template for producing a new 'neuron_symbols.owl'.

# 1 run process_mapping_file.py to add new mappings to 'input.tsv'
# 2 check 'new_input.tsv' and manually rename to 'input.tsv' if ok (and delete 'old_input.tsv')
# 3 run symbol_template.py
"""

# file of new symbol mappings to add to input file
if os.path.isfile('hemibrain_1-1_type_mapping.tsv'):
    new_mapping_file = 'hemibrain_1-1_type_mapping.tsv'
    hemibrain = True

if not hemibrain:
    new_mapping_file = 'new_symbols.tsv'

if os.path.isfile('input.tsv'):
    os.rename('input.tsv', 'old_input.tsv')

# load old input file and set symbol and ID as multiindex
old_input = pd.read_csv('old_input.tsv', sep='\t')
old_input = old_input[['term', 'FBbt', 'reference']].set_index('term', 'FBbt')

# load file, update colnames to 'term' and 'FBbt' (if using hemibrain file), drop excess cols and rows
new_mapping = pd.read_csv(new_mapping_file, sep='\t')
if hemibrain:
    new_mapping = new_mapping.rename({'np_type': 'term', 'FBbt_id': 'FBbt', 'pub': 'reference'}, axis=1)\
        .drop(['notes', 'notes_2', 'comment', 'FBbt_name'], axis=1)
new_mapping = new_mapping[new_mapping['FBbt'].notnull()]

# remove different hemibrain _a, _b, _c subtypes and remove duplicate rows
if hemibrain:
    new_mapping['term'] = new_mapping['term'].map(lambda x: re.sub(re.compile('_[a-z]$'), "", x))
new_mapping = new_mapping.drop_duplicates()

# check for duplicate FBbt IDs in the mapping file (will happen with hemibrain) and don't use these rows
dup_FBbt = list(new_mapping['FBbt'].value_counts()[
                                   new_mapping['FBbt'].value_counts() > 1].index)

if len(dup_FBbt) > 0:
    print('duplicate FBbt IDs in mapping file - ignoring these:')
    print(dup_FBbt)
new_mapping = new_mapping[~new_mapping.FBbt.isin(dup_FBbt)].set_index('term', 'FBbt')

# drop Giant Fiber and too broad mappings from hemibrain - TODO - check again later
if hemibrain:
    new_mapping = new_mapping.drop(
        ['Giant Fiber', 'H2', 'JO-A/B/C', 'LPC2', '5-HTPLP01', '5-HTPMPD01', 'KCab-m',
         'vDeltaA', 'DM3_vPN'], axis=0)

# check for symbols with changed FBbt IDs
changed_ids = []
for i in new_mapping.index:
    if i in old_input.index and old_input['FBbt'][i] != new_mapping['FBbt'][i]:
        changed_ids.append({i: {'old': old_input['FBbt'][i], 'new': new_mapping['FBbt'][i]}})
if len(changed_ids) > 0:
    print('WARNING: Symbols with changed FBbt IDs: ', changed_ids)

# add reference detail where present in one file and missing from other (for matching multiindex)
new_mapping.update(old_input, overwrite=False)
old_input.update(new_mapping, overwrite=False)
# merge old and new (indicator keeps track of which file row came from)
merged_mapping = pd.merge(new_mapping, old_input, on=['term', 'FBbt', 'reference'], how='outer', indicator=True)
merged_mapping.reset_index(inplace=True)

# check for FBbt IDs with changed symbols (will appear multiple times in merge)
# index of value_counts is FBbt IDs
FBbt_with_new_symbol = list(merged_mapping['FBbt'].value_counts()[merged_mapping['FBbt'].value_counts() > 1].index)
changed_symbols_df = merged_mapping[merged_mapping.FBbt.isin(FBbt_with_new_symbol)].sort_values(by='FBbt')
changed_symbols_df['in_file'] = changed_symbols_df['_merge'].map({'left_only': 'new', 'right_only': 'old'})
changed_symbols_df = changed_symbols_df.drop(['_merge'], axis=1)
if len(changed_symbols_df) > 0:
    print("Some FBbt ids have new symbols (using new symbol):")
    print(changed_symbols_df)

# drop rows from old file where symbol is different in new file
indices_to_drop = changed_symbols_df[changed_symbols_df['in_file'] == 'old'].index
merged_mapping = merged_mapping.drop(indices_to_drop, axis=0).drop(['_merge'], axis=1)

# sort dataframe (by symbol) and output to file
merged_mapping = merged_mapping.sort_values(by='term')
merged_mapping.to_csv('new_input.tsv', sep='\t', index=None)
