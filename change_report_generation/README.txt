Scripts for comparing releases of FlyBase ontologies (and the Disease Ontology)
Runs perl scripts located at:
https://raw.githubusercontent.com/FlyBase/drosophila-anatomy-developmental-ontology/master/tools/release_and_checking_scripts/releases/

Prepares a report showing the number of terms and changed names, definitions, comments and obsoletions.

Fill in the details of releases in the src/input.tsv file:
REQUIRED FIELDS
ontology is one of 'FBbt', 'FBdv', 'FBcv' or 'DO' (case insensitive, but will appear on report as written in file)
new_date is the date the newer file was released (found in obo file header - YYYY-MM-DD format)
old_date is the date the older file was released (found in obo file header - YYYY-MM-DD format)

OPTIONAL FIELDS
new_release is the release/epicycle that the new file was loaded into FlyBase (e.g. FB_2020_02_EP6) update_scripts can trigger re-downloading perl scripts from the FBbt repo, default is no, 'yes' or 'y' will update update_FBcv_namespaces can trigger an update of FBcv namespace list (if ontology is fbcv), default is no, 'yes' or 'y' will update

If the ontology is not available to download from GitHub (too old), you can copy the file to this folder with the filename appended by 'new_' or 'old_' (e.g. 'old_fly_anatomy.obo'). An existing file here will be used instead of trying to download a file, so delete any of these files if you want new ones to be downloaded.