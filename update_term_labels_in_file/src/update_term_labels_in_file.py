import pandas as pd
from vfb_connect.neo.neo4j_tools import Neo4jConnect, dict_cursor

nc = Neo4jConnect('http://kb.virtualflybrain.org', 'neo4j', 'neo4j')

# to run on a local file, amend details here:
file = './file.tsv'
id_column_name = 'FBbt_ID'
label_column_name = 'FBbt_name'


def replace_labels(dataframe, id_col_name='FBbt_ID', label_col_name='FBbt_name'):
    """Updates labels from latest FBbt release (from VFB) based on IDs.

    Input is a dataframe - default for ID column to be 'FBbt_ID' and label column as 'FBbt_name'.
    Label column not required in input."""
    col_order = dataframe.columns
    FBbt_list = [str(x).replace(':', '_') for x in set(
        dataframe[dataframe[id_col_name].notnull()][id_col_name])]

    query = "MATCH (c:Class) WHERE c.short_form IN %s \
    RETURN c.short_form AS %s, c.label AS %s" \
            % (FBbt_list, id_col_name, label_col_name)

    q = nc.commit_list([query])
    labels = dict_cursor(q)

    labels_df = pd.DataFrame(labels)
    labels_df = labels_df.applymap(lambda x: x.replace('_', ':'))

    existing_column = True
    try:
        dataframe = dataframe.drop(label_col_name, axis=1)
    except KeyError:
        existing_column = False
    dataframe = pd.merge(left=dataframe, right=labels_df, how='left', on=id_col_name)
    if existing_column:
        dataframe = dataframe[col_order]

    return dataframe


def replace_labels_in_file(filename, id_col_name='FBbt_ID', label_col_name='FBbt_name'):
    """Updates labels from latest FBbt release (from VFB) based on IDs.

    Input is a file - default for ID column to be 'FBbt_ID' and label column as 'FBbt_name'."""
    input_dataframe = pd.read_csv(filename, sep='\t')
    output_dataframe = replace_labels(input_dataframe, id_col_name, label_col_name)

    output_dataframe.to_csv(filename, sep='\t', index=None)


if __name__ == "__main__":
    replace_labels_in_file(file, id_column_name, label_column_name)
