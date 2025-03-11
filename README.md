# Biocatalysis Assistant

![Biocatalysis Assistant Architecture](/assets/GraphicalAbstract.png)

**Biocatalysis Assistant** is a Python-based chatbot framework designed to automate and streamline bioinformatics and biocatalysis tasks. By integrating advanced language models and a dynamic set of tools, it simplifies complex processes in computational biology and enzyme engineering, making research more efficient and accessible.

---

## Table of Contents

1. [Features](#features)
2. [Tools](#tools)
3. [Installation](#installation)
   - [Docker Setup and Usage](#docker-setup-and-usage)
   - [Local Installation](#local-installation)
4. [Usage](#usage)
   - [Command Line Interface (CLI)](#command-line-interface-cli)
   - [Streamlit Web Application](#streamlit-web-application)
5. [References](#references)
6. [License](#license)
7. [Support](#support)

---

## Features <a name="features"></a>

- **🗣️ Interactive Chatbot Interface**: Engage with the assistant via a user-friendly command-line or web interface.
- **🔧 Dynamic Tool Integration**: Seamlessly run bioinformatics and biocatalysis tools.
- **🤖 Language Model Integration**: Leverage state-of-the-art language models for analysis and decision-making.
- **🔗 Extensible Architecture**: Easily add new tools and functionalities.
- **📈 Optimization Capabilities**: Optimize enzyme sequences for enhanced catalytic activity.
- **🔍 Comprehensive Analysis**: Perform detailed bioinformatics analyses, including binding site extraction and reaction element analysis.

---

## Tools <a name="tools"></a>

The Biocatalysis Assistant integrates the following tools for bioinformatics and biocatalysis tasks:
- **ExtractBindingSites**: Extract binding sites from enzyme sequences.
- **GetElementsOfReaction**: Analyze and extract elements from biochemical reactions.
- **Blastp**: Perform BLASTP searches for protein sequence analysis.
- **OptimizeEnzymeSequences**: Optimize enzyme sequences for improved catalytic activity.
- **FindPDBStructure**: Search for related protein structures in the PDB database.
- **DownloadPDBStructure**: Download PDB structure files.
- **Mutagenesis**: Perform in silico mutagenesis on protein sequences.
- **MDSimulation**: Run molecular dynamics simulations.

**Note:**  

For a complete description of the tool and its usage, refer to [tools_description.md](./tools_description.md).

---

## Installation <a name="installation"></a>

### Docker Setup and Usage <a name="docker-setup-and-usage"></a>

The Biocatalysis Assistant can be run using Docker, which simplifies the setup process by encapsulating all dependencies in a container. **If you use Docker, you can skip the local installation steps below.**

#### **1. Build the Docker Image**
```bash
docker build -t lmabc .
```

#### **2. Run the Docker Container**
```bash
docker run -it -p 8501:8501 --env-file .env lmabc lmabc-app
```
- `-it`: Runs the container interactively.
- `-p 8501:8501`: Maps port `8501` on your host to the container.
- `--env-file .env`: Passes environment variables.

#### **3. Mount Local Directories**
To persist data or use local files:
```bash
docker run -it -p 8501:8501 --env-file .env --volume ${HOME}/my-cache:/app/.lmabc lmabc lmabc-app
```

#### **4. Access the Streamlit Web App**
Open your browser and navigate to:
```
http://localhost:8501
```

#### **5. Use the CLI Inside the Container**
```bash
docker run -it --env-file .env lmabc:latest lmabc --help
```

#### **6. Example Commands**
- **Run the Streamlit Web App**:
  ```bash
  docker run -it -p 8501:8501 --env-file .env lmabc:latest lmabc-app
  ```
- **Use the CLI**:
  ```bash
  docker run -it --env-file .env lmabc:latest lmabc
  ```
- **Run with Local Cache**:
  ```bash
  docker run -it -p 8501:8501 --env-file .env --volume ${HOME}/my-cache:/app/.lmabc lmabc:latest lmabc-app
  ```

---

### Local Installation <a name="local-installation"></a>

If you prefer to run the Biocatalysis Assistant locally, follow these steps.

#### **Prerequisites**
- **Python**: Version 3.10 or higher. [Download Python](https://www.python.org/downloads/).
- **GROMACS**: A molecular dynamics simulation package. [Install GROMACS](https://manual.gromacs.org/documentation/current/install-guide/index.html).

---

#### **1. Clone the Repository**

Clone the repository to your local machine:

```bash
git clone git@github.com:GT4SD/lm-assistant-for-biocatalysis.git
cd lm-assistant-for-biocatalysis
```

---

#### **2. Set Up the Environment File**

1. Create a `.env` file in the project root directory.
2. Add your credentials (e.g., for Hugging Face API):
   ```env
   HUGGINGFACEHUB_API_TOKEN=your_key_here
   ```
3. **Important**: Ensure `.env` is added to `.gitignore` to protect sensitive information.

---

#### **3. Install Dependencies**

Install dependencies using `uv`:

```bash
pip install uv
uv pip install -e .
```

---

#### **4. Set Up Tools and Databases**

Run the setup script to configure molecular dynamics files, RXNAAMapper, enzyme optimization models, and BLAST databases. Use the `--blastdb` option to specify which BLAST database(s) to download:
- **Default**: Downloads Swissprot database.
- **Custom**: Pass a specific database name (e.g., `nr`).
- **All**: Pass `all` to download a predefined set of databases.

##### **For macOS Users with Homebrew**
```bash
bash tools_setup/setup.sh --blastdb <db_name|all>
```

##### **For Other Operating Systems or Without Homebrew**
Skip Minio Client installation:
```bash
bash tools_setup/setup.sh --skip-mc --blastdb <db_name|all>
```

---

#### **5. Install Additional Tools**
- **PyMOL**: Install via Conda.
- **GROMACS**: Follow the [official installation guide](https://manual.gromacs.org/documentation/current/install-guide/index.html).

---

## Usage <a name="usage"></a>

### Command Line Interface (CLI) <a name="command-line-interface-cli"></a>

To start the Biocatalysis Assistant using the CLI:

1. Ensure you have completed the installation process using Uv.
2. Open your terminal.
3. Run the following command:

```bash
lmabc --help
```

---

### Streamlit Web Application <a name="streamlit-web-application"></a>

To run the Biocatalysis Assistant using the Streamlit web interface:

1. Ensure you have completed the installation process using Uv.
2. Open your terminal.
3. Run the following command:

```bash
lmabc-app
```

---

## References <a name="references"></a>

If you use `lmabc` in your projects, please cite:
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

## License <a name="license"></a>

The `lmabc` codebase is under the MIT license. For individual model usage, refer to the licenses of the original packages.

---

## Support <a name="support"></a>

For issues or questions, please [open an issue](https://github.com/GT4SD/lm-assistant-for-biocatalysis/issues) in the GitHub repository.

---
