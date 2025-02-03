"""PDB tools and utilities."""

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

import requests
from pydantic_settings import BaseSettings, SettingsConfigDict
from rcsbsearchapi.search import SequenceQuery

from ..configuration import BIOCATALYSIS_AGENT_CONFIGURATION
from .core import BiocatalysisAssistantBaseTool

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class PDBConfiguration(BaseSettings):
    """Configuration values for the PDB tool."""

    output_dir: str = str(BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("pdb"))
    evalue_cutoff: int = 1
    identity_cutoff: float = 1

    model_config = SettingsConfigDict(env_prefix="PDB_")


PDB_SETTINGS = PDBConfiguration()


class FindPDBStructure(BiocatalysisAssistantBaseTool):
    """Tool for finding the PDB structure of a protein sequence."""

    name: str = "FindPDBStructure"
    description: str = """
    This tool must be executed on the system.
    Given a protein sequence, FindPDBStructure uses RCSB Search API to find protein structures (also known as PDB structures or 3D structures) related to a given protein sequence.
    It takes as input a protein sequence.
    """

    def _run(self, protein_sequence: str) -> str:
        """Run FindPDBStructure."""
        try:
            results = SequenceQuery(
                protein_sequence,
                PDB_SETTINGS.evalue_cutoff,
                PDB_SETTINGS.identity_cutoff,
            )
            pdb_ids = [polyid for polyid in results("polymer_entity")]

            for tmp_pdb in pdb_ids:
                entry_id, entity_id = tmp_pdb.split("_")
                url = f"https://data.rcsb.org/rest/v1/core/polymer_entity/{entry_id}/{entity_id}"
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        tmp_target_sequence = data["entity_poly"]["pdbx_seq_one_letter_code_can"]
                        if tmp_target_sequence == protein_sequence:
                            return f"pdb code {entry_id} with entity id {entity_id}"
                except Exception as e:
                    logger.warning(f"Failed to fetch data for {entry_id}_{entity_id}: {e}")
                    continue

            return "Couldn't find a perfect match"

        except Exception as e:
            logger.error(f"Error in FindPDBStructure: {e}")
            raise ValueError("Failed to get elements of reaction.")

    async def _arun(self, protein_sequence: str) -> str:
        """
        Async method for finding pdb structures of a given protein sequence..

        Raises:
            NotImplementedError: Async execution is not implemented.
        """
        raise NotImplementedError("Async execution not implemented for FindPDBStructure.")


class DownloadPDBStructure(BiocatalysisAssistantBaseTool):
    """Tool for downloading a PDB structure file given a PDB code."""

    name: str = "DownloadPDBStructure"
    description: str = """
    This tool must be executed on the system.
    Given a PDB code, DownloadPDBStructure downloads the corresponding PDB structure file from the RCSB PDB database.
    It takes as input a PDB code (e.g., '1abc') and saves the PDB file in the configured output directory.

    This tool must be used only and only if the user asks to download it or strictly needed!
    """

    @staticmethod
    def check_requirements() -> bool:
        """
        Check if the required directories for PDB file download exist.
        Returns:
            True if all required directories exist, False otherwise.
        """
        output_dir = Path(PDB_SETTINGS.output_dir)
        if not output_dir.exists():
            logger.warning(f"Required directory {output_dir} does not exist.")
            return False
        return True

    def _run(self, pdb_code: str) -> str:
        """
        Download a PDB structure file.

        Args:
            pdb_code: The PDB code of the structure to download.

        Returns:
            A string message indicating success or failure of the download.

        Raises:
            ValueError: If the PDB file download fails.
        """
        try:
            pdb_code = pdb_code.lower()
            url = f"https://files.rcsb.org/download/{pdb_code}.pdb"
            response = requests.get(url)

            if response.status_code == 200:
                output_path = Path(PDB_SETTINGS.output_dir) / f"{pdb_code}.pdb"
                with output_path.open("wb") as f:
                    f.write(response.content)
                return f"Successfully downloaded PDB file: {output_path}"
            else:
                return f"Error: {response.status_code}, Failed to download PDB file for {pdb_code}"

        except Exception as e:
            logger.error(f"Error in DownloadPDBStructure: {e}")
            raise ValueError(f"Failed to download PDB file for {pdb_code}.")

    async def _arun(self, pdb_code: str) -> str:
        """
        Async method for downloading a PDB structure file.

        Raises:
            NotImplementedError: Async execution is not implemented.
        """
        raise NotImplementedError("Async execution not implemented for DownloadPDBStructure.")
