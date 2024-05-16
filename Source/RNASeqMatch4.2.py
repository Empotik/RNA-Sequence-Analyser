# RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files.
# Developed by:
#   pmukneam, Pitzer College
#       Majored in Data Science - Claremont McKenna College
#
#   Empotik, University of Colorado Boulder
#       Majored in Electrical and Computer Engineering - College of Engineering and Applied Science

# Build 4.1
# Python 3.11.1

# Last updated on March 27, 2023 by Empotik.

# Import dependencies
import sqlite3
import pandas as pd
import atexit
import os
from typing import List, Tuple

# Set up database
conn = sqlite3.connect('gene_data.db')
c = conn.cursor()

# Register the clean-up function to be called when the program exits
@atexit.register
def clean_up():
    print("Cleaning up database")    
    if conn:
        conn.close() 
    delete_database()

def delete_database(): 
    try:
        os.remove("gene_data.db")        
        # Inform the user that the database has been deleted
        print("The database has been deleted.")  
    except OSError:
        pass    

def insert_gene_data(gene_id: str, file_name: str, log2foldchange: float) -> None:
    """Insert gene data into the database."""
    c.execute("INSERT INTO gene_info VALUES (?, ?, ?)", (gene_id, file_name, log2foldchange))
    conn.commit()

def search_gene_data(gene_id: str) -> List[Tuple[str, float]]:
    """Search for gene data in the database."""
    c.execute("SELECT DISTINCT file_name, log2foldchange FROM gene_info WHERE gene_id=?", (gene_id,))
    results = c.fetchall()
    return list(set(results))

def read_file(file_path: str, file_name: str) -> List[Tuple[str, float]]:
    """Read gene data from file and insert into database."""
    print(f"Reading file: {file_name}")
    gene_data = []
    try:
        df = pd.read_excel(file_path, usecols="A,D", order_by=["GeneID", "log2FoldChange"])
        gene_data = [(gene_id, log2foldchange) for gene_id, log2foldchange in zip(df["GeneID"], df["log2FoldChange"])]
        gene_data = [(gene_id.split('-')[1], log2foldchange) for gene_id, log2foldchange in gene_data]
        c.executemany("INSERT INTO gene_info VALUES (?, ?, ?)", [(gene_id, file_name, log2foldchange) for gene_id, log2foldchange in gene_data])
        conn.commit()
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"Error reading file {file_name}: {str(e)}")
    return gene_data

def terminal_ui_welcome():
    credit = '''MIT License

Copyright (c) 2023 Empotik

RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files
Developed by:
  pmukneam, Pitzer College
      Majored in Data Science - Claremont McKenna College

  Empotik, University of Colorado Boulder
      Majored in Electrical and Computer Engineering - College of Engineering and Applied Science

Build 4.2

Last updated on March 25, 2023 by Empotik.'''
    print(credit)
    print("------------------------------------------------------------------------")

def main():
    try:
        # Run the program
        terminal_ui_welcome()

        # Create gene_info table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS gene_info
                    (gene_id text, file_name text, log2foldchange real)''')
        
        # Add an index on the gene_id column for improved query performance
        c.execute("CREATE INDEX IF NOT EXISTS gene_id_index ON gene_info(gene_id)")
        conn.commit()

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
                    # Loop through all the data in ./input_data/
                    rootdir = './input_data/'
                    for subdir, dirs, file_names in os.walk(rootdir):
                        print(f'Found: {len(file_names)} file(s)')

                        # Read files and insert gene data into database
                        for file_name in file_names:
                            file_path = os.path.join(subdir, file_name)
                            read_file(file_path, file_name)

        print("Initialization successful\nReady for query")
        # Keep the program running until the user decides to exit
        while True:
            user_input = input("\nPress 'q' then Enter to quit, or press Enter to search: ")
            if user_input.lower() == 'q':   
                print("Exited by user")
                clean_up()
                raise SystemExit
            else:            
                # Search for gene data
                gene_id = input("Enter gene ID: ")
                gene_data_list = search_gene_data(gene_id)
                
                # Print results
                if gene_data_list:
                    print(f"Results for gene ID: {gene_id}:")
                    for gene_data in gene_data_list:
                        print(f"File: {gene_data[0]:15} Log2FoldChange: {gene_data[1]}")
                else:
                    print(f"No results found for gene ID {gene_id}")
    except KeyboardInterrupt:
        # Handle program cleanup before exiting
        clean_up()

if __name__ == '__main__':
    main()