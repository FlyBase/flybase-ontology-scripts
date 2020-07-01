import pandas as pd
import os
from collections import OrderedDict
from conversion_functions import replace_spelled, replace_greek
import get_term_info
import obonet
import wget

"""
runs checks on input and makes template
"""
delete_edit_file = False
if not os.path.isfile("input_files/fbbt-edit.obo"):
    delete_edit_file = True
    wget.download(("https://raw.githubusercontent.com/FlyBase/"
                   "drosophila-anatomy-developmental-ontology"
                   "/master/src/ontology/fbbt-edit.obo"), "input_files/fbbt-edit.obo")

fbbt = obonet.read_obo("input_files/fbbt-edit.obo")

# input file should contain 'term', 'FBbt' and 'reference' columns
input_file = os.getcwd() + "/input_files/input.tsv"
term_table = pd.read_csv(input_file, sep='\t')\
    .applymap(str)\
    .applymap(lambda y: y.strip())
term_table_value_map = pd.read_csv(input_file, sep='\t').notnull()

# convert spelled-out greeks to symbols and add this as a column to the table
symbol = list()
for i in term_table.index:
    symbol.append(replace_spelled(term_table.term[i]))

term_table['symbol'] = symbol

# check for duplicates in input IDs and symbols
if max(term_table['FBbt'].value_counts()) > 1:
    print("Error: duplicate FBbt IDs in input file\nAborting")
    raise SystemExit
if max(term_table['symbol'].value_counts()) > 1:
    print("Error: duplicate symbols in input file\nAborting")
    raise SystemExit

# Get existing symbol and synonym data for terms from FBbt
synonym_info = get_term_info.get_synonym_info(mapping=term_table, ontology=fbbt)

# Check new symbol does not clash with existing symbol
for term in term_table['FBbt']:
    if (len(synonym_info[term].existing_symbol) > 0) \
            and (synonym_info[term].existing_symbol != synonym_info[term].new_symbol):
        print("Error: %s already has a different symbol\nAborting" % term)
        raise SystemExit

# Check symbol does not exist as a symbol on another term
existing_symbols = get_term_info.get_all_existing_symbols(fbbt)
for s in term_table['symbol']:
    if s in existing_symbols.keys():
        print("Error: symbol %s already in use for %s\nAborting"
              % (s, existing_symbols[s]))
        raise SystemExit


# prepare an empty template:
template_seed = OrderedDict([('ID', 'ID'), ('CLASS_TYPE', 'CLASS_TYPE'),
                             ('RDF_Type', 'TYPE'), ("Symbol", "A IAO:0000028"),
                             ('ref1', ">A oboInOwl:hasDbXref"),
                             ('Synonym_gr', "A oboInOwl:hasExactSynonym"),
                             ('ref2', ">A oboInOwl:hasDbXref"),
                             ('Synonym_en', "A oboInOwl:hasExactSynonym"),
                             ('ref3', ">A oboInOwl:hasDbXref")])
# TODO - references

template = pd.DataFrame.from_records([template_seed])

# make a row for each entry in symbol_map
for i in term_table.index:

    row_od = OrderedDict([])  # new template row as an empty ordered dictionary
    for c in template.columns:  # make columns and blank data for new template row
        row_od.update([(c, "")])

    # these are the same in each row
    row_od["CLASS_TYPE"] = "subclass"
    row_od["RDF_Type"] = "owl:Class"

    # ID, symbol,synonyms
    row_od['ID'] = term_table.FBbt[i]
    if synonym_info[term_table.FBbt[i]].add_as_symbol:
        row_od["Symbol"] = synonym_info[term_table.FBbt[i]].new_symbol
        if term_table_value_map['reference'][i]:
            row_od["ref1"] = term_table['reference'][i]

    # synonyms if not present
    if synonym_info[term_table.FBbt[i]].add_as_synonym_gr:
        row_od["Synonym_gr"] = synonym_info[term_table.FBbt[i]].new_symbol
        if term_table_value_map['reference'][i]:
            row_od["ref2"] = term_table['reference'][i]
    if synonym_info[term_table.FBbt[i]].add_as_synonym_en:
        row_od["Synonym_en"] = replace_greek(synonym_info[term_table.FBbt[i]].new_symbol)
        if term_table_value_map['reference'][i]:
            row_od["ref3"] = term_table['reference'][i]

    # make new row into a DataFrame and add it to template
    new_row = pd.DataFrame.from_records([row_od])
    template = pd.concat([template, new_row], ignore_index=True, sort=False)

template.to_csv("./template.tsv", sep="\t", header=True, index=False)

if delete_edit_file:
    os.remove("input_files/fbbt-edit.obo")

