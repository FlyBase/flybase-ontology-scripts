import subprocess
import pandas as pd
import os
import change_report_functions as crf

# details of releases to look at
input_details = pd.read_csv(os.path.join(os.getcwd(), "input.tsv"), sep='\t')
if input_details.notnull()['new_fb_release'][0]:
    new_release = input_details['new_fb_release'][0]
else:
    new_release = ""
parameters = crf.Parameters(
    ontology=input_details['ontology'][0],
    new_date=input_details['new_date'][0],
    old_date=input_details['old_date'][0],
    new_release=new_release)
parameters.set_parameters()

subprocess.run("mkdir " + parameters.outpath, shell=True)

scriptpath = os.path.join(os.getcwd(), "perl_scripts")
if input_details['update_scripts'][0].lower() in ["y", "yes"]:
    crf.update_scripts(scriptpath)

# if no ontology file is present already, get one from github
if not os.path.isfile(parameters.old_file):
    parameters.get_ontology_from_github(new_old='old')
if not os.path.isfile(parameters.new_file):
    parameters.get_ontology_from_github(new_old='new')

# remove any xref_analog lines (oak can't seem to handle these)
parameters.strip_xref_analog()

if parameters.ontology.lower() == 'fbcv':
    fbcv_namespace_file = os.path.join(os.getcwd(), "fbcv_namespaces.txt")
    # optionally update fbcv_namespace
    if input_details['update_FBcv_namespaces'][0].lower() in ["y", "yes"]:
        crf.update_fbcv_namespaces(parameters.new_file, fbcv_namespace_file)

    namespace_list = []
    with open(fbcv_namespace_file, 'r') as f:
        for ln in f.readlines():
            namespace_list.append(ln.strip())

    # no of terms and definitions for each namespace
    output = pd.DataFrame(columns=["Namespace", "Defined", "Total", "%"])
    count = 0

    for i in namespace_list:
        number = str(count)
        try:
            subprocess.run("perl -I %s %s %s %s > "
                           "%s_%s_no_defs.tsv"
                           % (scriptpath, os.path.join(scriptpath, "onto_metrics_calc.pl"), i, parameters.new_file,
                              parameters.report_prefix, number), check=True, shell=True)
        except subprocess.CalledProcessError:
            print("onto_metrics_calc.pl could not process " + i + " namespace, probably no usage.")
            continue

        try:
            result = pd.read_csv("%s_%s_no_defs.tsv"
                                 % (parameters.report_prefix, number), sep='\t', index_col=False)
            result["Namespace"] = i
            output = pd.concat([output, result], ignore_index=True, sort=False)
        except pd.errors.EmptyDataError:
            print("Empty file created for " + i)
            pass
        subprocess.run("rm %s_%s_no_defs.tsv"
                       % (parameters.report_prefix, number), shell=True)
        count += 1

    # add total row
    total_dict = {"Namespace": ["Total"], "Defined": [output["Defined"].sum()], "Total": [output["Total"].sum()],
                  "%": [round(output["Defined"].sum() * 100 / output["Total"].sum(), 2)]}
    termcount = pd.DataFrame.from_dict(total_dict, orient='columns')

    output = pd.concat([output, termcount], ignore_index=True, sort=False)

    output.to_csv("%s_no_defs.tsv" % parameters.report_prefix, sep='\t', index=False)
else:
    # Count number of terms and percent defined (not fbcv)
    subprocess.run("perl -I %s %s %s %s > %s_no_defs.txt"
                   % (scriptpath, os.path.join(scriptpath, "onto_metrics_calc.pl"), parameters.obo_namespace, parameters.new_file,
                      parameters.report_prefix), shell=True)

    termcount = pd.read_csv("%s_no_defs.txt" % parameters.report_prefix, sep='\t', index_col=False)

# run obo_def_comp.pl, which shows new/changed definitions/comments
subprocess.run("perl -I %s %s %s %s > %s_def_com_chg.txt"
               % (scriptpath, os.path.join(scriptpath, "obo_def_comp.pl"), parameters.old_file, parameters.new_file,
                  parameters.report_prefix), shell=True)

# get number of new definitions
(out1, err1) = subprocess.Popen("grep -c 'new definition' %s_def_com_chg.txt" % parameters.report_prefix,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                shell=True).communicate()
ndef = out1.decode().rstrip('\n')

# get number of changed definitions
(out2, err2) = subprocess.Popen("grep -c 'changed definition' %s_def_com_chg.txt" % parameters.report_prefix,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                shell=True).communicate()
chdef = out2.decode().rstrip('\n')

# get number of new comments
(out3, err3) = subprocess.Popen("grep -c 'new comment' %s_def_com_chg.txt" % parameters.report_prefix,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                shell=True).communicate()
ncom = out3.decode().rstrip('\n')

# get number of changed comments
(out4, err4) = subprocess.Popen("grep -c 'changed comment' %s_def_com_chg.txt" % parameters.report_prefix,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                shell=True).communicate()
chcom = out4.decode().rstrip('\n')

# for name changes obsoletions and merges:
subprocess.run("perl -I %s %s %s %s > %s_name_obs_merge.txt"
               % (scriptpath, os.path.join(scriptpath, "obo_track_new.pl"), parameters.old_file, parameters.new_file,
                  parameters.report_prefix), shell=True)

# get number of name changes
(out5, err5) = subprocess.Popen("grep -c 'has changed name' %s_name_obs_merge.txt"
                                % parameters.report_prefix, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                shell=True).communicate()
num_namchg = out5.decode().rstrip('\n')

# get number of obsoletions
(out6, err6) = subprocess.Popen("grep -c 'has been made obsolete' %s_name_obs_merge.txt"
                                % parameters.report_prefix, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                shell=True).communicate()
num_obs = out6.decode().rstrip('\n')

# get number of new merges
(out7, err7) = subprocess.Popen("grep -c 'has been merged' %s_name_obs_merge.txt"
                                % parameters.report_prefix, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                shell=True).communicate()
num_merges = out7.decode().rstrip('\n')

# get name changes
(out8, err8) = subprocess.Popen("grep 'has changed name' %s_name_obs_merge.txt"
                                % parameters.report_prefix, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                shell=True).communicate()
namchg = out8.decode()

# get obsoletions
(out9, err9) = subprocess.Popen("grep 'has been made obsolete' %s_name_obs_merge.txt"
                                % parameters.report_prefix, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                shell=True).communicate()
obs = out9.decode()

# get merges
(out10, err10) = subprocess.Popen("grep 'has been merged' %s_name_obs_merge.txt"
                                  % parameters.report_prefix, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                  shell=True).communicate()
merges = out10.decode()

# new terms
new_terms = parameters.find_new_terms()

# put document together
file = open(os.path.join(parameters.outpath, "release_details_%s_%s.txt"
                         % (parameters.ontology, parameters.new_date)), "w")

if len(parameters.new_release) > 0:
    release_text = " in " + parameters.new_release
else:
    release_text = ""

file.write("Release details for new %s dated %s%s:\n\n"
           % (parameters.ontology, parameters.new_date, release_text))
file.write(str(termcount['%'][0]) + "% of terms now have a definition (" + str(termcount.Defined[0]) + "/" + str(
    termcount.Total[0]) + ")\n\n")
file.write("====\n\n")

file.write("Since last release (" + parameters.old_date + "):\n\n")
file.write(f"New terms: {len(new_terms)}\n")
file.write(f"Name changes: {num_namchg}\n")
file.write(f"Obsoletions: {num_obs}\n")
file.write(f"Merges: {num_merges}\n")
file.write(f"New definitions: {ndef}\n")
file.write(f"Changed definitions: {chdef}\n")
file.write(f"New comments: {ncom}\n")
file.write(f"Changed comments: {chcom}\n\n")
file.write("====\n\n")

file.write("Details of new terms, name changes, obsoletions and merges:\n\n")

file.write("New terms:\n")
if len(new_terms) <= 50:
    for t in new_terms.keys():
        file.write(f'{t} ; {new_terms[t]}\n')
    output_new_terms = False
else:
    file.write("More than 50 new terms, please see separate file.\n")
    output_new_terms = True


file.write("\nName changes:\n")
file.write(namchg + "\n")
file.write("Obsoletions:\n")
file.write(obs + "\n")
file.write("Merges:\n")
file.write(merges + "\n")

file.close()

if output_new_terms:
    with open(os.path.join(parameters.outpath,
                           "new_terms_%s_%s.tsv" % (parameters.ontology, parameters.new_date)), "w") as f:
        for t in new_terms.keys():
            f.write(f'{t}\t{new_terms[t]}\n')
