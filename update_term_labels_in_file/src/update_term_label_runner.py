import update_term_labels_in_file
import os

"""Updates labels in all files in 'files' folder"""

file_list = os.listdir('files')

for f in file_list:
    update_term_labels_in_file.replace_labels_in_file(os.path.join('files', f))
