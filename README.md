# Project Manual

## Project: RNA Sequence Analysis Application for Excel Files Version 3.0

### Introduction

The RNA Sequence Analysis Application for Excel (.xls or .xlsx) Files is a Python-based tool for analyzing gene expression data from multiple samples. The application processes input data in the form of tab-separated value (TSV) files, with one file per sample, to identify genes that are differentially expressed across the different samples.

### Requirements

The tool is designed to run on WindowsTM operating systems, and no additional resources are required to run the executable file.

### Input Files

The input files for this tool should be in TSV format, with at least two columns: GeneID and log2FoldChange. GeneID is a unique identifier for each gene, while log2FoldChange represents the measured expression level for that gene in the sample.

### Running the Tool

To run the tool, follow these steps:

1. Use the provided executable file (`RNA_Analysis_Tool.exe`).
2. For usage examples, refer to the section below.

### Usage Examples

```bash
# Use the following command in the command line:
RNA_Analysis_Tool.exe
```

### Output

The tool outputs a list of genes that are differentially expressed across the different samples, along with their log2foldchange values and the name of the file where they were found. For example:

| Gene ID      | Found in filename | log2FoldChange       |
|--------------|-------------------|----------------------|
| Cluster-0001.0 | abc325            | [0.00000000000001]  |
| Cluster-0001.1 | def456, ghi789    | [0.00000000000002, -0.00000000000003] |

### Future Work

This tool has the potential for further development in various areas, including:

- Allowing the user to specify the names of the input files and output files.
- Adding support for more complex statistical tests to identify differentially expressed genes.
- Expanding functionality to handle different input file formats: Currently, the program is designed to handle input files in a specific format. In the future, it may be useful to add support for different file formats to make the program more flexible and applicable to a wider range of experiments.
- Adding statistical analysis features: While the program sorts and organizes gene expression data, it does not currently perform any statistical analyses. Future work could involve adding functionality to perform basic statistical analyses, such as calculating p-values or performing t-tests, to help users better understand the significance of their experimental results.
- Improving error handling and user feedback: While the program includes some error handling features, there is room for improvement in terms of providing more informative error messages and feedback to the user. Future work could involve adding more detailed error messages and logging features to help users troubleshoot issues more easily.

### Installation

No specific installation steps are required. Simply use the provided executable file.

### License

This project is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for more information.

### Contact Information

For questions, feedback, or issues, contact: myemail@mydomain.tld

### Acknowledgments

The source code of this project was originally from [pmukneam](https://github.com/pmukneam), a Data Science student at Pitzer College. It was originally available at [pmukneam/Bio-RNA-seq-analysis](https://github.com/pmukneam/Bio-RNA-seq-analysis). This project is made on their free time. The Pandas library was used in the development of this project.
