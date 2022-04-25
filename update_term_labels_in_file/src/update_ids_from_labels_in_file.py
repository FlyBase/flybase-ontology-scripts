import pandas as pd
from vfb_connect.neo.neo4j_tools import Neo4jConnect, dict_cursor

nc = Neo4jConnect('http://kb.virtualflybrain.org', 'neo4j', 'neo4j')

# to run on a local file, amend details here:
file = './file.tsv'
id_column_name = 'FBbt_id'
label_column_name = 'FBbt_name'


def replace_ids(dataframe, id_col_name='FBbt_id', label_col_name='FBbt_name'):
    """Updates IDs from latest FBbt release (from VFB) based on labels.

    Label must be an exact match.
    Input is a dataframe - default for ID column to be 'FBbt_id' and label column as 'FBbt_name'.
    ID column not required in input."""
    col_order = dataframe.columns
    label_list = list(set(dataframe[dataframe[label_col_name].notnull()][label_col_name].tolist()))

    query = "MATCH (c:Class) WHERE c.label IN %s \
    RETURN c.short_form AS %s, c.label AS %s" \
            % (label_list, id_col_name, label_col_name)

    q = nc.commit_list([query])
    ids = dict_cursor(q)

    ids_df = pd.DataFrame(ids)
    ids_df = ids_df.applymap(lambda x: x.replace('_', ':'))

    existing_column = True
    try:
        dataframe = dataframe.drop(id_col_name, axis=1)
    except KeyError:
        existing_column = False
    dataframe = pd.merge(left=dataframe, right=ids_df, how='left', on=label_col_name)
    if existing_column:
        dataframe = dataframe[col_order]

    return dataframe


def replace_ids_in_file(filename, id_col_name='FBbt_id', label_col_name='FBbt_name'):
    """Updates ids from latest FBbt release (from VFB) based on labels.

    Input is a file - default for ID column to be 'FBbt_id' and label column as 'FBbt_name'."""
    input_dataframe = pd.read_csv(filename, sep='\t')
    output_dataframe = replace_ids(input_dataframe, id_col_name, label_col_name)

    output_dataframe.to_csv(filename, sep='\t', index=False)


if __name__ == "__main__":
    replace_ids_in_file(file, id_column_name, label_column_name)
