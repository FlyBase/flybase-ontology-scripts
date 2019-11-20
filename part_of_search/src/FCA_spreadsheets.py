# Run release to put latest version fbbt.json in /oort
# This script finds is_a and part_of subclasses of a search term (IRI)
# and returns IDs, names, synonyms, definitions and definition references
# Then tidies this up and makes a nice xslx format spreadsheet

import json_functions
import json
import pandas as pd
import re

# example terms
# nervous system = FBbt_00005093, sense organ = FBbt_00005155, male terminalia = FBbt_00004835, ovary = FBbt_00004865
search_iri = "http://purl.obolibrary.org/obo/FBbt_00004835"

# fbbt (local copy)
fbbt = json.load(open("/Users/clare/git/drosophila-anatomy-developmental-ontology/fbbt-simple.json", "r"))

id_list = json_functions.get_term_iris(search_iri, ontology=fbbt,
                             cells_only=False)
term_list = json_functions.get_term_details(id_list, ontology=fbbt).applymap(str)

# minor tidying strings and lists
term_list = term_list.applymap(lambda x: x.replace("['", ""))  # tidy beginnings of lists
term_list = term_list.applymap(lambda x: x.replace("']", ""))  # tidy ends of lists
term_list = term_list.applymap(lambda x: x.replace("', '", "; "))  # tidy middles of lists
term_list = term_list.applymap(lambda x: re.sub("FBC:[a-zA-Z_]+;*\s*", "", x))  # remove FBC: refs
term_list = term_list.applymap(lambda x: re.sub("FlyBase:", "", x))  # remove FlyBase: prefixes

# substitute IRIs with hyperlinks

term_list["FBbt_ID"] = term_list["FBbt_ID"].apply(lambda x: "=HYPERLINK(\"" + json_functions.iri_to_ols(x)["link"]
                                                            + "\",\"" + json_functions.iri_to_ols(x)["term"] + "\")")

# substitute FBrfs with citations and links:

# open pub_miniref file (FBrfs are the index)
ref_list = pd.read_csv("pub_miniref.txt", sep=" == ", engine="python")
ref_list.columns = ["Reference"]

# list FBrfs in References column
fbrf_find = [re.findall("FBrf[0-9]+", ref) for ref in term_list.References]
fbrf_list = list(set([item for sublist in fbrf_find for item in sublist]))  # flattens list of lists

# replace FBrfs in term_list table
for fbrf in fbrf_list:
    term_list = term_list.applymap(lambda x: re.sub(fbrf, ref_list["Reference"][fbrf]
                                                    + " (flybase.org/reports/" + fbrf + ")", x))

# replace FlyPNS, DoOR
term_list = term_list.applymap(lambda x: x.replace("FlyPNS:", "http://www.normalesup.org/~vorgogoz/FlyPNS/"))
term_list = term_list.applymap(lambda x: x.replace(
    "DoOR:", "http://neuro.uni-konstanz.de/DoOR/content/receptor.php?OR="))


# add columns for review notes, suggested markers, abundance
term_list = term_list.reindex(columns=term_list.columns.tolist() + ['Review_notes', 'Suggested_markers', 'Abundance'])

# make new term file as xslx format
term_list.to_excel("./anatomy_terms.xlsx", header=True, index=False)
