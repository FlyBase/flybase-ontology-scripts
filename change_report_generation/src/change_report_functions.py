import subprocess
import wget
import urllib
import urllib.error
import os
import oaklib
import re

class Parameters:
    """Object for storing parameters."""
    def __init__(self, ontology, new_date, old_date, new_release):
        self.outpath = None
        self.obo_namespace = None
        self.id_namespace = None
        self.ontology = ontology
        self.new_date = new_date
        self.old_date = old_date
        self.new_release = new_release

    def set_parameters(self):
        """Adds parameters that depend on which ontology being reported on to an existing Parameters object."""
        if self.ontology.lower() == 'fbbt':
            self.obo_namespace = "fly_anatomy.ontology"
            self.id_namespace = "FBbt"
            self.outpath = os.path.join(os.getcwd(), "fbbt_%s_metrics" % self.new_date)
            self.old_file = os.path.join(os.getcwd(), "old_fbbt-simple.obo")
            self.new_file = os.path.join(os.getcwd(), "new_fbbt-simple.obo")
        elif self.ontology.lower() == 'fbdv':
            self.obo_namespace = "FlyBase\ development\ CV"
            self.id_namespace = "FBdv"
            self.outpath = os.path.join(os.getcwd(), "fbdv_%s_metrics" % self.new_date)
            self.old_file = os.path.join(os.getcwd(), "old_fly_development.obo")
            self.new_file = os.path.join(os.getcwd(), "new_fly_development.obo")
        elif self.ontology.lower() == 'fbcv':
            self.obo_namespace = ""
            self.id_namespace = "FBcv"
            self.outpath = os.path.join(os.getcwd(), "fbcv_%s_metrics" % self.new_date)
            self.old_file = os.path.join(os.getcwd(), "old_flybase_controlled_vocabulary.obo")
            self.new_file = os.path.join(os.getcwd(), "new_flybase_controlled_vocabulary.obo")
        elif self.ontology.lower() == 'do':
            self.obo_namespace = "disease_ontology"
            self.id_namespace = "DOID"
            self.outpath = os.path.join(os.getcwd(), "do_%s_metrics" % self.new_date)
            self.old_file = os.path.join(os.getcwd(), "old_doid.obo")
            self.new_file = os.path.join(os.getcwd(), "new_doid.obo")
        else:
            print('Unrecognised ontology - aborting')
            raise SystemExit
        self.report_prefix = os.path.join(self.outpath, self.ontology + "_" + self.new_date)

    def get_ontology_from_github(self, new_old):
        """downloads the ontology file used in FlyBase for FBbt, FBcv, FBdv or DO from GitHub.
        FBbt releases before 2019-09-05 do not have /releases/ in the PURL."""
        if new_old.lower() == 'new':
            release_date = self.new_date
            filename = self.new_file
        elif new_old.lower() == 'old':
            release_date = self.old_date
            filename = self.old_file
        else:
            raise ValueError("new_old must be 'new' or 'old'")

        if self.ontology.lower() == 'fbbt':
            try:
                wget.download("http://purl.obolibrary.org/obo/fbbt/releases/%s/fbbt-simple.obo" % release_date
                              , filename)
            except urllib.error.HTTPError:
                wget.download("http://purl.obolibrary.org/obo/fbbt/%s/fbbt-simple.obo" % release_date
                              , filename)

        elif self.ontology.lower() == 'fbcv':
            if release_date == '2019-07-11':
                wget.download(("https://raw.githubusercontent.com/FlyBase/flybase-controlled-vocabulary/"
                               "811b916885b5214701dccfda0f4d43b9da4753f1/fbcv-flybase.obo"), filename)
            else:
                wget.download("http://purl.obolibrary.org/obo/fbcv/releases/%s/flybase_controlled_vocabulary.obo"
                              % release_date, filename)
        elif self.ontology.lower() == 'fbdv':
            wget.download("http://purl.obolibrary.org/obo/fbdv/releases/%s/fly_development.obo" % release_date
                          , filename)
        elif self.ontology.lower() == 'do':
            if release_date == '2021-06-08':
                wget.download("http://purl.obolibrary.org/obo/doid/releases/2021--6-08/doid.obo", filename)
            else:
                wget.download("http://purl.obolibrary.org/obo/doid/releases/%s/doid.obo" % release_date, filename)
        else:
            raise ValueError('Unrecognised ontology')


    def strip_xref_analog(self):
        """Remove xref_analog annotations from old and new files."""
        for f in [self.old_file, self.new_file]:
            with open(f, 'r') as file:
                lines = [line for line in file if not line.startswith('xref_analog')]
            with open(f, 'w') as file:
                for l in lines:
                    file.write(l)


    def find_new_terms(self):
        old_ont = oaklib.get_adapter(self.old_file)
        new_ont = oaklib.get_adapter(self.new_file)
        terms_in_old = list(old_ont.entities())
        terms_in_new = list(new_ont.entities())
        added_term_ids = [i for i in terms_in_new if (i not in terms_in_old) and (i.startswith(self.id_namespace))]
        added_terms = {k: new_ont.label(k) for k in added_term_ids}
        return added_terms



def update_scripts(scriptpath):
    """Delete existing scripts and redownload from fbbt repo."""
    for script in ["onto_metrics_calc.pl", "obo_def_comp.pl", "obo_track_new.pl"]:
        subprocess.run("rm %s" % os.path.join(scriptpath, script), shell=True)
        subprocess.run("rm %s" % os.path.join(scriptpath, "OboModel.pm"), shell=True)

        wget.download(("https://raw.githubusercontent.com/FlyBase/drosophila-anatomy-developmental-ontology/"
                       "master/tools/release_and_checking_scripts/releases/%s" % script),
                      os.path.join(scriptpath, script))
        wget.download(("https://raw.githubusercontent.com/FlyBase/drosophila-anatomy-developmental-ontology/"
                       "master/tools/perl_modules/releases/OboModel.pm"),
                      os.path.join(scriptpath, "OboModel.pm"))





def update_fbcv_namespaces(fbcv_file, namespace_file):
    # Parse the OBO file and collect namespaces only from non-obsolete term stanzas.
    with open(fbcv_file, 'r') as fh:
        text = fh.read()

    # Split into stanzas (separated by one or more blank lines)
    stanzas = [s.strip() for s in re.split(r'\n\s*\n', text) if s.strip()]

    namespaces = []
    for stanza in stanzas:
        # consider only term stanzas that contain a namespace declaration
        if 'namespace:' not in stanza:
            continue
        # skip stanzas marked obsolete
        if re.search(r'^\s*is_obsolete:\s*true\b', stanza, flags=re.M):
            continue
        # find all namespace lines in this stanza
        for m in re.finditer(r'^\s*namespace:\s*(.+)$', stanza, flags=re.M):
            ns = m.group(1).strip()
            # preserve order but avoid duplicates
            if ns not in namespaces:
                namespaces.append(ns)

    # ensure the canonical FlyBase miscellaneous CV is always present
    if 'FlyBase miscellaneous CV' not in namespaces:
        namespaces.append('FlyBase miscellaneous CV')

    # Put the canonical FlyBase miscellaneous CV at the top, then sort the rest
    others = [ns for ns in namespaces if ns != 'FlyBase miscellaneous CV']
    sorted_others = sorted(others, key=lambda s: s.lower())
    sorted_namespaces = ['FlyBase miscellaneous CV'] + sorted_others

    # Escape/format namespaces for output (special-case the FlyBase entry)
    namespace_list = []
    for ns in sorted_namespaces:
        if ns == 'FlyBase miscellaneous CV':
            x = 'FlyBase\\ miscellaneous\\ CV'
        else:
            x = ns.replace('_', '\\_')
        namespace_list.append(x)

    # save file
    with open(namespace_file, 'w') as f:
        for namespace in namespace_list:
            f.write(namespace + '\n')

