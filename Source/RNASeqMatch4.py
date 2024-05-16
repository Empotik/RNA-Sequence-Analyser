# RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files.
# Developed by:
#   Puttisan Mukneam, Pitzer College
#       Majored in Data Science - Claremont McKenna College
#
#   Jeerakit Kanokthipphayakun, University of Colorado Boulder
#       Majored in Electrical and Computer Engineering - College of Engineering and Applied Science
#       Minored in Business - Leeds School of Business

# Licensed under the MIT license.

# Build 3.3

# Last updated on March 24, 2023 by Jeerakit Kanokthipphayakun.

import sqlite3
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Connect to database
conn = sqlite3.connect('gene_info.db')

# Create table to store gene information
conn.execute('''CREATE TABLE IF NOT EXISTS gene_info
             (GENE_ID TEXT PRIMARY KEY NOT NULL,
             GENE_NAME TEXT NOT NULL,
             LOG2FOLDCHANGE REAL NOT NULL);''')

# Insert sample gene information into the table
conn.execute("INSERT INTO gene_info (GENE_ID, GENE_NAME, LOG2FOLDCHANGE) VALUES ('gene1', 'Gene Name 1', 2.3)")
conn.execute("INSERT INTO gene_info (GENE_ID, GENE_NAME, LOG2FOLDCHANGE) VALUES ('gene2', 'Gene Name 2', -1.7)")
conn.execute("INSERT INTO gene_info (GENE_ID, GENE_NAME, LOG2FOLDCHANGE) VALUES ('gene3', 'Gene Name 3', 0.5)")
conn.execute("INSERT INTO gene_info (GENE_ID, GENE_NAME, LOG2FOLDCHANGE) VALUES ('gene4', 'Gene Name 4', -0.8)")

# Commit changes to the database
conn.commit()

# Get user input for gene ID and file directory
gene_id = input("Enter gene ID: ")
file_dir = input("Enter file directory: ")

# Search for gene ID in all files in directory
import os

for filename in os.listdir(file_dir):
    if filename.endswith(".txt"):
        try:
            with open(os.path.join(file_dir, filename), 'r') as f:
                for line in f:
                    if gene_id in line:
                        data = line.strip().split('\t')
                        log2foldchange = float(data[1])
                        print(f"{filename}: {log2foldchange}")
        except Exception as e:
            logging.error(f"Error reading file {filename}: {e}")

# Search for gene ID in database
try:
    cursor = conn.execute("SELECT GENE_NAME, LOG2FOLDCHANGE FROM gene_info WHERE GENE_ID=?", (gene_id,))
    for row in cursor:
        gene_name = row[0]
        log2foldchange = row[1]
        print(f"Database: {gene_name} ({log2foldchange})")
except Exception as e:
    logging.error(f"Error querying database: {e}")

# Close connection to database
conn.close()