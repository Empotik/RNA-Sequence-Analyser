# Load libaries
import pandas as pd
import os
import re

# Initialize dictionary
data_dict = {}

########################################################
def addDict(path, num ):
    # Read file
    file = pd.read_excel(path, usecols = "A")

    #Loop Through each row of the GeneID
    for index, row in file.iterrows():
        temp = row["GeneID"]
        if temp not in data_dict:
            data_dict[temp] = [num]
        else:
            data_dict[temp].append(num)

def printDict():
    for key in data_dict:
        val = data_dict[key]
        if len(val) > 1:
            val_sorted = sorted(val)
            print(f"{key:30}{val_sorted}")
#########################################################

# Loop through all the data in ./data/
rootdir = './data/'
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        path = os.path.join(subdir, file)
        n = re.findall("\d+", path)
        addDict(path, int(n[0]))

printDict()
