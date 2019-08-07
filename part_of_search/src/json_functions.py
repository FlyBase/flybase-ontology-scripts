#  These all take a decoded json version of an ontology (tested with fbbt) as produced by json.load()
import re


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

