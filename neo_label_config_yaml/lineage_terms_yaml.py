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
for nomenclature_col in ['ito_lee', 'hartenstein', 'primary', 'secondary']:
    for i in lineage_df[lineage_df[nomenclature_col].notna()].index:
        label = 'lineage_' + lineage_df[nomenclature_col][i]
        FBbt = lineage_df['defined_class'][i]
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
