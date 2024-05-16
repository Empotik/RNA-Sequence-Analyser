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
auto_match_output_filename='output.xlsx'

# Define database gloval variables
conn = None
c = None

def handler(signum, frame):
    print(f"Received signal {signum}, cleaning up...")
    clean_up()
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)

def print_dynamic_line(text):

    terminal_width = shutil.get_terminal_size().columns
    line_width = terminal_width - len(text)
    left_dashes = '-' * (line_width // 2)
    right_dashes = '-' * (line_width - len(left_dashes))
    line = left_dashes + text + right_dashes
    print(line)

def setup_database():

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
    
    print_dynamic_line('Cleaning up...')
    if conn:
        conn.close()
        print('Disconnecting from the database')

    if os.path.exists(temp_directory):
        # Delete the temporary directory
        shutil.rmtree(temp_directory, ignore_errors=True)     
        print("All temporary files has been deleted.")  
    print_dynamic_line('Done cleaning up')

def wait(waittime: int, animation: str = '/-\|') -> None:
    start_time = time.time()
    i = 0
    while time.time() - start_time < waittime:
        print(f'\b{animation[i]}', end='', flush=True)
        i = (i + 1) % len(animation)
        time.sleep(0.1)

def precheck_source() -> bool:

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

    c.execute("INSERT INTO gene_info VALUES (?, ?, ?)", (gene_id, file_name, log2foldchange))
    conn.commit()

def search_gene_data(gene_id: str) -> List[Tuple[str, float]]:
    
    try:
        gene_id_form = re.findall(r'(?:[C|c]luster-)?(\d+\.\d+)', gene_id)[-1]

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

    print_dynamic_line('Automatic matching start')
    txt_files = [f for f in os.listdir(input_directory) if f.endswith('.txt')]

    if len(txt_files) == 1:
        print(f"Reading from {txt_files}")
        with open(os.path.join(input_directory, txt_files[0]), 'r') as file:
            data = file.readlines()
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

    unique_c_values = natsort.natsorted(unique_c_values, key=lambda x: float(re.findall(r'\d+\.\d+', x)[0]) if re.findall(r'\d+\.\d+', x) else float('inf'), alg=natsort.REAL)
    unique_vs_values = natsort.natsorted(unique_vs_values, key=lambda x: float(re.findall(r'\d+', x)[0]), alg=natsort.REAL)  
    
    # Create a dataframe
    df = pd.DataFrame(columns=['Gene ID'] + list(unique_vs_values))

    if len(df.columns) != len(unique_vs_values) + 1:
        print(f"Number of columns ({len(df.columns)}) does not match length of unique_vs_values ({len(unique_vs_values)})")
        return

    for c_number in sorted(unique_c_values):
        # Create a new row with the c value
        row = [c_number]
        
        while len(row) < len(unique_vs_values) + 1:
            row.append('')

        gene_data_list = search_gene_data(c_number)

        if gene_data_list:
            for file_name in unique_vs_values:
                match_found = False
                
                for gene_data in gene_data_list:
                    gene_file, gene_log2foldchange = gene_data
                    gene_file = os.path.splitext(gene_file)[0]
                    if gene_file == file_name:
                        col_index = list(unique_vs_values).index(file_name) + 1
                        row[col_index] = gene_log2foldchange
                        match_found = True
                        break
                
                # If no match was found for the current sample
                if not match_found:
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
            print(f"output.xlsx has been generated in {output_directory}")
            break
        except PermissionError:
            print(f"Error: Permission denied to write to {output_file_path}. If you have other application using output.xlsx, close it can be written to\nWaiting for 5 seconds before trying again...")
            wait(5)
    print_dynamic_line('Automatic matching completed')

def manual_match():
    print_dynamic_line('Manual matching start')
    # Search for gene data
    gene_id = input("Enter Gene ID: ")
    search_gene_data(gene_id)
    print_dynamic_line('Manual matching completed')

def initialization():
    setup_database()
    
    continue_with_automatch = precheck_source()

    print("Initialization completed\nReady for query")
    print_dynamic_line('')
    return continue_with_automatch

def main():
    try:
        continue_with_automatch = initialization()
        # Keep the program running until the user decides to exit
        while True:
            if not continue_with_automatch:
                user_input = input("[M]anual search\n[Q]uit\n Please make a selection:")
            else:
                user_input = input("[A]uto match and export output as an exel (.xlsx) file\n[M]anual search\n[Q]uit\n Please make a selection:")                

                if user_input.lower() == 'q':   
                    print("Exited by user")
                    raise SystemExit
                elif user_input.lower() == 'a' and continue_with_automatch:
                    auto_match()
                elif user_input.lower() == 'm':            
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

# ##its time to use multi treads
# import threading
# import time

# def check_user_input():
#     while True:
#         user_input = input("Enter a value: ")
#         print("You entered:", user_input)

# def do_something_else():
#     while True:
#         print("I am doing something else.")
#         time.sleep(2)

# # Start the threads
# input_thread = threading.Thread(target=check_user_input)
# input_thread.start()

# other_thread = threading.Thread(target=do_something_else)
# other_thread.start()

# # Wait for the input thread to finish
# input_thread.join()

# def wait(timeout=None, animation_char='.'):
#     start_time = time.time()
#     signal_received = False

#     def handler(signum, frame):
#         nonlocal signal_received
#         signal_received = True

#     # Set up signal handler
#     signal.signal(signal.SIGUSR1, handler)

#     try:
#         while True:
#             if signal_received:
#                 print()  # Print a newline to clear the animation
#                 break

#             elapsed_time = time.time() - start_time
#             if timeout is not None and elapsed_time >= timeout:
#                 print()  # Print a newline to clear the animation
#                 break

#             num_dots = int(elapsed_time % 3) + 1
#             animation = animation_char * num_dots

#             print(f"\rCleaning up {animation}", end="")
#             time.sleep(0.1)

#     finally:
#         # Cleanup code here
#         print("\nCleaning up done.")

#     # Restore the default signal handler
#     signal.signal(signal.SIGUSR1, signal.SIG_DFL)

#     import time

# def cleanup():
#     time.sleep(3)  # Simulate some cleanup work

# # Start the cleanup process in a separate thread
# import threading
# t = threading.Thread(target=cleanup)
# t.start()

# # Wait for the cleanup to finish
# wait(animation_char='.')