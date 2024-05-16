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
import re
import time

# Define input and output directory
input_directory='./input_data/'
output_directory='./output_data/'

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

def wait(waittime: int) -> None:
    start_time = time.time()
    while time.time() - start_time < waittime:
        for char in '/-\|':
            print(f'\b{char}', end='', flush=True)
            time.sleep(0.1)

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

def auto_match():
    # Find all TXT files in input directory and read
    txt_files = [f for f in os.listdir(input_directory) if f.endswith('.txt')]

    if len(txt_files) == 1:
        print(f"Reading from {txt_files}")
        # Only one TXT file found, read from that file
        with open(os.path.join(input_directory, txt_files[0]), 'r') as file:
            data = file.readlines()
    else:
        # Multiple TXT files found, prompt the user to select a file to read from
        print(f"Found {len(txt_files)} TXT files in {input_directory}:")
        for i, txt_file in enumerate(txt_files):
            print(f"{i + 1}. {txt_file}")
        while True:
            user_input = input("Which TXT file do you want to read from? (Enter a number): ")
            try:
                txt_index = int(user_input) - 1
                if txt_index < 0 or txt_index >= len(txt_files):
                    print("Invalid input. Please enter a valid number.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")
        with open(os.path.join(input_directory, txt_files[txt_index]), 'r') as file:
            data = file.readlines()

    # Extract the required information
    tx_pattern = re.compile(r'T\d+VsC\d+|T\d+vsC\d+')
    c_pattern = re.compile(r'C\d+\.\d+')
    unique_c_values = set()
    unique_tx_values = set()
    values = {}
    for line in data:
        line = line.strip()
        tx_matches = tx_pattern.findall(line)
        c_matches = c_pattern.findall(line)
        if tx_matches:
            for match in tx_matches:
                unique_tx_values.add(match)
                if match not in values:
                    values[match] = []
        elif c_matches:
            for match in c_matches:
                unique_c_values.add(match)
                for key in values:
                    if key in line:
                        values[key].append(match)
        else:
            continue

    # Sort unique_c_values with natsort
    unique_c_values = natsort.natsorted(unique_c_values, key=lambda x: float(re.findall(r'\d+', x)[0]), alg=natsort.REAL)
    unique_tx_values = natsort.natsorted(unique_tx_values, key=lambda x: float(re.findall(r'\d+', x)[0]), alg=natsort.REAL)

    # Create a dataframe
    df = pd.DataFrame(columns=['Gene ID'] + list(unique_tx_values))

    # Make sure number of columns matches length of unique_tx_values
    if len(df.columns) != len(unique_tx_values) + 1:
        print(f"Number of columns ({len(df.columns)}) does not match length of unique_tx_values ({len(unique_tx_values)})")
        return

    # Loop over unique c values (each represents a gene)
    for c_number in sorted(unique_c_values):
        # Create a new row with the c value
        row = [c_number]
        
        # Add empty cells to the row until it has the same number of cells as unique tx values + 1 (for the c value column)
        while len(row) < len(unique_tx_values) + 1:
            row.append('')
            
        # Extract the gene ID from the c value using a regular expression
        gene_id_match = re.compile(r'C(\d+\.\d+|\d+)').search(c_number)
        if gene_id_match:
            gene_id = gene_id_match.group(1)
            
            # Search for gene data in the database
            gene_data_list = search_gene_data(gene_id)
            
            ###debug
            print(f"Gene ID being used to search database: {gene_id} ")
            ###debug

            # If gene data is found, loop over unique tx values (each represents a sample)
            if gene_data_list:
                for file_name in unique_tx_values:
                    # Initialize a variable to keep track of whether a match has been found
                    match_found = False
                    
                    for gene_data in gene_data_list:
                        # Extract the file name and log2foldchange from the gene data
                        gene_file, gene_log2foldchange = gene_data
                                                
                        # Remove the file extension from the file name
                        gene_file = os.path.splitext(gene_file)[0]
                        
                        # If the gene file name is a match for the current sample
                        if gene_file == file_name:
                            
                            # Debugging line to print the file name and log2foldchange for each gene/sample pair
                            print(f"File: {file_name:15} Log2FoldChange: {gene_log2foldchange}")

                            # Determine the index of the current sample in the row
                            col_index = list(unique_tx_values).index(file_name) + 1
                            
                            # Set the corresponding cell in the row to the log2foldchange value
                            row[col_index] = gene_log2foldchange
                            
                            # Mark that a match has been found
                            match_found = True
                                                        
                            # Break out of the inner loop (since each file name should only match one gene)
                            break
                    
                    # If no match was found for the current sample
                    if not match_found:
                        # Add empty cells to the row until it has the same number of cells as the current sample index
                        # Then set the cell at the current sample index to an empty string
                        col_index = list(unique_tx_values).index(file_name) + 1
                        row += [''] * (col_index - len(row))
                        row[col_index] = ''
        
        # Append the row to the DataFrame
        df = df.append(pd.Series(row, index=df.columns), ignore_index=True)


    # Write the dataframe to an Excel file
    output_file_path = os.path.join(output_directory, 'output.xlsx')
    while True:
        try:
            df.to_excel(output_file_path, index=False)
            print(f"output.xlsx has been generated in {output_directory}")
            break
        except PermissionError:
            print(f"Error: Permission denied to write to {output_file_path}. If you have other application using output.xlsx, close it can be written to\nWaiting for 5 seconds before trying again...")
            wait(5)

def manual_match():
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

        # Initialize flag
        continue_with_automatch = True

        # checking if the directories input_data and output_data exist or not.
        if not os.path.exists(input_directory) or not os.path.exists(output_directory):
            # if the input_data directory is not present, create it.
            print(f"{input_directory} or {output_directory} directory was not found\nPlease refer to Project Manual.pdf for more information")
            if not os.path.exists(input_directory):
                os.makedirs(input_directory)
                print(f"Directory {input_directory} has been automatically made")
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
                print(f"Directory {output_directory} has been automatically made")
            print("Please try again later\nExited with error\n")
            input("Press Enter to exit...")
            raise SystemExit

        else:
            # check if there is at least one exel file and at least one txt file exist in the input_data directory
            with os.scandir(input_directory) as it:
                excel_file_exists = False
                txt_file_exists = False
                for entry in it:
                    if entry.name.endswith('.xls') or entry.name.endswith('.xlsx'):
                        excel_file_exists = True
                    elif entry.name.endswith('.txt'):
                        txt_file_exists = True
                if not excel_file_exists:
                    print(f"No Excel file detected in {input_directory}")
                    input("Press Enter to exit...")
                    raise SystemExit
                elif not txt_file_exists:
                    print(f"No TXT file detected in {input_directory}")
                    while True:
                        user_input = input("Do you want to continue without TXT file? This means that auto-matching feature will be diabled (y/n): ")
                        if user_input.lower() in ['yes', 'y']:
                            continue_with_automatch = False
                            break
                        elif user_input.lower() in ['no', 'n']:
                            print(f"Move or copy your TopX_Log2FoldChange_DATE.txt file into {input_directory} and try again later")
                            input("Press Enter to exit...")
                            raise SystemExit
                        else:
                            print("Invalid input...")            
                else:
                    # Loop through all the data in {input_directory}
                    print(f'Adding excel file(s) in {input_directory} into database')
                    for subdir, dirs, file_names in os.walk(input_directory):
                        # Exclude non-Excel files
                        excel_files = [file_name for file_name in file_names if file_name.endswith('.xlsx') or file_name.endswith('.xls')]
                        print(f'Found: {len(excel_files)} Excel file(s)')

                        # Read Excel files and insert gene data into database
                        for file_name in excel_files:
                            file_path = os.path.join(subdir, file_name)
                            read_file(file_path, file_name)

        print("Initialization completed\nReady for query")
        # Keep the program running until the user decides to exit
        while True:
            if not continue_with_automatch:
                user_input = input("\nPress Enter to search:\nPress 'Q' then Enter to quit\n")

            else:
                user_input = input("\nPress Enter to search:\nPress 'A' then Enter to auto match and export output as an exel (.xlsx) file\nPress 'Q' then Enter to quit\n")
                if user_input.lower() == 'q':   
                    print("Exited by user")
                    clean_up()
                    raise SystemExit
                elif user_input.lower() == 'a' and continue_with_automatch:
                    print("Auto-matching start")
                    auto_match()
                elif user_input.lower() == '':            
                    manual_match()
    except KeyboardInterrupt:
        # Handle program cleanup before exiting
        clean_up()

if __name__ == '__main__':
    main()
