# Application for analyzing RNA Sequence recorded in form of exel (.xls or .xsls)
# Developed by  Puttisan "Ninja" Mukneam 
#               Maj. Data Science - Claremont Mckenna College
#               Pitzer College
#          and  Jeerakit "Jay" Kanokthipphayakun
#               Maj. Electical and Computer Engineering - College of Engineering and Applied Science 
#               Min. Business - LEEDs School of Business
#               University of Colorado Boulder
# Licensed under MIT license
# Build 2.1
# Feb 6, 2023

# Load libaries
import pandas as pd
import os
import re

# Initialize dictionary for gene ID
gene_id_dict = {}
# Initialize dictionary for value stored in column D
value_list = []
# Initialize tmp arr 2 file
outchar = []

########################################################
def addDict(path, filename):
    # Read file at path only from colums A
    xaxis = pd.read_excel(path, usecols = "A")
    yaxis = pd.read_excel(path, usecols = "D")

    #Loop through each row of the GeneID
    for index, row in xaxis.iterrows():     
        temp_x = row["GeneID"]#temp_x is GeneID eg. Cluster-00000.00000
        temp_y = yaxis[row]#temp_y is log2FoldChange eg. xx
        if temp_x not in gene_id_dict:
            gene_id_dict[temp_x] = [filename, temp_y]#{'Cluster-00000.00000': [T0, xx]}
        else:
            gene_id_dict[temp_x].append([filename, temp_y])     
        print(f'Loaded: {filename}')

def analyzetDict():
    print('Analyzing...')
    for key in gene_id_dict: #key is GeneID eg. Cluster-00000.00000
        x_val = gene_id_dict[key][0] #x_val is filename in the translation of Cluster-00000.00000 eg T0
        y_val = gene_id_dict[key][1]
        if len(x_val) >= 1:
            x_val_sorted = sorted(x_val)
            y_val_sorted = sorted(y_val)
            list_str = str(re.findall(r"'([^']+)'", str(x_val_sorted)))[1:-1]      
            outchar.append(f"{key:25}{list_str:20}{y_val_sorted}\n")
            #outchar.append(f"{key:30}{ast.literal_eval(list_str)}\n")
            #print(list_str)
    print('Analyzation completed')

def print2file():
    print('Preparing results.txt')
    with open(r"results.txt", "w") as outfile:
        outfile.write("********************Begining of report*********************\n")
        outfile.writelines(outchar)
        outfile.write("***********************End of report***********************\n")
    print('Successfully exported results.txt')

def main():
    # checking if the directory input_data exist or not.
    if not os.path.exists('./input_data/'):       
        # if the input_data directory is not present, create it.
        print("'input_data' directory was not found\nPlease refer to README.txt for more information")
        os.makedirs("./input_data/")
        print("Directory 'input_data' has been automatically made\nPlease try again later\nExited with error\n")
        input("Press any key to exit...")
        raise SystemExit

    else:
        # check if there is some file exit in the input_data directory
        with os.scandir('./input_data/') as it:
            if not any(it):
                print("No file detcted in 'input_data' directory\nPlease refer to README.txt for more information\nExited with error\n")
                input("Press any key to exit...")
                raise SystemExit
        
            else:
                print('Matching start')
                # Loop through all the data in ./data/
                rootdir = './input_data/'
                for subdir, dirs, files in os.walk(rootdir):
                    print(f'Found: {len(files)} file(s)')
                    for file in files:
                        path = os.path.join(subdir, file)
                        filename = str(re.findall(r"^([^.]*).*"  , file))[1:-1]#comment out for extension
                        addDict(path, filename)
    analyzetDict()
    print2file()
    print('Matching completed')
    input("Press any key to exit...")

main()