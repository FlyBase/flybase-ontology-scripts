import update_term_labels_in_file
import os

"""Updates labels in all files in 'files' folder"""

file_list = [f for f in os.listdir('files') if not f.startswith('.')]

for f in file_list:
    update_term_labels_in_file.replace_labels_in_file(filename=os.path.join('files', f),
                                                      id_col_name='FBbt_id',
                                                      source='fbbt-merged.db')
#
#                                                      id_col_name='FBbt_id', label_col_name='FBbt_name',