# RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files.
# Developed by:#
#   Empotik, University of Colorado Boulder
#       Majored in Electrical and Computer Engineering - College of Engineering and Applied Science

# Build 5.0
# Python 3.11.1

# Last updated on March 29, 2023.

# Import dependencies
import sqlite3
import pandas as pd
import os
from typing import List, Tuple
import natsort
import re
import time
import shutil
import signal
import sys

# Define directory name
input_directory='./input_data/'
output_directory='./output_data/'
temp_directory='./temp/'

# Define file name
database_name='gene_data.db'

# Define database gloval variables
conn = None
c = None

def handler(signum, frame):
    """
    Signal handler function that gets called when the program receives a signal. Calls the `clean_up()` function to perform cleanup tasks, and then exits the program.

    Parameters:
        signum (int): The signal number that triggered the handler.
        frame (object): The current stack frame.

    Returns:
        None.
    """

    print(f"Received signal {signum}, cleaning up...")
    clean_up()
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)

def print_dynamic_line(text='', style='-'):
    """
    Prints a line of dashes that fits the current terminal width, followed by the given text centered within the line.

    Parameters:
        text (str): The text to be centered within the line.

    Returns:
        None
    """
    terminal_width = shutil.get_terminal_size().columns
    line_width = terminal_width - len(text)
    left_style= style * (line_width // 2)
    right_style = style * (line_width - len(left_style))
    line = left_style + text + right_style
    print(line)

def setup_database():
    """
    Sets up a SQLite database for storing gene information.

    Parameters:
        None

    Returns:
        None
    """
    global conn, c
    global database_path
    database_path = os.path.join(temp_directory,  database_name)
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    print(f"{database_name} has been created")
    # Create gene_info table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS gene_info
                (gene_id text, file_name text, log2foldchange real)''')
    
    # Add an index on the gene_id column for improved query performance
    c.execute("CREATE INDEX IF NOT EXISTS gene_id_index ON gene_info(gene_id)")
    conn.commit()

def clean_up():
    """
    Closes the database connection and deletes the database file if it exists.

    Parameters:
        None

    Returns:
        None
    """    
    print_dynamic_line('Cleaning up...')
    if conn:
        conn.close()
        print('Disconnecting from the database')

    if os.path.exists(temp_directory):
        # Delete the temporary directory
        shutil.rmtree(temp_directory, ignore_errors=True)     
        print("All temporary files has been deleted.")  
    print_dynamic_line('Done cleaning up')

def wait(waittime: int) -> None:
    """
    Function to display a progress bar to the user for the given amount of time.

    Parameters:
        waittime (int): The amount of time to display the progress bar (in seconds).

    Returns:
        None
    """
    start_time = time.time()
    while time.time() - start_time < waittime:
        for char in '/-\|':
            print(f'\b{char}', end='', flush=True)
            time.sleep(0.1)

def precheck_source() -> bool:
    """
    Function to check if the input and output directories and files required for the application exist.

    Parameters:
        None

    Returns:
        continue_with_automatch (bool): A boolean indicating whether to continue with the auto-matching feature or not.
    """
    continue_with_automatch = True
    # checking if the directories input_data and output_data exist or not.
    if not os.path.exists(input_directory): 
        # if the input_data directory is not present, create it.
        print(f"{input_directory} or {output_directory} directory was not found\nPlease refer to Project Manual.pdf for more information")
        if not os.path.exists(input_directory):
            os.makedirs(input_directory)
            print(f"Directory {input_directory} has been automatically made")
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
                        return continue_with_automatch
                    elif user_input.lower() in ['no', 'n']:
                        print(f"Move or copy your TopX_Log2FoldChange_DATE.txt file into {input_directory} and try again later")
                        input("Press Enter to exit...")
                        raise SystemExit
                    else:
                        print("Invalid input...")            
            else:
                print(f'Adding excel file(s) in {input_directory} into database')
                for subdir, dirs, file_names in os.walk(input_directory):
                    excel_files = [file_name for file_name in file_names if file_name.endswith('.xlsx') or file_name.endswith('.xls')]
                    print(f'Found {len(excel_files)} Excel file(s)')

                    for file_name in excel_files:
                        file_path = os.path.join(subdir, file_name)
                        read_file(file_path, file_name)
                        print(f"Added {file_name} into database")
    return continue_with_automatch

def insert_gene_data(gene_id: str, file_name: str, log2foldchange: float) -> None:
    """
    Inserts the gene data into the database.

    Parameters:
        gene_id (str): Gene ID for the gene being inserted.
        file_name (str): Name of the file where the gene data was read from.
        log2foldchange (float): Log2FoldChange value for the gene.

    Returns:
        None
    """
    c.execute("INSERT INTO gene_info VALUES (?, ?, ?)", (gene_id, file_name, log2foldchange))
    conn.commit()

def search_gene_data(gene_id: str) -> List[Tuple[str, float]]:
    """
    Searches the database for the gene data and returns a list of tuples containing the file name and Log2FoldChange value.

    Parameters:
        gene_id (str): Gene ID for the gene being searched.

    Returns:
        List[Tuple[str, float]]: A list of tuples containing the file name and Log2FoldChange value for the gene.
    """   
    try:
        gene_id_form = re.findall(r'(?:[C|c]luster-)?(\d+\.\d+)', gene_id)[-1]
        print_dynamic_line('','+')
        print(f"Gene ID being used to search database: {gene_id_form}")
        c.execute("SELECT DISTINCT file_name, log2foldchange FROM gene_info WHERE gene_id=?", (gene_id_form,))
        rows = c.fetchall()

        rows_sorted = natsort.natsorted(rows, key=lambda row: (row[0], row[1]))
        files_sorted = [row[0] for row in rows_sorted]
        log2foldchanges_sorted = [row[1] for row in rows_sorted]
        gene_data_list = list(zip(files_sorted, log2foldchanges_sorted))

        # Print results
        if gene_data_list:
            print(f"Result(s) for Cluster-{gene_id_form}:")
            for gene_data in gene_data_list:
                print(f"File: {gene_data[0]:15} Log2FoldChange: {gene_data[1]}")
        else:
            print(f"No results found for Cluster-{gene_id_form}")

        return gene_data_list

    except Exception as e:
        print(f"Exception: {e}")
        print(f"Error getting data for gene {gene_id}: {str(e)}")
        return None

def read_file(file_path: str, file_name: str) -> List[Tuple[str, float]]:
    """
    Reads the gene data from an Excel file, inserts it into the database, and returns a list of tuples containing the gene ID and Log2FoldChange value.

    Parameters:
        file_path (str): Path to the Excel file containing the gene data.
        file_name (str): Name of the file containing the gene data.

    Returns:
        List[Tuple[str, float]]: A list of tuples containing the gene ID and Log2FoldChange value for the gene.
    """    
    print(f"Reading {file_name}")
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
    """
    Automatically matches the TXT files in the input directory and extracts the required information from them.

    Parameters:
        None

    Returns:
        None
    """
    print_dynamic_line('Automatic matching start')
    
    # Find all TXT files in input directory and read
    txt_files = [f for f in os.listdir(input_directory) if f.endswith('.txt')]
    
    # Only one TXT file found, read from that file
    if len(txt_files) == 1:
        print(f"Reading from {txt_files}")
        txt_index = 0

    # Multiple TXT files found, prompt the user to select a file to read from
    else:
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

    # Set output filename according to the txt file used to search the match
    auto_match_output_filename = txt_files[txt_index]
    base_name, ext = os.path.splitext(auto_match_output_filename)
    new_ext = '.xlsx'
    auto_match_output_filename = base_name + new_ext

    # Extract the required information
    vs_pattern = re.compile(r'T\d+VsC\d+|T\d+vsC\d+|t\d+vsC\d+|T\d+vsc\d+|t\d+vs\d+')
    c_pattern = re.compile(r'C\d+\.\d+')
    unique_c_values = set()
    unique_vs_values = set()
    values = {}
    for line in data:
        line = line.strip()
        vs_matches = vs_pattern.findall(line)
        c_matches = c_pattern.findall(line)
        if vs_matches:
            for match in vs_matches:
                unique_vs_values.add(match)
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
    unique_c_values = natsort.natsorted(unique_c_values, key=lambda x: float(re.findall(r'\d+\.\d+', x)[0]) if re.findall(r'\d+\.\d+', x) else float('inf'), alg=natsort.REAL)
    unique_vs_values = natsort.natsorted(unique_vs_values, key=lambda x: float(re.findall(r'\d+', x)[0]), alg=natsort.REAL)  
    
    # Create a dataframe
    df = pd.DataFrame(columns=['Gene ID'] + list(unique_vs_values))

    # Make sure number of columns matches length of unique_vs_values
    if len(df.columns) != len(unique_vs_values) + 1:
        print(f"Number of columns ({len(df.columns)}) does not match length of unique_vs_values ({len(unique_vs_values)})")
        return

    # Loop over unique c values (each represents a gene)
    for c_number in sorted(unique_c_values):
        # Create a new row with the c value
        row = [c_number]
        
        # Add empty cells to the row until it has the same number of cells as unique vs values + 1 (for the c value column)
        while len(row) < len(unique_vs_values) + 1:
            row.append('')

        # Search for gene data in the database
        gene_data_list = search_gene_data(c_number)

        # If gene data is found, loop over unique vs values (each represents a sample)
        if gene_data_list:
            for file_name in unique_vs_values:
                # Initialize a variable to keep track of whether a match has been found
                match_found = False
                
                for gene_data in gene_data_list:
                    # Extract the file name and log2foldchange from the gene data
                    gene_file, gene_log2foldchange = gene_data
                                            
                    # Remove the file extension from the file name
                    gene_file = os.path.splitext(gene_file)[0]
                    
                    # If the gene file name is a match for the current sample
                    if gene_file == file_name:
                        
                        # Determine the index of the current sample in the row
                        col_index = list(unique_vs_values).index(file_name) + 1
                        
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
                    col_index = list(unique_vs_values).index(file_name) + 1
                    row += [''] * (col_index - len(row))
                    row[col_index] = ''
        
        # Append the row to the DataFrame
        df = pd.concat([df, pd.DataFrame([row], columns=df.columns)], ignore_index=True)


    # Write the dataframe to an Excel file
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file_path = os.path.join(output_directory, auto_match_output_filename)
    while True:
        try:
            df.to_excel(output_file_path, index=False)
            print(f"{auto_match_output_filename} has been generated in {output_directory}")
            break
        except PermissionError:
            cancle=input(f"Error: Permission denied to write to {output_file_path}. If you have other applications using {auto_match_output_filename}, close them so the file can be written to\nWaiting for 5 seconds before trying again...")
            
            wait(5)
    print_dynamic_line('Automatic matching completed')

def manual_match():
    """
    Function for manual gene ID search.
    
    Parameters:
        None

    Returns:
        None
    """
    print_dynamic_line('Manual matching start')
    # Search for gene data
    gene_id = input("Enter Gene ID: ")
    search_gene_data(gene_id)
    print_dynamic_line('Manual matching completed')

def initialization():
    """
    Initializes the application, creates the database table and index, and performs a precheck of the source.
    
    Parameters:
        None

    Returns:
        bool: Whether to continue with auto match or not.
    """
    
    welcome()
    setup_database()
    
    continue_with_automatch = precheck_source()

    print("Initialization completed\nReady for query")
    print_dynamic_line()
    return continue_with_automatch

def welcome():
    """
    Initializes the application, creates the database table and index, and performs a precheck of the source.
    
    Parameters:
        None

    Returns:
        bool: Whether to continue with auto match or not.
    """
    welcome = '''
RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files v5.0-March 29, 2023.
Spacifically made for Laboratory 2903, 9th floor, Science Complex Building 2 (SCB2), Faculty of Science, Chiang Mai University, Thailand.
For more information, please visit https://github.com/Empotik/Bio-RNA-seq-analysis
Thank you for using the application!'''
    print(welcome)
    print_dynamic_line('Empotik')

def main():
    """
    Prints the application's credits and version information.
    
    Parameters:
        None

    Returns:
        None
    """
    try:
        continue_with_automatch = initialization()
        # Keep the program running until the user decides to exit
        while True:
            if not continue_with_automatch:
                user_input = input("[M]anual search\n[Q]uit\nPlease make a selection:")
            else:
                user_input = input("1. [A]uto match and export output as an exel (.xlsx) file\n2. [M]anual search\n3. [Q]uit\nPlease make a selection:")
                
                if user_input.lower() in ['q', '3']:
                    raise SystemExit
                elif user_input.lower() in ['a', '1'] and continue_with_automatch:
                    auto_match()
                elif user_input.lower() in ['m', '2']:
                    manual_match()
                else:
                    print("Invalid selection, try again")
    except KeyboardInterrupt:
        print("Interrupted by user.")            
    finally:
        # Handle program cleanup before exiting regardless of the reason
        clean_up()

if __name__ == '__main__':
    main()