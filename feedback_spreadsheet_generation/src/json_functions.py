#  These all take a decoded json version of an ontology (tested with fbbt) as produced by json.load()
import re
import pandas as pd
import sys
import json
import requests


def part_search(ontology, search_term):
    """Search for all terms with (direct or inherited) part_of or is_a relationships to the search term.

    Returns a list."""
    terms = [search_term]
    result = [search_term]
    x = 1
    while x > 0:
        x = 0  # will terminate search if no new results
        new_terms = list()
        for e in ontology['graphs'][0]['edges']:
            if (e['obj'] in terms) and ((e['pred'] == 'http://purl.obolibrary.org/obo/BFO_0000050')
                                        or (e['pred'] == 'is_a')):
                new_terms.append(e['sub'])
                x += 1  # keeps search going if new results are found
        terms.clear()
        for i in new_terms:
            if i not in result:  # add output terms to result if not there already
                result.append(i)
                terms.append(i)
        new_terms.clear()
    return result


def sub_search(ontology, search_term):
    """Search for all terms with (direct or inherited) is_a relationships to the search term."""
    terms = [search_term]
    result = [search_term]
    x = 1
    while x > 0:
        x = 0  # will terminate search if no new results
        new_terms = list()
        for e in ontology['graphs'][0]['edges']:
            if (e['obj'] in terms) and (e['pred'] == 'is_a'):
                new_terms.append(e['sub'])
                x += 1  # keeps search going if new results are found
        terms.clear()
        for i in new_terms:
            if i not in result:  # add output terms to result if not there already
                result.append(i)
                terms.append(i)
        new_terms.clear()
    return result


def find_label(ontology, term_id):
    """Finds the label for a given term ID, returns an empty string if term is not found."""

    label = ""
    for n in ontology['graphs'][0]['nodes']:
        if n['id'] == term_id:
            label = n['lbl']
    return label


def find_synonyms(ontology, term_id):
    """Finds synonyms (returns a list) for a given term ID.

    Returns an empty list if the term is not found and "None" if no synonyms.
    """

    synonyms = []
    synonyms.clear()
    for n in ontology['graphs'][0]['nodes']:
        if n['id'] == term_id:
            try:
                synonyms = [syn['val'] for syn in n['meta']['synonyms']]
            except:
                synonyms = "None"
    return synonyms


def find_symbol(ontology, term_id):
    """Finds the symbol (should only be one!) for a given term ID, returns an empty string if term is not found."""

    symbol = ""
    for n in ontology['graphs'][0]['nodes']:
        if n['id'] == term_id:
            symbol = [s['val'] for s in n['meta']['basicPropertyValues']
                      if s['pred'] == 'http://purl.obolibrary.org/obo/IAO_0000028']
    return symbol


def find_definition(ontology, term_id):
    """Finds the definition for a given term ID.

    Returns an empty string if term is not found and "None" if no definition.
    """
    definition = ""
    for n in ontology['graphs'][0]['nodes']:
        if n['id'] == term_id:
            try:
                definition = n['meta']['definition']['val']
            except:
                definition = "None"
    return definition


def find_def_refs(ontology, term_id):
    """Finds references on definition (returns a list) for a given term ID.

    Returns an empty list if term is not found and "None" if no references.
    """
    refs = []
    refs.clear()
    for n in ontology['graphs'][0]['nodes']:
        if n['id'] == term_id:
            try:
                refs = n['meta']['definition']['xrefs']
            except:
                refs = "None"
    return refs


def get_term_iris(search_iri, ontology=None,
                  cells_only=False):
    """Returns a list of all parts of all subclasses of the search term ('search_iri').

     Ontology file can be specified (must be json - default = FBbt from PURL).
     Can choose to restrict to cell types (in FBbt) using cells_only=True (default = False)."""
    if not ontology:
        ontology = requests.get("http://purl.obolibrary.org/obo/fbbt/fbbt.json").json()

    # check term is in ontology and print term name
    label = find_label(ontology, search_iri)
    if len(label) == 0:
        print("term not found - aborting")
        sys.exit()
    else:
        print('term = ' + label)

    # carry out search for terms with part_of or is_a relationships back to search term
    result_id_list = part_search(ontology, search_iri)

    # create and check against list of terms for cells if required
    # cell = FBbt:00007002
    if cells_only:
        cell_type_list = sub_search(ontology, "http://purl.obolibrary.org/obo/FBbt_00007002")
        result_id_list = [x for x in result_id_list if x in cell_type_list]

    return result_id_list


def get_term_details(id_list, ontology=None):
    """Returns a DataFrame with labels, synonyms, definitions and references for iris in id_list.

    Can specify ontology (default = FBbt)."""

    if not ontology:
        ontology = requests.get("http://purl.obolibrary.org/obo/fbbt/fbbt.json").json()

    result_label = [find_label(ontology, i) for i in id_list]  # one label per term
    result_symbol = [find_symbol(ontology, i) for i in id_list]  # one symbol per term
    result_syn = [find_synonyms(ontology, i) for i in id_list]  # list of synonyms per term
    result_def = [find_definition(ontology, i) for i in id_list]  # one def per term
    result_ref = [find_def_refs(ontology, i) for i in id_list]  # list of def refs per term

    # output list of results
    data = {"FBbt_ID": id_list, "Symbol": result_symbol, "Name": result_label, "Synonyms": result_syn,
            "Definition": result_def, "References": result_ref}
    return pd.DataFrame(data)

# move this somewhere else?
def iri_to_ols(iri):
    """Returns an OLS link for a given IRI.

    IRI must be in the format http://purl.obolibrary.org/obo/FBbt_00000001.
    Output is a dictionary in the form {"term": "FBbt:00000001", "link": "<hyperlink>"}.
    """
    if not re.match("\Ahttp://purl\.obolibrary\.org/obo/[a-zA-Z]*_[0-9]*", iri):
        print("Please enter IRI in the format http://purl.obolibrary.org/obo/FBbt_00000001")
        return
    else:
        term = iri.replace("http://purl.obolibrary.org/obo/", "")
        ontology = re.sub("_[0-9]*", "", term)
        term = term.replace("_", ":")
        ols = "https://www.ebi.ac.uk/ols/ontologies/" + ontology.lower() + "/terms?iri=" + iri
        return {"term": term, "link": ols}

