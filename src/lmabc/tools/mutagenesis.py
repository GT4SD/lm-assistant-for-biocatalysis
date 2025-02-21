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
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..configuration import BIOCATALYSIS_AGENT_CONFIGURATION
from .core import BiocatalysisAssistantBaseTool
from .pdb import PDB_SETTINGS, DownloadPDBStructure

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class MutagenesisConfiguration(BaseSettings):
    """Configuration values for the Mutagenesis tool."""

    cache_dir: Path = Field(
        default_factory=lambda: Path(
            BIOCATALYSIS_AGENT_CONFIGURATION.get_tool_cache_dir("mutagenesis")
        ),
        description="Cache directory.",
    )
    clean_pdb: Path = Field(
        default=BIOCATALYSIS_AGENT_CONFIGURATION.get_tool_dir("mutagenesis") / "clean_pdb",
        description="Clean PDB path.",
    )
    mutated_pdb: Path = Field(
        default=BIOCATALYSIS_AGENT_CONFIGURATION.get_tool_dir("mutagenesis") / "mutated_pdb",
        description="Mutated PDB path.",
    )
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
    This tool facilitates the transformation of protein structures by performing targeted mutations using PyMOL. It adapts a given protein structure, specified by its PDB code, to match a desired target sequence using PYMOL. The process involves:

    It takes as input:
    - pdb_code (required): The 4-character PDB code of the protein structure to mutate.
    - target_sequence (required): The target protein sequence to mutate towards.
    - perform_rmsd (optional, default False): Whether to perform RMSD calculation. Default is False

    Output:
    - Path to the mutated PDB file.
    - Optional RMSD value between original and mutated structures.
    """

    @staticmethod
    def check_requirements() -> bool:
        """
        Check if the required directories and PyMOL are available.
        Returns:
            True if all requirements are met, False otherwise.
        """
        try:
            from pymol import cmd

            _ = cmd  # Ensure PyMOL is importable
            for path in [
                MUTAGENESIS_SETTINGS.cache_dir,
                MUTAGENESIS_SETTINGS.clean_pdb,
                MUTAGENESIS_SETTINGS.mutated_pdb,
            ]:
                path.mkdir(parents=True, exist_ok=True)
            return True
        except ImportError:
            logger.error("PyMOL is not installed or PyQt5 is missing.")
            return False
        except Exception as e:
            logger.error(f"Error checking requirements: {e}")
            return False

    @staticmethod
    def get_pdb_file(pdb_code: str) -> Path:
        """
        Retrieve or download a PDB file.

        Args:
            pdb_code: The 4-character PDB code.

        Returns:
            Path to the local PDB file.
        """
        local_path = Path(PDB_SETTINGS.cache_dir) / f"{pdb_code}.pdb"
        if not local_path.exists():
            logger.info(f"Downloading PDB structure: {pdb_code}")
            DownloadPDBStructure()._run(pdb_code=pdb_code)
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
            ValueError: If no SEQRES records are found.
        """
        with pdb_file.open("r") as f:
            seqres_lines = [line for line in f if line.startswith("SEQRES")]

        if not seqres_lines:
            raise ValueError("No SEQRES records found in the PDB file.")

        chain_id = seqres_lines[0][11]
        sequence = "".join(
            seq1(res) for line in seqres_lines for res in line[19:].split() if line[11] == chain_id
        )

        return chain_id, sequence

    @staticmethod
    def one_to_three(one_letter_code: str) -> str:
        """
        Convert a one-letter amino acid code to its three-letter equivalent.

        Args:
            one_letter_code: A single character representing an amino acid.

        Returns:
            The three-letter code for the amino acid, or 'UNK' if not recognized.

        Raises:
            ValueError: If the input is not a single character.
        """
        if not isinstance(one_letter_code, str) or len(one_letter_code) != 1:
            raise ValueError(
                f"Invalid one-letter code: {one_letter_code}. Expected a single character."
            )

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
    def find_mutations(original_sequence: str, target_sequence: str) -> List[str]:
        """
        Identify mutations needed to transform the original sequence into the target sequence.

        Args:
            original_sequence: The original amino acid sequence.
            target_sequence: The target amino acid sequence.

        Returns:
            A list of mutation strings in the format 'OriginalAA{position}NewAA'.
        """
        return [
            f"{orig}{i}{target}"
            for i, (orig, target) in enumerate(zip(original_sequence, target_sequence), start=1)
            if orig != target
        ]

    @staticmethod
    def perform_mutations(pdb_file: Path, mutations: List[str], output_file: Path) -> None:
        """
        Apply specified mutations to a protein structure using PyMOL.

        Args:
            pdb_file: Path to the input PDB file.
            mutations: List of mutations to perform.
            output_file: Path to save the mutated structure.

        Raises:
            RuntimeError: If PyMOL fails to perform mutations.
        """
        from pymol import cmd

        cmd.load(str(pdb_file), "protein")
        cmd.wizard("mutagenesis")

        for mutation in mutations:
            _, pos, new = mutation[0], mutation[1:-1], mutation[-1]
            cmd.get_wizard().set_mode(Mutagenesis.one_to_three(new))
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

        atoms1 = [residue["CA"] for residue in structure1.get_residues() if residue.has_id("CA")]
        atoms2 = [residue["CA"] for residue in structure2.get_residues() if residue.has_id("CA")]

        if not atoms1 or not atoms2:
            raise ValueError("No CA atoms found in one or both structures.")

        sup = Superimposer()
        sup.set_atoms(
            atoms1[: min(len(atoms1), len(atoms2))], atoms2[: min(len(atoms1), len(atoms2))]
        )

        return cast(float, sup.rms)

    def _run(self, pdb_code: str, target_sequence: str, perform_rmsd: bool = False) -> str:
        """
        Execute the mutagenesis process on a given protein structure.

        Args:
            pdb_code: The 4-character PDB code of the protein to mutate.
            target_sequence: The target amino acid sequence.
            perform_rmsd: Whether to calculate RMSD after mutation (default False).

        Returns:
            A string containing the results of the mutagenesis process.

        Raises:
            ValueError: If the mutagenesis process fails at any step.
        """
        try:
            pdb_file = self.get_pdb_file(pdb_code)
            _, original_sequence = self.extract_full_sequence(pdb_file)
            mutations = self.find_mutations(original_sequence, target_sequence)

            output_file = MUTAGENESIS_SETTINGS.mutated_pdb / f"{pdb_code}_mutated.pdb"
            self.perform_mutations(pdb_file, mutations, output_file)

            result = f"Mutations performed: {', '.join(mutations)}. Mutated structure saved to: {output_file}."

            if perform_rmsd:
                rmsd = self.calculate_rmsd(pdb_file, output_file)
                result += f" RMSD between original and mutated structure: {rmsd:.4f} Å."

            return result
        except Exception as e:
            logger.error(f"Failed to perform mutagenesis: {e}")
            raise ValueError(f"Failed to perform mutagenesis: {e}")

    async def _arun(self, *args, **kwargs) -> str:
        """
        Async method for Mutagenesis.

        Raises:
            NotImplementedError: Async execution is not implemented.
        """
        raise NotImplementedError("Async execution not implemented for Mutagenesis.")
