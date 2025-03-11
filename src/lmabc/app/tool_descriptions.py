#
# MIT License
#
# Copyright (c) 2025 GT4SD team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.#
"""Tool Descriptions."""

TOOL_DESCRIPTIONS = {
    "**GetElementsOfReaction**": """Parses reaction SMILES to extract specific reactants, amino acid sequences, and products. This tool is essential for deconstructing complex biochemical reactions, allowing for detailed analysis of individual components.

    **Input Format**:
        - Reaction SMILES must follow this structure: 'substrate SMILES | amino acid sequence >> product SMILES'
        - Example: 'CC(=O)Cc1ccccc1|MTENALVR>>CC(O)Cc1ccccc1'
    
    **Components**:
        1. Substrate SMILES: Chemical structure of starting material(s) in SMILES notation
           - Multiple substrates should be separated by '.'
        2. Amino Acid Sequence: Protein sequence in single-letter code
           - Must be separated from substrates by '|'
           - Valid characters are standard amino acid letters (A-Z)
        3. Product SMILES: Chemical structure of product(s) in SMILES notation
           - Separated from previous components by '>>'
           - Multiple products should be separated by '.'
    
    **Output Format**:
        Returns a formatted string with three components:
        'Reactants: [substrate SMILES], AA Sequence: [protein sequence], Products: [product SMILES]'
    
    **Usage Notes**:
        - All SMILES must be valid chemical structures
        - Spaces around separators (| and >>) are optional
    """,
    "**ExtractBindingSites**": """Utilizes [RXNAAMapper](https://doi.org/10.1016/j.csbj.2024.04.012) to extract binding sites from reaction SMILES strings. This tool is crucial for understanding enzyme functionality, as it identifies key sites that can be targeted for mutations to enhance catalytic activity or optimize user-specified fitness functions.

    
    **Input Format**:
        - Reaction SMILES must follow this structure: substrate SMILES | amino acid sequence >> product SMILES
        - Example: CC(=O)Cc1ccccc1|MTENALVR>>CC(O)Cc1ccccc1
    
    **Output Format**:
        - Returns a string containing the extracted binding sites in the format:
          'The binding sites are: [start-end, start-end, ...]'
        - Example: 'The binding sites are: 0-1, 20-24, 34-36'
    
    **Usage Notes**:
        - The tool checks for the existence of required files and directories before execution.
        - If the input is invalid or extraction fails, an error message is returned.
    """,
    "**OptimizeEnzymeSequences**": """Optimizes enzyme sequences for biocatalytic reactions using [Enzeptional](https://chemrxiv.org/engage/chemrxiv/article-details/65f0746b9138d23161510400). This powerful tool supports multiple optimization iterations based on substrate and product SMILES, featuring customizable scoring models and interval-specific mutations. It employs Genetic Algorithms to explore the vast sequence space and identify promising enzyme variants with improved catalytic properties. The tool outputs a ranked list of optimized sequences for experimental validation, significantly accelerating the enzyme engineering process.

    **Input Format**:
        - `substrate_smiles` (str): SMILES representation of the reactant molecule.
        - `product_smiles` (str): SMILES representation of the desired product molecule.
        - `protein_sequence` (str): Amino acid sequence of the enzyme to optimize.
        - `scorer_type` (str): The scoring model type, either `'feasibility'` (default) or `'kcat'`.
        - `intervals` (List[List[int]], optional): List of regions (start, end) to focus mutations on (e.g., important sites). Example: `[[1, 4], [20, 21], [50, 56]]`.
        - `number_of_results` (int, optional): Number of optimized sequences to return. Default: 10.
        - Additional optional parameters include `num_iterations`, `num_sequences`, `num_mutations`, `time_budget`, `batch_size`, `top_k`, `selection_ratio`, `perform_crossover`, `crossover_type`, `pad_intervals`, `minimum_interval_length`, and `seed`.

    **Output Format**:
        - Returns a tabulated string of optimized enzyme sequences ranked by predicted performance for the given reaction.
        - Example output:
            ```
            +--------+-----------------------------+--------+
            | Index  | Sequence                    | Score  |
            +--------+-----------------------------+--------+
            | 1      | MVLSPADKTNVKAA...           | 0.9200 |
            | 2      | MVLAPADKTNVKAA...           | 0.8900 |
            | 3      | MVLSPADRTNVKAA...           | 0.8750 |
            +--------+-----------------------------+--------+
            ```
    """,
    "**Blastp**": """Performs BLASTP (Basic Local Alignment Search Tool for Proteins) searches to identify protein sequences similar to a given query using [NCBI](https://www.ncbi.nlm.nih.gov). This tool allows customization of key parameters and generates comprehensive output including aligned sequences, descriptions, and statistical data, facilitating detailed protein homology and function analysis. By leveraging the vast NCBI database, it enables researchers to discover evolutionarily related proteins, predict functional similarities, and identify conserved domains. The results can guide further experimental investigations and provide insights into protein structure-function relationships.

    **Input Format**:
        - `query` (str): The protein sequence as a string.
        - `experiment_id` (str, optional): A unique identifier for this run. If not provided, a default ID is generated.
        - `database_name` (str, optional): The name of the BLAST database to use (default: `"swissprot"`).
        - `evalue` (float, optional): The E-value threshold for reporting matches (default: `1e-5`).
        - `outfmt` (str, optional): The output format (default: `"6 sseqid pident evalue bitscore stitle sseq"`).
        - `max_target_seqs` (int, optional): The maximum number of aligned sequences to keep (default: `10`).
        - Additional BLASTP arguments can be passed as keyword arguments (e.g., `gapopen=11`). Only valid BLASTP arguments are accepted.

    **Output Format**:
        - Returns a formatted message with result details, including:
            - The database used.
            - The experiment ID (if provided).
            - A tabulated list of top matches with columns such as Accession, Identity (%), E-Value, Bit Score, and Description.
            - The total number of matches found.
            - The location of saved results (query FASTA file and BLAST output file).
        - Example output:
            ```
            BLASTP Search Completed Successfully!

            Results saved in: `.cache_dir/blast/blast_logs/experiment_id/experiment_folder`
            - Query FASTA File: `.cache_dir/blast/blast_logs/experiment_id/query.fasta`
            - BLAST Output File: `.cache_dir/blast/blast_logs/experiment_id/blast_output.txt`

            Top Matches:
            +------------+------------+---------+-----------+-----------------------------------+
            | Accession  | Identity   | E-Value | Bit Score | Description                       |
            +------------+------------+---------+-----------+-----------------------------------+
            | XXX        | XX.X       | X       | X         | X                                 |
            | XXX        | XX.X       | X       | X         | X                                 |
            | XXX        | XX.X       | X       | X         | X                                 |
            +------------+------------+---------+-----------+-----------------------------------+
            ```
    """,
    "**FindPDBStructure**": """Finds and retrieves [PDB](https://www.rcsb.org) structures based on a query using the [RCSB python package](https://rcsbsearchapi.readthedocs.io/en/latest/). This tool identifies protein structures (PDB structures or 3D structures) related to a given protein sequence by querying the RCSB database.

    **Input Format**:
        - `protein_sequence` (str): The protein sequence as a string.

    **Output Format**:
        - Returns a string containing the PDB code and entity ID of the matching structure (if found).
        - Example output: `"pdb code 1abc with entity id 1"`.
        - If no perfect match is found, returns: `"Couldn't find a perfect match"`.
    """,
    "**DownloadPDBStructure**": """Downloads specific PDB structures based on a PDB code using the [RCSB Search API](https://search.rcsb.org). This tool complements the FindPDBStructure functionality by allowing direct retrieval of identified structures. It downloads the corresponding PDB structure file from the RCSB PDB database and saves it in the configured output directory.

    **Input Format**:
        - `pdb_code` (str): The PDB code of the structure to download (e.g., `"1abc"`).

    **Output Format**:
        - Returns a string message indicating the success or failure of the download.
        - Example output: `"Successfully downloaded PDB file: .cache_dir/pdb/1abc.pdb"`.
        - If the download fails, returns an error message: `"Error: [status_code], Failed to download PDB file for [pdb_code]"`.

    """,
    "**Mutagenesis**": """Employs [PyMOL](https://www.pymol.org) to perform targeted mutations on protein structures, enabling the transformation of a protein structure to match a specified target sequence. It can optionally perform additional analyses like RMSD (Root Mean Square Deviation) calculations to assess structural changes. This tool can be used for predicting the structural consequences of amino acid substitutions, allowing researchers to visualize potential changes in protein conformation and stability. By integrating with PyMOL's powerful visualization capabilities, it provides both quantitative and qualitative insights into the effects of mutations on protein structure and function.

    **Input Format**:
        - `pdb_code` (str): The 4-character PDB code of the protein structure to mutate (e.g., `"1abc"`).
        - `target_sequence` (str): The target protein sequence to mutate towards.
        - `perform_rmsd` (bool, optional): Whether to perform RMSD calculation (default: `False`).

    **Output Format**:
        - Returns a string containing:
            - The path to the mutated PDB file.
            - If `perform_rmsd=True`, the RMSD value between the original and mutated structures.
        - Example output:
            ```
            Mutations performed: A1G, L2V. Mutated structure saved to: .cache_dir/mutagenesis/1abc_mutated.pdb. RMSD between original and mutated structure: 0.1234 Å.
            ```
    """,
    "**MDSimulation**": """Facilitates Molecular Dynamics simulations using [GROMACS](https://www.gromacs.org). This tool automates the setup and execution of standard MD simulation stages, including Minimization, NVT (constant Number, Volume, Temperature) equilibration, and NPT (constant Number, Pressure, Temperature) equilibration.

    **Input Format**:
        - `pdb_file` (Path): Path to the input PDB file containing the protein structure.
        - `stages` (List[str], optional): List of simulation stages to run. Default is `["minimization", "nvt", "npt"]`.
        - `experiment_id` (str, optional): A unique identifier for this run. If not provided, a default ID is generated.
        - Additional keyword arguments can be passed to customize simulation parameters for each stage:
            - `minimization`: Dictionary of parameters for the minimization stage (e.g., `{"nsteps": 100}`).
            - `nvt`: Dictionary of parameters for the NVT equilibration stage (e.g., `{"nsteps": 5000}`).
            - `npt`: Dictionary of parameters for the NPT equilibration stage (e.g., `{"nsteps": 5000}`).

    **Output Format**:
        - Returns a string describing the simulation outcome, including the path to the final output file.
        - Example output: `"MD simulation completed successfully. Final output: .cache_dir/molecular_dynamics/output_file.gro"`.

    **Usage Notes**:
        - The tool runs the stages in the order specified in the `stages` argument.
        - Each stage depends on the completion of the previous one (e.g., NVT requires Minimization to complete first).
        - Default parameters are provided for each stage, but users can override them using keyword arguments.
        - The tool preprocesses the input PDB file to extract only the protein structure before running simulations.
    """,
}
