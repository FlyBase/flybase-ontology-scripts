# generate a yaml file for adding node labels for lineage terms
# put it here: https://github.com/VirtualFlyBrain/vfb-prod/blob/master/

import wget
import pandas as pd

#file_url = 'https://raw.githubusercontent.com/FlyBase/drosophila-anatomy-developmental-ontology/master/src/patterns/data/all-axioms/neuroblastAnnotations.tsv'
#wget.download(file_url)

lineage_df = pd.read_csv('neuroblastAnnotations.tsv', dtype='str', sep='\t')

# drop sex-specific
lineage_df = lineage_df[~lineage_df['defined_class_label'].str.contains('male|female')]

yaml_lines = ['neo_node_labelling:\n']
nomenclature_cols = ['ito_lee', 'hartenstein', 'secondary', 'primary']
for i, row in lineage_df.iterrows():
    parts = []
    for col in nomenclature_cols:
        val = row.get(col)
        if pd.notna(val) and val != 'nan' and not val in parts:
            parts.append(val)
    if not parts:
        continue
    label = 'lineage_' + '_'.join(parts)
    FBbt = row['defined_class']
    yaml_lines.append(f'  - label: {label}\n')
    yaml_lines.append(f'    classes:\n')
    yaml_lines.append(f'      - {FBbt}\n')
    yaml_lines.append(f'      - RO:0002202 some {FBbt}\n')

yaml_lines.append(f'  - label: primary_neuron\n')
yaml_lines.append(f'    classes:\n')
yaml_lines.append(f'      - FBbt:00047097\n')
yaml_lines.append(f'  - label: secondary_neuron\n')
yaml_lines.append(f'    classes:\n')
yaml_lines.append(f'      - FBbt:00047096\n')

with open('lineage_neo_labels.yaml', 'w') as f:
    f.writelines(yaml_lines)
