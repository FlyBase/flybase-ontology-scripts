import re
from conversion_functions import replace_greek


class Term:
    """For storing term name and synonym data from FBbt.
    Assumes that symbols will contain greek characters where possible"""
    def __init__(self):
        self.label = ""
        self.new_symbol = ""
        self.existing_symbol = ""
        self.synonyms = []
        self.add_as_symbol = False
        self.add_as_synonym_gr = False
        self.add_as_synonym_en = False

    def check_existing_info(self):
        if len(self.existing_symbol) == 0:
            self.add_as_symbol = True

        if self.new_symbol not in self.synonyms:
            self.add_as_synonym_gr = True

        if (replace_greek(self.new_symbol) not in self.synonyms)\
                and (self.new_symbol != replace_greek(self.new_symbol)):
            self.add_as_synonym_en = True


def get_synonym_info(mapping, ontology):
    """Makes Term classes in a dictionary from a table containing FBbt ids and symbols.
    Ontology is a networkx object as generated using obonet.
    Mapping expected to be a pandas dataframe with 'FBbt' (ID) and 'symbol' columns."""
    synonym_dict = {}
    synonym_pattern = re.compile('["].*["]')
    for i in mapping.index:
        term_id = mapping['FBbt'][i]
        x = Term()
        x.new_symbol = mapping['symbol'][i]
        x.label = ontology.nodes[term_id]['name']

        try:
            for p in ontology.nodes[term_id]['property_value']:
                if 'IAO:0000028' in p:
                    x.existing_symbol = p.lstrip('IAO:0000028 ')
        except KeyError:
            pass

        try:
            for syn in ontology.nodes[term_id]['synonym']:
                x.synonyms.append(synonym_pattern.match(syn).group(0).strip('"'))
        except KeyError:
            pass

        x.check_existing_info()

        synonym_dict[term_id] = x

    return synonym_dict


def get_all_existing_symbols(ontology):
    """Makes a dictionary of symbols (IAO:0000028) (= keys) and FBbt IDs (=values).
    Ontology is a networkx object as generated using obonet."""
    existing_symbols = {}

    for n in ontology.nodes:
        try:
            for p in ontology.nodes[n]['property_value']:
                if 'IAO:0000028' in p:
                    existing_symbols[p.lstrip('IAO:0000028 ')] = n
        except KeyError:
            pass

    return existing_symbols

# 'property_value': ['IAO:0006011 FBbt:00110924', 'IAO:0006011 FBbt:00111168']
# IAO:0000028
