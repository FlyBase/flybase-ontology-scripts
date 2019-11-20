# Run release to put latest version fbbt.json in /oort
# This script finds is_a and part_of subclasses of a search term (FBbt ID)
# and returns IDs, names, synonyms, definitions and definition references

import json_functions
import json

search_iri = "http://purl.obolibrary.org/obo/FBbt_00004835"

# fbbt (local copy)
fbbt = json.load(open("/Users/clare/git/drosophila-anatomy-developmental-ontology/fbbt-simple.json", "r"))

id_list = json_functions.get_term_iris(search_iri, ontology=fbbt,
                             cells_only=False)
result_df = json_functions.get_term_details(id_list, ontology=fbbt)


result_df.to_csv("./term_list.tsv", sep="\t", header=True, index=False)  # DO NOT CHANGE


# example terms
# nervous system = FBbt_00005093, sense organ = FBbt_00005155, male terminalia = FBbt_00004835, ovary = FBbt_00004865