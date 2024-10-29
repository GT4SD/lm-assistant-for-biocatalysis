# Biocatalysis Assistant

![Biocatalysis Assistant Architecture](/assets/GraphicalAbstract.png)

**Biocatalysis Assistant** is an advanced Python-based chatbot framework designed to automate and facilitate bioinformatics and biocatalysis tasks. Leveraging a dynamic set of tools and integrating powerful language models, this assistant streamlines complex processes in computational biology and enzyme engineering, making research more efficient and accessible.



## Features

- **🗣️ Interactive Chatbot Interface**: Engage with the assistant through a user-friendly command-line interface.
- **🔧 Dynamic Tool Integration**: Seamlessly run various bioinformatics and biocatalysis tools.
- **🤖 Language Model Integration**: Utilize state-of-the-art language models to guide analysis and decision-making processes.
- **🔗 Extensible Architecture**: Easily integrate new tools and functionalities.
- **📈 Optimization Capabilities**: Optimize enzyme sequences for improved catalytic activity.
- **🔍 Comprehensive Analysis**: Perform detailed bioinformatics analyses, including binding site extraction and reaction element analysis.

## Tools

The Biocatalysis Assistant integrates several powerful tools to assist in various bioinformatics and biocatalysis tasks:

- **ExtractBindingSites**: Extract binding sites from enzyme sequences.
- **GetElementsOfReaction**: Analyze and extract elements from biochemical reactions.
- **Blastp**: Perform BLASTP searches for protein sequence analysis.
- **OptimizeEnzymeSequences**: Optimize enzyme sequences for improved catalytic activity.
- **FindPDBStructure**: Search for related protein structures in the PDB database.
- **DownloadPDBStructure**: Download PDB structure files.
- **Mutagenesis**: Perform in silico mutagenesis on protein sequences.
- **MDSimulation**: Run molecular dynamics simulations.

## Installation

### Prerequisites

- **Python**: Version 3.10 or higher. [Download Python](https://www.python.org/downloads/)

To use all the supported tools, install the following on your system:

- **BLASTP**: NCBI BLAST+ toolkit. [Download BLASTP](https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)
- **PyMOL**: Molecular visualization system. [Install PyMOL via Conda](https://pymol.org/2/#download)
- **GROMACS**: Molecular dynamics package. [Install GROMACS](https://manual.gromacs.org/documentation/current/install-guide/index.html)

### Steps

1. **Clone the Repository**

   ```bash
   git clone git@github.com/GT4SD/lm-assistant-for-biocatalysis
   cd lm-assistant-for-biocatalysis
   ```

2. **Install Poetry and Project Dependencies**

   ```bash
   pip install poetry
   poetry install
   ```

3. **Setup molecular dynamics file, the rxnaamapper and enzyme optimization models**
    Choose one of the following options based on your operating system:

    a) For macOS users with Homebrew:
    ```bash
    bash tools_setup/setup.sh
    ```

    b) For users on other operating systems or without Homebrew:
    ```bash
    bash tools_setup/setup.sh --skip-mc
    ```

    The script performs the following actions:

    (i) **RXNAAMapper Setup**
         - Sets up thea BERT model, a tokenizer and vocabulary

    (ii) **Minio Client (mc) Setup** (skipped if using `--skip-mc`)
         - Installs Minio Client using Homebrew
         - Configures Minio Client with predefined credentials

    (iii) **Enzyme Optimization Models Setup**
         - Downloads and sets up models for enzyme optimization (Minio needed)

    

    **Note:** - If you're not using macOS or don't have Homebrew, use the `--skip-mc` option and manually install Minio Client appropriate for your operating system.

4. **Install Additional Required Tools**

   - **BLASTP**
   - **PyMOL**
   - **GROMACS**

5. **Configure Environment Variables**

   Create a `.env` file in the project root and add your configuration:

   ```env
   KEY=your_genai_key_here
   API=your_genai_api_here
   ```

   > **Note**: Ensure that `.env` is added to `.gitignore` to protect sensitive information.

## Configuration

Each tool within the Biocatalysis Assistant has its own configuration options that can be customized using environment variables. Refer to the [Tool Documentation](./docs/tools.md) for specific configuration details.

## Usage

### Running the Biocatalysis Assistant

The Biocatalysis Assistant offers two interfaces for interaction: a Command Line Interface (CLI) and a Streamlit web application. Choose the interface that best suits your needs.

#### Command Line Interface (CLI)

To start the Biocatalysis Assistant using the CLI:

1. Ensure you have completed the installation process using Poetry.
2. Open your terminal.
3. Run the following command:

```bash
lmabc --help


Biocatalysis Assistant CLI Help

DESCRIPTION:
    This CLI provides an interface to interact with the Biocatalysis Assistant,
    allowing users to ask questions and receive responses related to biocatalysis.

USAGE:
    lmabc

INITIAL SETUP:
    Upon starting, you will be prompted to:
    1. Set verbosity level
    2. Confirm or change the model and provider

COMMANDS:
    help   : Display this help message
    exit   : Exit the program
    clear  : Clear the screen

INTERACTION:
    After setup, you can start asking questions. The assistant will process your
    input and provide responses based on its knowledge of biocatalysis.

EXAMPLES:
    - To ask a question:
      > Enter your question: What are the main types of enzyme catalysis?

    - To clear the screen:
      > Enter your question: clear

    - To exit the program:
      > Enter your question: exit
```

#### Streamlit Web Application

To run the Biocatalysis Assistant using the Streamlit web interface:

1. Ensure you have completed the installation process using Poetry.
2. Open your terminal.
3. Run the following command:

```bash
lmabc-app
```

This command starts the Streamlit server and automatically opens the web application in your default browser. If it doesn't open automatically, the terminal will display a local URL you can copy and paste into your browser.

The Streamlit app provides a user-friendly interface with:
- A chat-like interaction on the home page
- A list of available tools
- Settings for customizing the assistant's configuration

![Biocatalysis Assistant Homepage](/assets/Homepage.png)

Choose the interface that best fits your workflow and preferences. Both interfaces interact with the same underlying Biocatalysis Assistant, ensuring consistent functionality and results.


## References

If you use `lmabc` in your projects, please consider citing the following:

```bib
@software{LMABC,
  author = {Yves Gaetan Nana Teukam, Francesca Grisoni, Matteo Manica},
  month = {10},
  title = {The biocatalysis assistant: a language model agent for biocatalysis (lmabc)},
  url = {https://github.com/GT4SD/lm-assistant-for-biocatalysis},
  version = {main},
  year = {2024}
}
```

## License

The `lmabc` codebase is under MIT license.
For individual model usage, please refer to the model licenses found in the original packages.

## Support

For issues or questions, please [open an issue](https://github.com/GT4SD/lm-assistant-for-biocatalysis/issues) in the GitHub repository.