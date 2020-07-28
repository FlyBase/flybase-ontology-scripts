import pandas as pd
import update_term_labels_in_file
import re

# 1 rename input to old_input manually, then
# 2 run process_mapping_file.py
# 3 check new_input and manually rename to input
# 4 run symbol_template.py

# load old input file and set symbol as index
old_input = pd.read_csv('input_files/old_input.tsv', sep='\t')
old_input = old_input[['term', 'FBbt', 'reference']].set_index('term', 'FBbt')

# load file, update colnames to 'term' and 'FBbt', drop excess cols and rows
mapping = pd.read_csv('input_files/archive/hemibrain_1-1_type_mapping.tsv', sep='\t')
mapping = mapping.rename({'np_type': 'term', 'FBbt_id': 'FBbt', 'pub': 'reference'}, axis=1)\
    .drop(['notes', 'notes_2', 'comment', 'FBbt_name'], axis=1)
mapping = mapping[mapping['FBbt'].notnull()]

# remove different _a, _b, _c subtypes
mapping['term'] = mapping['term'].map(lambda x: re.sub(re.compile('_[a-z]$'), "", x))
mapping = mapping.drop_duplicates()

# keep only rows with a unique FBbt ID and set symbol as index
mapping = mapping[mapping.FBbt.isin(list(mapping['FBbt'].value_counts()[
                mapping['FBbt'].value_counts() == 1].index))].set_index('term', 'FBbt')

# check for symbols with changed FBbt IDs
changed_ids = []
for i in mapping.index:
    if i in old_input.index and old_input['FBbt'][i] != mapping['FBbt'][i]:
        changed_ids.append({i: {'old': old_input['FBbt'][i], 'new': mapping['FBbt'][i]}})
print('Changed FBbt IDs: ', changed_ids)

# add any reference detail that was in old file and missing from new
mapping.update(old_input)
# merge old and new (indicator keeps track of which file row came from)
mapping = pd.merge(mapping, old_input, on=['term', 'FBbt', 'reference'], how='outer', indicator=True)
mapping.reset_index(inplace=True)

# check for FBbt IDs with changed symbols (will appear multiple times in merge)
# index of value_counts is FBbt IDs
FBbt_with_new_symbol = list(mapping['FBbt'].value_counts()[mapping['FBbt'].value_counts() > 1].index)
changed_symbols_df = mapping[mapping.FBbt.isin(FBbt_with_new_symbol)].sort_values(by='FBbt')
changed_symbols_df['in_file'] = changed_symbols_df['_merge'].map({'left_only': 'new', 'right_only': 'old'})
changed_symbols_df = changed_symbols_df.drop(['_merge'], axis=1)

# update term labels and save file of conflicts
chsym_df_labels = update_term_labels_in_file.replace_labels(changed_symbols_df, id_col_name='FBbt')
chsym_df_labels.to_csv('symbol_conflicts.tsv', sep='\t', index=None)

# drop rows from old mapping where symbol is now different in new mapping
indices_to_drop = changed_symbols_df[changed_symbols_df['in_file'] == 'old'].index
mapping = mapping.drop(indices_to_drop, axis=0).drop(['_merge'], axis=1)

# drop Giant Fiber
mapping = mapping.drop(mapping[mapping['term'] == 'Giant Fiber'].index, axis=0)

# update term labels and save file
mapping = update_term_labels_in_file.replace_labels(mapping, id_col_name='FBbt')
mapping = mapping.sort_values(by='term')
mapping.to_csv('input_files/new_input.tsv', sep='\t', index=None)
