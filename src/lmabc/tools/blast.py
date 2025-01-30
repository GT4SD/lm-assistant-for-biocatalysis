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
import random
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
from Bio import SeqIO
from pydantic_settings import BaseSettings, SettingsConfigDict
from tabulate import tabulate

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

    db: Path = BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("blast") / "blastdb"

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
        This tool facilitates the execution of a BLASTP search using a specified query protein sequence.

        Key Features:
        - Users can choose the database to search against (default: `swissprot`).
        - Users can specify an experiment ID for better tracking. If not provided, a default ID is generated.
        - If the selected database is not available, instructions will be provided on how to install it.
        - Results are stored in a dedicated folder for each experiment.
        - Only explicitly requested parameters are modified.

        BLASTP Arguments:
        - `query`: The protein sequence as a string.
        - `experiment_id`: A unique identifier for this run (optional).
        - `database_name`: The name of the BLAST database to use (default: `swissprot`).
        - `evalue`: The E-value threshold for reporting matches (default: `1e-5`).
        - `outfmt`: The output format (default: `6`).
        - `max_target_seqs`: The maximum number of aligned sequences to keep (default: `10`).
        - Additional BLASTP arguments can be passed as keyword arguments (e.g., `gapopen=11`).
        Only valid BLASTP arguments are accepted. Invalid arguments will raise an error.

        Example Usage:
        ```python
        tool.run(
            query="MY_PROTEIN_SEQUENCE",
            database_name="swissprot",
            evalue=1e-5,
            outfmt=6,
            max_target_seqs=10,
            gapopen=11  # Additional valid BLASTP argument
        )
        ```

        Example Output:
        ```
        BLASTP Search Results

        Query Sequence:
        Database Used:
        Experiment ID (if present):

        --------------------------------------------------------
        | Accession  | Identity (%) | E-Value  | Bit Score | Description                           |
        --------------------------------------------------------
        | XXX   | XX.X        | X    | X     | X         |
        | XXX   | XX.X        | X    | X     | X         |
        | XXX   | XX.X        | X    | X     | X         |
        --------------------------------------------------------

        Results Saved in: "OUT_FILE"
        ```

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

    def _run(
        self,
        query: str,
        experiment_id: Optional[str] = None,
        database_name: Optional[str] = "swissprot",
        evalue: Optional[float] = None,
        outfmt: Optional[str] = None,
        max_target_seqs: Optional[int] = None,
        **kwargs,
    ) -> str:
        """
        Run the Blastp tool on the provided query sequence with dynamically provided parameters.

        Args:
            query: The protein sequence as a string.
            experiment_id: A unique identifier for this run. If None, generate one based on timestamp + random number.
            database_name: The name of the BLAST database to use (default: swissprot).
            evalue: The E-value threshold for reporting matches.
            outfmt: The output format.
            max_target_seqs: The maximum number of aligned sequences to keep.
            **kwargs: Additional BLASTP arguments to pass directly to the command. Must be valid BLASTP arguments.

        Returns:
            A formatted message with result details.

        Raises:
            ValueError: If an invalid BLASTP argument is provided in `**kwargs`.
        """
        valid_blastp_args = {
            "query",
            "db",
            "evalue",
            "outfmt",
            "max_target_seqs",
            "out",
            "gapopen",
            "gapextend",
            "matrix",
            "word_size",
            "threshold",
            "comp_based_stats",
            "seg",
            "soft_masking",
            "lcase_masking",
            "subject",
            "subject_loc",
            "query_loc",
            "qcov_hsp_perc",
            "max_hsps",
            "num_threads",
            "remote",
            "html",
            "show_gis",
            "parse_deflines",
            "num_descriptions",
            "num_alignments",
            "line_length",
            "html",
            "max_target_seqs",
            "ungapped",
            "use_sw_tback",
        }

        invalid_args = set(kwargs.keys()) - valid_blastp_args
        if invalid_args:
            raise ValueError(
                f"The following arguments are not valid BLASTP arguments: {invalid_args}. "
                f"Valid arguments are: {valid_blastp_args}"
            )

        try:
            settings = BLAST_SETTINGS
            settings.trash_dir.mkdir(parents=True, exist_ok=True)

            if experiment_id is None:
                experiment_id = (
                    datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{random.randint(1000,9999)}"
                )

            experiment_folder = settings.trash_dir / experiment_id
            experiment_folder.mkdir(parents=True, exist_ok=True)

            fasta_file_path = experiment_folder / "query.fasta"
            output_file_path = experiment_folder / "blast_output.txt"
            accession_file_path = experiment_folder / "hit_accessions.txt"
            sequences_output_file = experiment_folder / "full_sequences.fasta"
            merged_output_file = experiment_folder / "merged_results.json"

            with fasta_file_path.open("w") as fasta_file:
                fasta_file.write(f">query_sequence\n{query}\n")

            blastdb_path = (
                BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("blast") / "blastdb"
            )

            if database_name is None:
                database_name = "swissprot"
            selected_db_path = blastdb_path / database_name

            if not any(
                selected_db_path.with_suffix(ext).exists() for ext in [".pin", ".psq", ".phr"]
            ):
                return f"""
                Error: BLAST database `{database_name}` not found!
                
                Expected location: `{selected_db_path}`
                
                To install `{database_name}`, run:
                ```
                update_blastdb.pl --decompress {database_name}
                ```
                Ensure it is installed in: `{blastdb_path}`
                """

            effective_evalue = evalue if evalue is not None else settings.evalue
            effective_outfmt = outfmt if outfmt is not None else settings.outfmt
            effective_max_target_seqs = (
                max_target_seqs if max_target_seqs is not None else settings.max_target_seqs
            )

            command: List[Any] = [
                "blastp",
                "-query",
                str(fasta_file_path),
                "-db",
                str(selected_db_path),
                "-evalue",
                str(effective_evalue),
                "-outfmt",
                str(effective_outfmt),
                "-max_target_seqs",
                str(effective_max_target_seqs),
                "-out",
                str(output_file_path),
            ]

            for key, value in kwargs.items():
                command.extend([f"-{key}", str(value)])

            result = subprocess.run(command, check=True, capture_output=True, text=True)
            if result.returncode != 0:
                raise ValueError(f"BLASTP search failed with exit code {result.returncode}")

            self._extract_accessions(str(output_file_path), str(accession_file_path))
            self._fetch_full_sequences(
                db=str(selected_db_path),
                accession_file=str(accession_file_path),
                sequences_output=str(sequences_output_file),
            )
            self._merge_hits_and_sequences(
                blastp_output=str(output_file_path),
                sequences_output=str(sequences_output_file),
                merged_output=str(merged_output_file),
            )

            df = pd.read_json(f"{merged_output_file}", orient="records", lines=True)
            formatted_results = tabulate(
                df[["subject", "perc_identity", "evalue", "bit_score", "description"]],
                headers=["Accession", "Identity (%)", "E-Value", "Bit Score", "Description"],
                tablefmt="pretty",
            )

            return f"""
            BLASTP Search Completed Successfully!

            Results saved in: `{experiment_folder}`
            - Query FASTA File: `{fasta_file_path}`
            - BLAST Output File: `{output_file_path}`
            - Accession File: `{accession_file_path}`
            - Sequences File: `{sequences_output_file}`
            - Merged JSON Results: `{merged_output_file}`

            Database Used: `{database_name}`

            Top Matches:
            {formatted_results}

            Total Matches Found: {len(df)}
            """

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
