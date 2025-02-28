# Biocatalysis Assistant

![Biocatalysis Assistant Architecture](/assets/GraphicalAbstract.png)

**Biocatalysis Assistant** is an advanced Python-based chatbot framework designed to automate and facilitate bioinformatics and biocatalysis tasks. Leveraging a dynamic set of tools and integrating powerful language models, this assistant streamlines complex processes in computational biology and enzyme engineering, making research more efficient and accessible.

---

## Features

- **🗣️ Interactive Chatbot Interface**: Engage with the assistant through a user-friendly command-line interface.
- **🔧 Dynamic Tool Integration**: Seamlessly run various bioinformatics and biocatalysis tools.
- **🤖 Language Model Integration**: Utilize state-of-the-art language models to guide analysis and decision-making processes.
- **🔗 Extensible Architecture**: Easily integrate new tools and functionalities.
- **📈 Optimization Capabilities**: Optimize enzyme sequences for improved catalytic activity.
- **🔍 Comprehensive Analysis**: Perform detailed bioinformatics analyses, including binding site extraction and reaction element analysis.

---

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

---

## Installation

### Prerequisites

- **Python**: Version 3.10 or higher. [Download Python](https://www.python.org/downloads/)
- **GROMACS**: Molecular dynamics package. [Install GROMACS](https://manual.gromacs.org/documentation/current/install-guide/index.html)

---

### **1. Clone the Repository**

Clone the repository to your local machine:

```bash
git clone git@github.com/GT4SD/lm-assistant-for-biocatalysis
cd lm-assistant-for-biocatalysis
```

---

### **2. Set Up the Environment File**

Before running the application locally or in Docker, you **must** configure the `.env` file. This file contains essential environment variables required for the application to function correctly.

1. Create a `.env` file in the project root directory.
2. Add the following configuration:

   ```env
   KEY=your_key_here
   API=your_api_here
   ```

   Replace `your_key_here` and `your_api_here` with your actual credentials.

3. **Important**: Ensure that `.env` is added to `.gitignore` to protect sensitive information.

---

### **3. Install Uv and Project Dependencies**

Install the project dependencies using `uv`:

```bash
pip install uv
uv pip install -e .
```

---

### **4. Setup Molecular Dynamics Files, RXNAAMapper, Enzyme Optimization Models, and BLAST Databases**

The setup script supports a new `--blastdb` option to control which BLAST database(s) to download:

- **Default Behavior**: If no `--blastdb` option is provided, only the Swissprot database is downloaded.
- **Custom Database**: Pass a specific BLAST database name (e.g., `nr`) to download that database.
- **All Databases**: Pass `all` to download a predefined set of BLAST databases (swissprot, nr, nt, refseq_protein, refseq_rna, pdb).

#### **For macOS Users with Homebrew**

```bash
bash tools_setup/setup.sh --blastdb <db_name|all>
```

#### **For Users on Other Operating Systems or Without Homebrew**

Skip Minio Client installation using the `--skip-mc` flag:

```bash
bash tools_setup/setup.sh --skip-mc --blastdb <db_name|all>
```

---

### **5. Install Additional Required Tools**

- **PyMOL**: Install via Conda.
- **GROMACS**: Follow the official installation guide.

---


## Docker Setup and Usage

The Biocatalysis Assistant can also be run using Docker, which simplifies the setup process by encapsulating all dependencies in a container.

### **1. Building the Docker Image**

To build the Docker image, navigate to the project root directory and run:

```bash
docker build -t lmabc .
```

This command builds a Docker image tagged as `lmabc`.

---

### **2. Running the Docker Container**

Once the image is built, you can run the container using:

```bash
docker run -it -p 8501:8501 --env-file .env lmabc lmabc-app
```

- `-it`: Runs the container in interactive mode.
- `-p 8501:8501`: Maps port `8501` on your host to port `8501` in the container.
- `--env-file .env`: Passes environment variables from the `.env` file.

---

### **3. Mounting Local Directories**

To persist data or use local files (e.g., cache or configuration files) inside the container, you can mount a local directory to the container using the `--volume` flag. For example:

```bash
docker run -it -p 8501:8501 --env-file .env --volume ${HOME}/my-cache:/app/.lmabc lmabc lmabc-app
```

- `--volume ${HOME}/my-cache:/app/.lmabc`: Mounts the local directory `${HOME}/my-cache` to `/app/.lmabc` inside the container. This allows you to persist or share data between the host and the container.

---

### **4. Accessing the Streamlit Web Application**

After running the container, open your browser and navigate to:
```
http://localhost:8501
```

This will launch the Streamlit web application.

---

### **5. Running the CLI Inside the Container**

To use the Command Line Interface (CLI) inside the Docker container, run:

```bash
docker run -it --env-file .env lmabc:latest lmabc --help
```

This will display the CLI help message and allow you to interact with the assistant.

---

### **6. Example Commands**

Here are a couple of examples to get you started:

#### **Example 1: Running the Streamlit Web App**
```bash
docker run -it -p 8501:8501 --env-file .env lmabc:latest lmabc-app
```
Open your browser and go to `http://localhost:8501` to interact with the web interface.

#### **Example 2: Using the CLI to Ask a Question**
```bash
docker run -it --env-file .env lmabc:latest lmabc
```
Follow the prompts to set up the assistant and start asking questions.

#### **Example 3: Running with a Local Cache Directory**
```bash
docker run -it -p 8501:8501 --env-file .env --volume ${HOME}/my-cache:/app/.lmabc lmabc:latest lmabc-app
```
This command mounts the local directory `${HOME}/my-cache` to `/app/.lmabc` inside the container, allowing you to persist or share data.

---

### **7. Additional Tips**

- **Environment Variables**: Ensure your `.env` file is correctly formatted (key-value pairs without quotes) and located in the same directory as the `docker run` command.
- **Data Persistence**: Use the `--volume` flag to mount directories for data persistence, such as cache or configuration files.
- **Debugging**: If the container fails to start, you can inspect the logs by running:
  ```bash
  docker logs <container_id>
  ```

---

## Configuration

Each tool within the Biocatalysis Assistant has its own configuration options that can be customized using environment variables. Refer to the [Tool Documentation](./docs/tools.md) for specific configuration details.

---

## Usage

### Running the Biocatalysis Assistant

The Biocatalysis Assistant offers two interfaces for interaction: a Command Line Interface (CLI) and a Streamlit web application. Choose the interface that best suits your needs.

#### **Command Line Interface (CLI)**

To start the Biocatalysis Assistant using the CLI:

1. Ensure you have completed the installation process using Uv.
2. Open your terminal.
3. Run the following command:

```bash
lmabc --help
```

This displays a help message similar to:

```
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

#### **Streamlit Web Application**

To run the Biocatalysis Assistant using the Streamlit web interface:

1. Ensure you have completed the installation process using Uv.
2. Open your terminal.
3. Run the following command:

```bash
lmabc-app
```

This starts the Streamlit server and automatically opens the web application in your default browser. If it doesn't open automatically, the terminal will display a local URL you can copy and paste into your browser.

The Streamlit app provides a user-friendly interface with:
- A chat-like interaction on the home page.
- A list of available tools.
- Settings for customizing the assistant's configuration.

![Biocatalysis Assistant Homepage](/assets/Homepage.png)

Choose the interface that best fits your workflow and preferences. Both interfaces interact with the same underlying Biocatalysis Assistant, ensuring consistent functionality and results.

---

## References

If you use `lmabc` in your projects, please consider citing the following:

```bibtex
@software{LMABC,
  author = {Yves Gaetan Nana Teukam, Francesca Grisoni, Matteo Manica},
  month = {10},
  title = {The biocatalysis assistant: a language model agent for biocatalysis (lmabc)},
  url = {https://github.com/GT4SD/lm-assistant-for-biocatalysis},
  version = {main},
  year = {2024}
}
```

---

## License

The `lmabc` codebase is under MIT license.
For individual model usage, please refer to the model licenses found in the original packages.

---

## Support

For issues or questions, please [open an issue](https://github.com/GT4SD/lm-assistant-for-biocatalysis/issues) in the GitHub repository.

---
