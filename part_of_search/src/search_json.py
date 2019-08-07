# Run release to put latest version fbbt.json in /oort
# This script finds is_a and part_of subclasses of a search term (FBbt ID)
# and returns IDs, names, synonyms, definitions and definition references

import requests
import json
import pandas as pd
import sys
import json_functions

# import fbbt from web
# fbbt = requests.get("http://purl.obolibrary.org/obo/fbbt/fbbt.json").json()

# import fbbt from /oort TODO - EDIT LOCATION FOR NEW RELEASE PROCESS
fbbt = json.load(open("/Users/clare/git/drosophila-anatomy-developmental-ontology/oort/fbbt.json", "r"))

# get user input for the search term
# nervous system = FBbt_00005093, sense organ = FBbt_00005155, male terminalia = FBbt_00004835, ovary = FBbt_00004865
search_term = "http://purl.obolibrary.org/obo/FBbt_" + input("Enter FBbt ID number: FBbt_")

# ask if user wants cell types only
cell_check = input("Return cell types only(y/n)?") is ("y" or "Y")

# search for subclasses (not parts) of cell if requested
# cell = FBbt:00007002
if cell_check:
    cell_type_list = json_functions.sub_search(fbbt, "http://purl.obolibrary.org/obo/FBbt_00007002")

# check term is in fbbt.json and print term name
label = json_functions.find_label(fbbt, search_term)
if len(label) == 0:
    print("term not found - aborting")
    sys.exit()
else:
    print('term = ' + label)

# carry out recursive search for terms with part_of or is_a relationships back to search term
result_id = json_functions.part_search(fbbt, search_term)

# check against list of terms for cells if required
if cell_check:
    result_id = [x for x in result_id if x in cell_type_list]

# list labels for all terms in id list
result_label = [json_functions.find_label(fbbt, i) for i in result_id]

# list lists of synonyms for all terms in id list
result_syn = [json_functions.find_synonyms(fbbt, i) for i in result_id]

# list definitions for all terms in id list
result_def = [json_functions.find_definition(fbbt, i) for i in result_id]

# list lists of references for definitions for all terms in id list
result_ref = [json_functions.find_def_refs(fbbt, i) for i in result_id]

# output list of results
data = {"FBbt_ID": result_id, "Name": result_label, "Synonyms": result_syn,
        "Definition": result_def, "References": result_ref}
result_df = pd.DataFrame(data)
result_df.to_csv("./term_list.tsv", sep="\t", header=True, index=False)  # DO NOT CHANGE
