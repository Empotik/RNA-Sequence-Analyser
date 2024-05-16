# RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files.
# Developed by:
#   pmukneam, Pitzer College
#       Majored in Data Science - Claremont McKenna College
#
#   Empotik, University of Colorado Boulder
#       Majored in Electrical and Computer Engineering - College of Engineering and Applied Science
#       Minored in Business - Leeds School of Business

# Licensed under the MIT license.

# Build 3.3

# Last updated on March 24, 2023 by Empotik.

# Load libraries
import pandas as pd
import os
import re

# Initialize dictionary for gene ID
gene_id_dict = {}
# Initialize tmp arr 2 file
outchar = []

########################################################
def addDict(path, filename):
    # Read file at path only from columns A and D
    xaxis = pd.read_excel(path, usecols="A")
    yaxis = pd.read_excel(path, usecols="D")
    
    processed_files = set() #define as an empty set
    # check if filename has already been processed
    if filename not in processed_files:
        # Loop through each row of the GeneID
        for index, row in xaxis.iterrows():
            temp_x = row["GeneID"]  # temp_x is GeneID e.g. Cluster-00000.00000
            temp_y = yaxis.iloc[index, 0]  # temp_y is log2FoldChange e.g. xx
            if temp_x not in gene_id_dict:
                gene_id_dict[temp_x] = [[filename, temp_y]]  # {'Cluster-00000.00000': [['T0', xx]]}
            else:
                gene_id_dict[temp_x].append([filename, temp_y])
        
        # mark filename as processed        
        filename = filename.replace("'", "")
        processed_files.add(filename)
        print(f'Loaded: {filename}')

def analyzeDict():
    print('Analyzing...')
    for key in sorted(gene_id_dict.keys()):  # sort keys alphabetically and numerically. The keys are GeneID e.g. Cluster-00000.00000, Cluster-00000.00001, Cluster-00000.00002,... 
        x_val = [i[0] for i in gene_id_dict[key]]  # x_val is list of filenames in the translation of Cluster-00000.00000 e.g. ['T0', 'T1', ...]
        y_val = [i[1] for i in gene_id_dict[key]]
        if len(x_val) >= 1:
            x_val_sorted = sorted(x_val, key=lambda x: (int(re.search(r'\d+', x).group()), x))
            y_val_sorted = [y for _, y in sorted(zip(x_val, y_val), key=lambda pair: pair[0])]
            list_str = str(re.findall(r"'([^']+)'", str(x_val_sorted)))[1:-1]
            list_str = list_str.replace("'", "")  # replace single quotes with commas
            outchar.append(f"{key:25}{list_str:20}{y_val_sorted}\n")
    print('Analysis completed')

def print2file():
    print('Preparing results.txt')
    with open(r"results.txt", "w") as outfile:
        outfile.write("********************Beginning of report*********************\n")
        outfile.write(f"{'Gene ID':25}{'Found in filename':20}{'log2FoldChange'}\n")
        outfile.writelines(outchar)
        outfile.write("***********************End of report***********************\n")
    print('Successfully exported results.txt')

def terminal_ui():
    credit = '''RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files
Developed by:
  Puttisan Mukneam, Pitzer College
      Majored in Data Science - Claremont McKenna College

  Empotik, University of Colorado Boulder
      Majored in Electrical and Computer Engineering - College of Engineering and Applied Science
      Minored in Business - Leeds School of Business

Licensed under the MIT license.

Build 3.0

Last updated on March 24, 2023 by Empotik.'''
    print(credit)
    print("------------------------------------------------------------------------")

    # checking if the directory input_data exist or not.
    if not os.path.exists('./input_data/'):
        # if the input_data directory is not present, create it.
        print("'input_data' directory was not found\nPlease refer to Project Manual.pdf for more information")
        os.makedirs("./input_data/")
        print("Directory 'input_data' has been automatically made\nPlease try again later\nExited with error\n")
        input("Press Enter to exit...")
        raise SystemExit

    else:
        # check if there is some file exist in the input_data directory
        with os.scandir('./input_data/') as it:
            if not any(it):
                print("No file detcted in 'input_data' directory\nPlease refer to Project Manual.pdf for more information\nExited with error\n")
                input("Press Enter to exit...")
                raise SystemExit
        
            else:
                print('Matching start')
                # Loop through all the data in ./input_data/
                rootdir = './input_data/'
                for subdir, dirs, files in os.walk(rootdir):
                    print(f'Found: {len(files)} file(s)')
                    for file in files:
                        path = os.path.join(subdir, file)
                        filename = str(re.findall(r"^([^.]*).*"  , file))[1:-1]#comment out for extension
                        addDict(path, filename)
def main():
    terminal_ui()
    analyzeDict()
    print2file()
    print('Matching completed')
    input("Press Enter to exit...")

main()