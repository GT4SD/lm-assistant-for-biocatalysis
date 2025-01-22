"""Blast tools and utilities"""

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
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from Bio import SeqIO
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..configuration import BIOCATALYSIS_AGENT_CONFIGURATION
from .core import BiocatalysisAssistantBaseTool

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class BlastpSettings(BaseSettings):
    """
    Configuration values for the Blastp.

    Attributes:
        db: The database to use for the BLASTP search.
        evalue: The E-value threshold for reporting matches.
        outfmt: The output format.
        max_target_seqs: The maximum number of aligned sequences to keep.
        trash_dir: Directory to store temporary files like the FASTA query and BLAST output.
    """

    db: Path = BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("blast") / "blastdb/swissprot"
    evalue: float = 1e-5
    outfmt: str = "6"
    max_target_seqs: int = 5
    trash_dir: Path = BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("blast") / "blast_logs"

    model_config = SettingsConfigDict(env_prefix="BLASTP_")


BLAST_SETTINGS = BlastpSettings()
DEFAUL_DB = BLAST_SETTINGS.db


class Blastp(BiocatalysisAssistantBaseTool):
    """
    Tool for performing a BLASTP search using a query protein sequence.

    Attributes:
        name: Name of the tool.
        description: Description of the tool.
    """

    name: str = "Blastp"
    description: str = """
                    This tool must be executed on the system. This tool facilitates the execution of a BLASTP search using a specified query protein sequence. Before starting set parameters to {} unless some specific parameters are required!
                    Importantly, any parameter not explicitly specified for modification should remain unchanged, ensuring the
                    integrity of the default or pre-set configurations. Change only the parameters that have been explicitly asked to be changed.
                    If asked to only find a certain amount of sequences, the only parameter to change is max_target_seqs.
                    More details about blast arguments:
                    Here are more info about the different arguments
                    -query <File_In>
                    Input file name
                    -db <String>
                    BLAST database name or path. As Default value {DEFAUL_DB}
                    -evalue <Real>
                    Expectation value (E) threshold for saving hits. Default = 1e-5
                    -out <File_Out, file name length < 256>
                    Output file name
                    -outfmt 6
                    -max_target_seqs <Integer, >=1>
                    Default = '10'
                    """

    @classmethod
    def check_requirements(cls) -> bool:
        """
        Check if the required directories for BLASTP exist.

        Returns:
            True if all required directories exist, False otherwise.
        """
        settings = BLAST_SETTINGS
        if not Path(settings.db).parent.exists():
            logger.warning(f"Database directory {Path(settings.db).parent} does not exist.")
            return False
        if not settings.trash_dir.exists():
            logger.warning(f"Trash directory {settings.trash_dir} does not exist.")
            return False
        return True

    def _run(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Run the Blastp tool on the provided query sequence with dynamically provided parameters.

        Args:
            query: The protein sequence as a string.
            parameters: A dictionary of parameters to override the BLASTP search settings. The default setting is parameters = {}.

        Returns:
            The path to the file containing the BLASTP results.

        Raises:
            ValueError: If the BLASTP command fails.
        """
        try:
            settings = BLAST_SETTINGS
            settings.trash_dir.mkdir(parents=True, exist_ok=True)
            fasta_file_path = settings.trash_dir / "query.fasta"
            with fasta_file_path.open("w") as fasta_file:
                fasta_file.write(f">query_sequence\n{query}\n")

            effective_settings = settings.model_dump()
            if parameters:
                effective_settings.update(parameters)

            output_file_path = settings.trash_dir / "blast_output.txt"
            effective_settings["out"] = output_file_path

            command: List[Any] = [
                "blastp",
                "-query",
                str(fasta_file_path),
                "-db",
                effective_settings["db"],
                "-evalue",
                str(effective_settings["evalue"]),
                "-outfmt",
                str(effective_settings["outfmt"]),
                "-max_target_seqs",
                str(effective_settings["max_target_seqs"]),
                "-out",
                str(effective_settings["out"]),
            ]

            result = subprocess.run(command, check=True, capture_output=True, text=True)
            if result.returncode != 0:
                raise ValueError(f"BLASTP search failed with exit code {result.returncode}")

            accession_file_path = settings.trash_dir / "hit_accessions.txt"
            self._extract_accessions(str(output_file_path), str(accession_file_path))

            sequences_output_file = settings.trash_dir / "full_sequences.fasta"
            self._fetch_full_sequences(
                db=str(effective_settings["db"]),
                accession_file=str(accession_file_path),
                sequences_output=str(sequences_output_file),
            )

            merged_output_file = settings.trash_dir / "merged_blastp_results.json"
            self._merge_hits_and_sequences(
                blastp_output=str(output_file_path),
                sequences_output=str(sequences_output_file),
                merged_output=str(merged_output_file),
            )

            df = pd.read_json(f"{merged_output_file}", orient="records", lines=True).to_dict(
                "records"
            )
            return f"The results have been saved to {merged_output_file}, and here is the data inside the result {df}"

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running Blastp: {e.stderr}")
            raise ValueError("Failed to perform BLASTP search") from e

    def _extract_accessions(self, blastp_output: str, accession_file: str):
        """
        Extracts hit accessions from BLASTP output using awk.

        Args:
            blastp_output: Path to the BLASTP output file.
            accession_file: Path to the file where the extracted accessions will be saved.

        Raises:
            ValueError: If the extraction fails.
        """
        try:
            awk_command = f"awk '{{print $2}}' {blastp_output} > {accession_file}"
            subprocess.run(awk_command, shell=True, check=True)
            logger.info(f"Hit accessions saved to {accession_file}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting accessions: {e.stderr}")
            raise ValueError("Failed to extract hit accessions") from e

    def _fetch_full_sequences(self, db: str, accession_file: str, sequences_output: str):
        """
        Fetches full sequences from the BLAST database using the extracted accessions.

        Args:
            db: Path to the BLAST database.
            accession_file: Path to the file with hit accessions.
            sequences_output: Path to the file where the full sequences will be saved.

        Raises:
            ValueError: If the sequence fetching fails.
        """
        try:
            blastdbcmd_command = [
                "blastdbcmd",
                "-db",
                db,
                "-entry_batch",
                accession_file,
                "-out",
                sequences_output,
            ]
            subprocess.run(blastdbcmd_command, check=True)
            logger.info(f"Full sequences saved to {sequences_output}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error fetching full sequences: {e.stderr}")
            raise ValueError("Failed to fetch full sequences") from e

    def _merge_hits_and_sequences(
        self, blastp_output: str, sequences_output: str, merged_output: str
    ):
        """
        Merge BLASTP hits and full sequences and descriptions into a single file.

        Args:
            blastp_output: Path to the BLASTP output file (tabular format).
            sequences_output: Path to the full sequences file (FASTA format).
            merged_output: Path to the file where the merged results will be saved.
        """
        try:
            blastp_df = pd.read_csv(blastp_output, sep="\t", header=None)
            blastp_df.columns = [
                "query",
                "subject",
                "perc_identity",
                "alignment_length",
                "mismatches",
                "gap_opens",
                "q_start",
                "q_end",
                "s_start",
                "s_end",
                "evalue",
                "bit_score",
            ]

            sequences_dict = {
                record.id: str(record.seq) for record in SeqIO.parse(sequences_output, "fasta")
            }
            descriptions_dict = {
                record.id: str(record.description)
                for record in SeqIO.parse(sequences_output, "fasta")
            }

            blastp_df["sequence"] = blastp_df["subject"].map(sequences_dict)
            blastp_df["description"] = blastp_df["subject"].map(descriptions_dict)

            blastp_df.to_json(merged_output, orient="records", lines=True)
            logger.info(f"Merged results saved to {merged_output}")
        except Exception as e:
            logger.error(f"Error merging hits and sequences: {e}")
            raise ValueError("Failed to merge BLASTP hits and sequences") from e

    async def _arun(self, *args, **kwargs) -> str:
        """Async method for blastp."""
        raise NotImplementedError("Async execution not implemented for Blastp.")
