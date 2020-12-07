import pandas as pd
from vfb_connect.neo.neo4j_tools import Neo4jConnect, dict_cursor

nc = Neo4jConnect('http://kb.virtualflybrain.org', 'neo4j', 'neo4j')

# to run on a local file, amend details here:
file = './file.tsv'
id_column_name = 'FBbt_id'


def check_obsoletes_in_df(dataframe, id_col_name='FBbt_id'):
    """Checks whether FBbt IDs in a dataframe are obsolete (in VFB).

    Input is a dataframe - default for ID column to be 'FBbt_id'."""
    col_order = dataframe.columns
    FBbt_list = [str(x).replace(':', '_') for x in set(
        dataframe[dataframe[id_col_name].notnull()][id_col_name])]

    query = "MATCH (c:Class) WHERE c.short_form IN %s and c.is_obsolete = true\
    RETURN c.short_form AS %s, c.label AS %s" \
            % (FBbt_list, id_col_name, 'term_label')

    q = nc.commit_list([query])
    obsoletes = dict_cursor(q)

    if len(obsoletes) > 0:
        obsoletes_df = pd.DataFrame(obsoletes)
        obsoletes_df = obsoletes_df.applymap(lambda x: x.replace('_', ':'))

        print("Some obsolete terms in use:")
        print(obsoletes_df)
        return obsoletes_df
    else:
        print("No obsolete terms in use.")
        return False


def check_obsoletes_in_file(filename, id_col_name='FBbt_id', label_col_name='FBbt_name'):
    """Checks whether FBbt IDs in a file are obsolete (in VFB).

    Input is a file - default for ID column to be 'FBbt_id'."""
    input_dataframe = pd.read_csv(filename, sep='\t')
    output_dataframe = check_obsoletes_in_df(input_dataframe, id_col_name)

    return output_dataframe


if __name__ == "__main__":
    check_obsoletes_in_file(file, id_column_name)
