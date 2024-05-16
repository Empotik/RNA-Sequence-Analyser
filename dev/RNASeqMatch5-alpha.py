import re
import pandas as pd

# Read the file
with open('Top30_Log2FoldChange_Mar2023.txt', 'r') as file:
    data = file.readlines()

# Extract the required information
tx_pattern = re.compile(r'T\d+VsC\d+|T\d+vsC\d+')
c_pattern = re.compile(r'C\d+\.\d+')
unique_values = set()
values = {}
for line in data:
    line = line.strip()
    tx_matches = tx_pattern.findall(line)
    c_matches = c_pattern.findall(line)
    if tx_matches:
        for match in tx_matches:
            if match not in values:
                values[match] = []
            values[match].append('')
    elif c_matches:
        for match in c_matches:
            unique_values.add(match)
            for key in values:
                if key in line:
                    values[key].append(match)
    else:
        continue

# Create a dataframe and write to an Excel file
df = pd.DataFrame(columns=['Gene ID'] + list(values.keys()))

for i, value in enumerate(unique_values):
    row = [value]
    for key in values:
        if value in values[key]:
            row.append(key)
        else:
            row.append('')
    df.loc[i] = row

df.to_excel('output.xlsx', index=False)