# RNA Sequence Analysis Application for Excel Files

Specifically made for Laboratory 2903, 9th floor, Science Complex Building (SCB2), Faculty of Science, Chiang Mai University, Thailand

## Introduction

The RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files is a Python-based tool for analyzing gene expression data from multiple samples. The application processes input data in the form of tab-separated value (CSV) files, with one file per sample, to identify genes that are differentially expressed across the different samples. Users can insert gene data into a database, search for gene data in the database, and view the results of their queries.

## Dependencies

The following dependencies are required to run the application:

- sqlite3
- pandas
- xlrd

Certainly! Here's the revised section with grammatical improvements, mentioning CSV compatibility, and providing clearer instructions:

## Input Files

- The Excel input files (either `.xls` or `.xlsx`) for this tool should be in CSV format. Each file should contain at least two columns: GeneID and log2FoldChange. GeneID serves as a unique identifier for each gene, while log2FoldChange represents the measured expression level for that gene in the sample.

- Additionally, the reference TXT file used in the auto-match process should follow a specific format: `file_of_interest1` `geneID_of_interest1` `geneID_of_interest2` `geneID_of_interest3` ... `geneID_of_interestn` `file_of_interest2` `geneID_of_interest1` ... The application will associate each `geneID_of_interest` with the corresponding reading `file_of_interest name`.
  - The `file_of_interest` should adhere to one of the following formats: `TnVsCn`, `TnvsCn`, `tnvsCn`, `Tn+VScn`, or `tnvsdn`. The application determines the input file associated with each geneID_of_interest by identifying the value of n following T and C in the file_of_interest format. 
  - Each `geneID_of_interest` can follow the pattern `some_string` `number1.number2`.

See more here: [file_examples](Examples/)

## Database Structure

The database used for this application is called `gene_data.db`. It will be located in `temp/` directory of the current working directory. If this database does not exist, the application will create it automatically. The database has a single table called `gene_info` with the following columns:

- gene_id (string)
- file_name (string)
- log2foldchange (real number)

An index has been created on the gene_id column for improved query performance.

## Usage

1. **Install Python:**
   - If you don't have Python installed on your computer, you can download and install it from the official Python website: [python.org](https://www.python.org/downloads/).
   - Follow the installation instructions for your operating system.
   - Version `3.11.1` or later is recommended.

2. **Install pip:**
   - Pip is a package manager for Python that allows you to install and manage Python packages.
   - After installing Python, pip should be automatically installed. You can verify this by opening a terminal or command prompt and running the following command:

     ```bash
     pip --version
     ```

   - If pip is installed, you should see its version information. If not, you can install pip by following the instructions [here](https://pip.pypa.io/en/stable/installation/).

3. **Set Up a Virtual Environment (Optional but Recommended):**
   - It's good practice to work within a virtual environment to isolate your project dependencies from other Python projects on your system.
   - To create a virtual environment, navigate to your project directory in the terminal or command prompt and run the following command:

     ```bash
     python -m venv venv
     ```

   - This will create a new directory named `venv` in your project directory, which will contain the virtual environment.
   - To activate the virtual environment, run the appropriate command based on your operating system:
     - On Windows:

       ```bash
       venv\Scripts\activate
       ```

     - On macOS and Linux:

       ```bash
       source venv/bin/activate
       ```

   - After this process is finished, you should see the `venv` directory appear in your working directory.

4. **Install Dependencies:**
   - Once you have Python installed and a virtual environment set up (if desired), you can install the project dependencies by running the following command in your terminal or command prompt:

    ```bash
    pip install -r requirements.txt
    ```

   - This command will install all the dependencies listed in the [requirements.txt](requirements.txt) file.

5. **Download Script:**
   - Download the [RNASeqMatch.py](RNASeqMatch.py) script and save it in your workspace directory.

6. **Run the Application:**

    - Open the terminal or command prompt and navigate to the directory where the script is saved.
    - Run the following command:

    ```bash
    python RNASeqMatch.py
    ```

    This command will start the application in the terminal.

7. **Ensure Input Data Directory:**

    - If the `input_data` directory does not exist in the current directory, the application will exit with an error message and automatically create a blank `input_data` for you. To avoid this, create the `input_data` directory and copy your `.xls` or `.xlsx` files into this directory ahead of the execution.

8. **Start the Application Again If Step 7 Failed:**

    - Once you have copied your files into the `input_data` directory, start the application again by running the command in step 6.

9. **Database Creation:**

    - You will notice that a new directory named `temp` will be created in your working directory. The application will automatically create a database file at `temp/gene_data.db` in order to store the input data from your Excel files.
    - This process might take a while depending on the size of data you are dealing with.

10. **Choosing Operation Mode**
    - You will be prompted to choose between auto-matching or manual search mode.

    ```plaintext
    1. [A]uto match and export output as an Excel (.xlsx) file
    2. [M]anual search
    3. [Q]uit
    Please make a selection:
    ```

    You can simply type `1` or `A` or `a` then `Enter` to select `Automatic matching`.

    10.1 **Chose `Auto Matching`**
    - You will be further asked which TXT files to use if there is more than one file exist in `input_data`.

    ```plaintext
    Found 2 TXT files in ./input_data/:
    1. set_of_interest_1.txt
    2. set_of_interest_1.txt
    Which TXT file do you want to read from? (Enter a number):
    ```

    You can, for example, choose file `set_of_interest_1.txt` by typing in `1` then `Enter`.

    - Outputs should look like:

    ```plaintext
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Gene ID being used to search database: 55555.0
    Result(s) for Cluster-55555.0:
    File: T1VsC1.xls      Log2FoldChange: -1.56789456123125
    File: T15vsC15.xls    Log2FoldChange: -4.033215648
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Gene ID being used to search database: 59784.0
    No results found for Cluster-59784.0
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ```

    - In a single Excel file named after the reference TXT file `set_of_interest.xlsx`, the tool outputs a list of genes that are differentially expressed across the different samples, along with their log2foldchange values and the name of the file where they were found. For example:

    | Gene ID | Filename 1 | Filename 2 | ... | Filename N |
    |---------|------------|------------|-----|------------|
    | C0001.0 | value 11   | value 21   | ... | value n1   |
    | C0001.1 | value 12   | value 22   | ... | value n2   |
    | ...     | ...        | ...        | ... | ...        |
    | Cn.n    | value 1n   | value 2n   | ... | value nn   |

    10.2. **Chose `Manual Searching`**

    - Enter the gene ID when prompted. For example, to search for `Cluster-1234.1`, simply type `1234.1` then `Enter`. The application will only entertain the number pattern `ABCD.EFGH` where A to H are numbers. Other strings will be disregarded or it would return an error.

    - The application will search the database for the gene and display the results. If there are no results, the application will display a message indicating no results were found. For examples:
        - When entering the number in the expected format and found

        ```plaintext
        Enter Gene ID: 8690.0
        Gene ID being used to search database: 8182.0
        Result(s) for Cluster-8690.0:
        File: T15vsC15.xls    Log2FoldChange: 3.14159265358979
        ```

        - When entering the number in the expected format and not found

        ```plaintext
        Enter Gene ID: cluster168324.0
        Gene ID being used to search database: 168324.0
        No results found for Cluster-168324.0
        ```

        - When entering an unexpected format

        ```plaintext
        Enter Gene ID: asdf123
        Exception: list index out of range
        Error getting data for gene asdf123: list index out of range
        ```

11. **Exit the Application:**

    - Cleaning up after you are done to make sure that the database won't unnecessarily take your space. It also can prevent malicious activity from wrongfully accessing the database.
    - Normally, when prompted, exit the application by pressing `'q'` then `Enter`.
    - Alternatively, without being prompted, `'Ctrl+C'` should also properly terminate and clean up at any stage of the program.
    -To deactivate the virtual environment, run the appropriate command based on your operating system:

    On Windows:

    ```bash
    venv\Scripts\deactivate
    ```

    On macOS and Linux:

    ```bash
    source venv/bin/deactivate
    ```

12. **Manual Database Deletion:**
    - You should always check if the `temp/gene_data.db` actually got deleted.
    - If the application was not terminated as described in step 11, the database might still exist on your system. You can manually delete the temporary directory `temp` in the current directory.

------

## Future work

- **GUI implementation:** The application can be further developed to include a graphical user interface (GUI) to provide a better user experience.
- **Error handling improvement:** Although error handling is present in the application, further enhancement can be done to cover additional edge cases and provide more informative error messages to the user.
- **Additional features:** The suggested features like exporting data to a CSV file, sorting search results, and filtering data based on criteria can still be valuable additions to enhance the functionality of the application.
- **Compatibility extension:** While the current version of the application fixed the input file location, adding flexibility for users to specify input file names and locations could improve usability.
- **Expanding functionality to handle different input file formats:** Although the program currently handles specific file formats, adding support for additional formats can increase the versatility of the application.
- **Adding statistical analysis features:** Integrating statistical analysis capabilities would provide users with more insights into their data and enhance the utility of the application.
- **Cloud integration:** Connecting the application with cloud platforms would enable users to access it remotely and facilitate data storage and management. This could be beneficial for collaboration and scalability.

------

## Version History

### [Version 1.0 - Feb 4, 2023](old/main.py)

- Initial release of the program.
- Added functionality to read gene ID data from multiple Excel files in a directory.
- Added ability to group gene IDs based on the numbers found in the filename.
- Implemented a dictionary to store gene IDs and their associated numbers.
- Added a function to print out gene IDs and their associated numbers.

### [Version 2.0 - Feb 6, 2023](old/RNASeqMatch2.py)

- Changed required file naming convention. Users are no longer required to change the filename into numbers so that the application can access the file.

### [Version 2.1 - Feb 8, 2023](old/RNASeqMatch2.1.py)

- Fixed an issue where the program would crash if no `input_data` directory was present.
- Added functionality to automatically create an `input_data` directory if it doesn't exist.
- Added a check for an empty `input_data` directory.
- Improved output formatting in the `results.txt` file.
- Improved code readability.

### [Version 3.0 - Feb 8, 2023](old/RNASeqMatch3.py)

- Added output for the Log2FoldChange associated with the GeneID.
- Improved output formatting of the `results.txt` file.
- Refactored the code for better readability and maintainability.
- Added comments to explain the code logic.

### [Version 3.1 - Feb 25, 2023](old/RNASeqMatch3.1.py)

- Improved the UI.
- Improved output formatting of the `results.txt` file.
- Improved sorting mechanism.

### [Version 3.2 - Feb 26, 2023](src/old/RNASeqMatch3.2.py)

- Improved the UI.
- Log2FoldChange value output order is now ordered according to the filename order it is associated with.

### [Version 4.0 - March 25, 2023](old/RNASeqMatch4.py)

- Introduced SQLite 3 as a database infrastructure for more efficiency and security.
- Added the feature to search for Log2FoldChange values associated with the GeneID and the filename in which the GeneID and Log2FoldChange value are found. GeneIDs can now be specified directly by the user in the terminal.
- Users can now specify the source data directory path.
- Removed the feature to export results as `results.txt` file.

### [Version 4.1 - March 26, 2023](old/RNASeqMatch4.1.py)

- Removed the feature to specify the source data directory path. A fixed source path to source data is fixed to `./input_data/`.
- Replaced the feature to read from CSV values in `.txt` files back to CSV values in either `.xls` or `.xlsx` files.
- Improved the terminal UI.
- Added an auto-delete database `gene_data.db` feature at exit.

### [Version 4.2 - March 26, 2023](old/RNASeqMatch4.2.py)

- Added a feature to sort the gene data search results by filename and then by log2foldchange using the natsort library.
- Improved error handling for file reading and database queries.
- Fixed an issue where exiting the program by the user did not delete the database.
- Improved the auto-delete database `gene_data.db` feature at exit.

### [Version 5.0 - March 29, 2023](RNASeqMatch.py)

- Added functionality to read input files from a specified directory.
- Improved database.
- Added manual matching of gene data.
- Renamed original feature to "auto-matching" for automatically matching gene data.
- Allowed users to choose between manual search, auto-matching mode.
- Improved error handling and signal handling for graceful termination.
- **Threading Support:**
  - Introduced threading for concurrent execution of tasks.
  - Implemented separate threads for user input monitoring and background operations.
  - Enhanced user experience by allowing input monitoring while performing other tasks.
  - Demonstrated thread usage with example cleanup code featuring a timeout.
  - Integrated cleanup with a timeout functionality into the script.
  - Improved responsiveness and efficiency by leveraging threading for parallel task execution.

------

## License

This project is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for more information.

**Note:** This software incorporates code from [pmukneam](https://github.com/pmukneam), used with permission under the terms of the MIT License. This permission supersedes any conflicting license terms from previous versions. See more in Acknowledgments.

------

## Contact Information

For questions, feedback, or issues, contact: myemail@mydomain.tld

------

## Acknowledgments

The source code of this project was originally from [pmukneam](https://github.com/pmukneam), a Data Science student at Pitzer College. It was originally available at [pmukneam/Bio-RNA-seq-analysis](https://github.com/pmukneam/Bio-RNA-seq-analysis). [pandas](https://github.com/pandas-dev/pandas), [SQLite](https://github.com/sqlite/sqlite), [xlrd](https://github.com/python-excel/xlrd), and [openpyxl](https://github.com/theorchard/openpyxl) libraries were used in the development of this project.
