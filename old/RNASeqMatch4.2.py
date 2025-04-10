# RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files.
# Developed by:
#   pmukneam, Pitzer College
#       Majored in Data Science - Claremont McKenna College
#
#   Empotik, University of Colorado Boulder
#       Majored in Electrical and Computer Engineering - College of Engineering and Applied Science

# Build 4.2
# Python 3.11.1

# Last updated on March 27, 2023 by Empotik.

# Import dependencies
import sqlite3
import pandas as pd
import atexit
import os
from typing import List, Tuple
import natsort

# Set up database
conn = sqlite3.connect('gene_data.db')
c = conn.cursor()

# Register the clean-up function to be called when the program exits
@atexit.register
def clean_up():
    """Closes the database connection and deletes the database file if it exists."""  
    if conn:
        conn.close()
    if os.path.exists("gene_data.db"):
        delete_database()
    else:
        print("Clean up completed")

def delete_database():
    """Deletes the database file""" 
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
    """Searches for gene data in the database and returns a list of tuples containing the file name and log2foldchange for the gene."""
    try:
        c.execute("SELECT DISTINCT file_name, log2foldchange FROM gene_info WHERE gene_id=?", (gene_id,))
        rows = c.fetchall()

        # Sort the rows by file name and then by log2foldchange using natsort
        rows_sorted = natsort.natsorted(rows, key=lambda row: (row[0], row[1]))
        files_sorted = [row[0] for row in rows_sorted]
        log2foldchanges_sorted = [row[1] for row in rows_sorted]

        return list(zip(files_sorted, log2foldchanges_sorted))
    except Exception as e:
        print(f"Error getting data for gene {gene_id}: {str(e)}")
        return None

def read_file(file_path: str, file_name: str) -> List[Tuple[str, float]]:
    """Reads gene data from an Excel file, inserts it into the database, and returns a list of tuples containing the gene ID and log2foldchange for the gene."""
    print(f"Reading file: {file_name}")
    gene_data = []
    try:
        df = pd.read_excel(file_path, usecols="A,D")
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
    """Prints the application's credits and version information."""
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
    """The main function that initializes the application, creates the database table and index, reads data from Excel files in the input_data directory, and allows the user to search for gene data in the database. The function also includes a loop that keeps the program running until the user decides to exit. The loop prompts the user to enter a Gene ID to search for, and prints the results if any are found."""
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

        print("Initialization completed\nReady for query")
        # Keep the program running until the user decides to exit
        while True:
            user_input = input("\nPress 'q' then Enter to quit, or press Enter to search: ")
            if user_input.lower() == 'q':   
                print("Exited by user")
                clean_up()
                raise SystemExit
            else:            
                # Search for gene data
                gene_id = input("Enter Gene ID: Cluster-")
                gene_data_list = search_gene_data(gene_id)
                
                # Print results
                if gene_data_list:
                    print(f"Results for Gene ID: {gene_id}:")
                    for gene_data in gene_data_list:
                        print(f"File: {gene_data[0]:15} Log2FoldChange: {gene_data[1]}")
                else:
                    print(f"No results found for Cluster-{gene_id}")
    except KeyboardInterrupt:
        # Handle program cleanup before exiting
        clean_up()

if __name__ == '__main__':
    main()
