"""Mutagenesis tools."""

__copyright__ = """
MIT License

Copyright (c) 2024 GT4SD team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, cast

from Bio.PDB import PDBParser, Superimposer
from Bio.SeqUtils import seq1
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..configuration import BIOCATALYSIS_AGENT_CONFIGURATION
from .core import BiocatalysisAssistantBaseTool
from .pdb import PDB_SETTINGS, DownloadPDBStructure

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class MutagenesisConfiguration(BaseSettings):
    """Configuration values for the Mutagenesis tool."""

    output_dir: Path = BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path(
        "mutagenesis"
    )
    clean_pdb_dir: Path = output_dir / "clean_pdb"
    mutated_pdb_dir: Path = output_dir / "mutated_pdb"
    pymol_path: str = "pymol"
    alignment_threshold: float = 0.5
    model_config = SettingsConfigDict(env_prefix="MUTAGENESIS_")


MUTAGENESIS_SETTINGS = MutagenesisConfiguration()


class MutationInput(BaseModel):
    """
    Input model for the Mutagenesis tool.

    Attributes:
        pdb_code: The 4-character PDB code of the protein structure to mutate.
        target_sequence: The target protein sequence to mutate towards.
        perform_rmsd: Whether to perform RMSD calculation (default is False).
    """

    pdb_code: str
    target_sequence: str
    perform_rmsd: bool = False


class Mutagenesis(BiocatalysisAssistantBaseTool):
    """Tool for performing mutations on protein structures using PyMOL."""

    name: str = "Mutagenesis"
    description: str = """
    This tool performs mutations on protein structures using PyMOL.
    It takes as input:
    - pdb_code (required): The 4-character PDB code of the protein structure to mutate.
    - target_sequence (required): The target protein sequence to mutate towards.
    - perform_rmsd (optional, default True): Whether to perform additional analysis on the structures.
    
    The tool performs the following steps:
    1. Downloads the PDB file if not found locally
    2. Cleans the PDB file by removing water molecules and other specified residues
    3. Determines the best matching chain to the target sequence
    4. Performs the specified mutations to match the target sequence
    5. Saves the mutated structure
    6. Optionally performs additional analysis (e.g., RMSD calculation)

    Output:
    - Path to the mutated PDB file
    - Optional analysis results (e.g., RMSD between original and mutated structures)

    Note: This tool requires PyMOL to be installed and accessible.

    Example:
        mutagenesis_tool = Mutagenesis()
        result = mutagenesis_tool.run(pdb_code="XXXX", target_sequence="MKLPVRW...", perform_rmsd=True)
    """

    @staticmethod
    def check_requirements() -> bool:
        """
        Check if the required directories and files for Mutagenesis exist.
        Returns:
            True if all required directories and files exist, False otherwise.
        """
        settings = MUTAGENESIS_SETTINGS

        paths_to_check = [
            settings.output_dir,
            settings.clean_pdb_dir,
            settings.mutated_pdb_dir,
        ]

        for path in paths_to_check:
            path_obj = Path(path)
            if not path_obj.exists():
                if path_obj.suffix:
                    logger.warning(f"Required file {path} does not exist.")
                    return False
                else:
                    try:
                        path_obj.mkdir(parents=True, exist_ok=True)
                        logger.info(
                            f"Directory {path} was missing and has been created."
                        )
                        return True
                    except Exception as e:
                        logger.error(f"Failed to create directory {path}. Error: {e}")
                        return False
            else:
                logger.info(f"{path} already exists.")
                return True

        try:
            from pymol import cmd

            _ = cmd
            return True
        except Exception as e:
            logger.warning(f"Error instantiating Mutagenesis: {str(e)}")
            return False

    @staticmethod
    def get_pdb_file(pdb_code: str) -> Path:
        """
        Retrieves or downloads a PDB file.

        Args:
            pdb_code: The 4-character PDB code.

        Returns:
            Path to the local PDB file.
        """
        local_path = Path(PDB_SETTINGS.output_dir) / f"{pdb_code}.pdb"
        if not local_path.exists():
            logger.info(f"Downloading PDB structure: {pdb_code}")
            DownloadPDBStructure().run(pdb_code)
        logger.info(f"Using PDB file: {local_path}")
        return local_path

    @staticmethod
    def extract_full_sequence(pdb_file: Path) -> Tuple[str, str]:
        """
        Extract the full amino acid sequence from a PDB file's SEQRES records.

        Args:
            pdb_file: Path to the PDB file.

        Returns:
            A tuple containing the chain ID and the full amino acid sequence.

        Raises:
            ValueError: If no SEQRES records are found in the PDB file.
        """
        with Path.open(pdb_file, "r") as f:
            lines = f.readlines()

        seqres_lines = [line for line in lines if line.startswith("SEQRES")]

        if not seqres_lines:
            raise ValueError("No SEQRES records found in the PDB file.")

        chain_id = seqres_lines[0][11]
        sequence = ""

        for line in seqres_lines:
            if line[11] == chain_id:
                sequence += "".join(seq1(res) for res in line[19:].split())

        return chain_id, sequence

    @staticmethod
    def find_mutations(original_sequence: str, target_sequence: str) -> List[str]:
        """
        Identify mutations needed to transform the original sequence into the target sequence.

        Args:
            original_sequence: The original amino acid sequence.
            target_sequence: The target amino acid sequence.

        Returns:
            A list of mutation strings in the format 'OriginalAA{position}NewAA'.
        """
        mutations = []
        for i, (orig, target) in enumerate(
            zip(original_sequence, target_sequence), start=1
        ):
            if orig != target:
                mutations.append(f"{orig}{i}{target}")
        return mutations

    @staticmethod
    def one_to_three(one_letter_code: str) -> str:
        """
        Convert a one-letter amino acid code to its three-letter equivalent.

        Args:
            one_letter_code: A single character representing an amino acid.

        Returns:
            The three-letter code for the amino acid, or 'UNK' if not recognized.
        """
        aa_dict: Dict[str, str] = {
            "A": "ALA",
            "C": "CYS",
            "D": "ASP",
            "E": "GLU",
            "F": "PHE",
            "G": "GLY",
            "H": "HIS",
            "I": "ILE",
            "K": "LYS",
            "L": "LEU",
            "M": "MET",
            "N": "ASN",
            "P": "PRO",
            "Q": "GLN",
            "R": "ARG",
            "S": "SER",
            "T": "THR",
            "V": "VAL",
            "W": "TRP",
            "Y": "TYR",
        }
        return aa_dict.get(one_letter_code.upper(), "UNK")

    @staticmethod
    def perform_mutations(
        pdb_file: Path, mutations: List[str], output_file: Path
    ) -> None:
        """
        Apply specified mutations to a protein structure using PyMOL.

        Args:
            pdb_file: Path to the input PDB file.
            mutations: List of mutations to perform.
            output_file: Path to save the mutated structure.

        Raises:
            PyMOLError: If there's an error in PyMOL during mutation.
        """
        from pymol import cmd

        cmd.load(str(pdb_file), "protein")
        cmd.wizard("mutagenesis")
        cmd.do("refresh_wizard")

        for mutation in mutations:
            _, pos, new = mutation[0], mutation[1:-1], mutation[-1]
            new_res = Mutagenesis.one_to_three(new)

            cmd.get_wizard().set_mode(new_res)
            cmd.get_wizard().do_select(f"{pos}/")

            cmd.frame(1)

            cmd.get_wizard().apply()

        cmd.save(str(output_file))
        cmd.delete("all")

    @staticmethod
    def calculate_rmsd(structure_1: Path, structure_2: Path) -> float:
        """
        Calculate the RMSD between two protein structures using CA atoms.

        Args:
            structure_1: Path to the first PDB structure file.
            structure_2: Path to the second PDB structure file.

        Returns:
            The calculated RMSD value as a float.

        Raises:
            ValueError: If the structures cannot be aligned or compared.
        """
        parser = PDBParser(QUIET=True)
        structure1 = parser.get_structure("structure1", structure_1)
        structure2 = parser.get_structure("structure2", structure_2)

        def get_ca_atoms(structure):
            atoms = []
            for model in structure:
                for chain in model:
                    for residue in chain:
                        if residue.has_id("CA"):
                            atoms.append(residue["CA"])
            return atoms

        atoms1 = get_ca_atoms(structure1)
        atoms2 = get_ca_atoms(structure2)

        n_atoms = min(len(atoms1), len(atoms2))
        atoms1 = atoms1[:n_atoms]
        atoms2 = atoms2[:n_atoms]

        sup = Superimposer()
        sup.set_atoms(atoms1, atoms2)

        return cast(float, sup.rms)

    def _run(
        self, pdb_code: str, target_sequence: str, perform_rmsd: bool = False
    ) -> str:
        """
        Execute the mutagenesis process on a given protein structure.

        Args:
            pdb_code: The 4-character PDB code of the protein to mutate.
            target_sequence: The target amino acid sequence.
            perform_rmsd: Whether to calculate RMSD after mutation (default False).

        Returns:
            A string containing the results of the mutagenesis process,
            including mutations performed and optionally the RMSD.

        Raises:
            ValueError: If the mutagenesis process fails at any step.
        """
        try:
            pdb_file = self.get_pdb_file(pdb_code)
            _, original_sequence = self.extract_full_sequence(pdb_file)
            mutations = self.find_mutations(original_sequence, target_sequence)

            output_file = pdb_file.parent / f"{pdb_code}_mutated.pdb"
            self.perform_mutations(pdb_file, mutations, output_file)

            result = f"Mutations performed: {', '.join(mutations)}. "
            result += f"Mutated structure saved to: {output_file}. "

            if perform_rmsd:
                rmsd = self.calculate_rmsd(pdb_file, output_file)
                result += f"RMSD between original and mutated structure: {rmsd:.4f} Å"

            return result
        except Exception as e:
            raise ValueError(f"Failed to perform mutagenesis: {str(e)}")

    async def _arun(self, *args, **kwargs) -> str:
        """
        Async method for Mutagenesis.

        Raises:
            NotImplementedError: Async execution is not implemented.
        """
        raise NotImplementedError("Async execution not implemented for Mutagenesis.")
