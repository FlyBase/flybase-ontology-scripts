# simple script to find unused IDs within a specified range in an obo format ontology

# parameters
outfile = 'unused_ids.txt'
ontology_file = "" # path to ontology file
ontology_short = "FBbt"
id_range = range(51000,52999,1)
id_length = 8

# convert id_range to list strings with correct length
def id_extender(i,l):
	"""
	Extends a string 'i' by prefixing '0's to output a string of total length 'l'.
	'i' must not be longer than 'l' characters.
	"""
	padding = '0' * (l-len(i))
	new_i = padding + i
	return new_i

id_range_list = [id_extender(str(i), id_length) for i in id_range]

# list of lines in ontology file (without '\n')
with open(ontology_file, 'r') as f:
    ontology_lines = f.read().splitlines() 

# check whether each ID in the range is present as an ID in the file
unused_ids = []
for i in id_range_list:
	namespaced_id = "id: %s:%s" %(ontology_short,i)
	if namespaced_id not in ontology_lines:
		unused_ids.append("%s:%s" %(ontology_short,i))

if len(unused_ids) > 0:
	print('unused IDs found, saving to ' + outfile)

with open(outfile, 'w') as f:
    f.write('\n'.join(unused_ids))
