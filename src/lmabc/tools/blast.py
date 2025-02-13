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
from pydantic_settings import BaseSettings, SettingsConfigDict
from tabulate import tabulate

from ..configuration import BIOCATALYSIS_AGENT_CONFIGURATION
from .blast_utils import BLAST_OPTIONS, BLAST_OUTPUT_FORMATS, BLAST_SPECIFIERS
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
    outfmt: str = "6 sseqid pident evalue bitscore stitle sseq"
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

        settings = BLAST_SETTINGS
        invalid_options = set(kwargs.keys()) - set(BLAST_OPTIONS.keys())
        effective_evalue = evalue if evalue is not None else settings.evalue
        effective_outfmt = outfmt if outfmt is not None else settings.outfmt
        effective_max_target_seqs = (
            max_target_seqs if max_target_seqs is not None else settings.max_target_seqs
        )
        first, *rest = effective_outfmt.split(" ")
        invalid_outfmt = set({first}) - set(BLAST_OUTPUT_FORMATS.keys())
        invalid_specifiers = set(rest) - set(BLAST_SPECIFIERS.keys())
        if any((invalid_options, invalid_outfmt, invalid_specifiers)):
            raise ValueError("Invalid arguments, please check your inputs")

        try:
            settings.trash_dir.mkdir(parents=True, exist_ok=True)

            if experiment_id is None:
                experiment_id = (
                    datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{random.randint(1000,9999)}"
                )

            experiment_folder = settings.trash_dir / experiment_id
            experiment_folder.mkdir(parents=True, exist_ok=True)

            fasta_file_path = experiment_folder / "query.fasta"
            output_file_path = experiment_folder / "blast_output.txt"

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

            command: List[Any] = [
                "blastp",
                "-query",
                str(fasta_file_path),
                "-db",
                str(selected_db_path),
                "-evalue",
                str(effective_evalue),
                "-outfmt",
                f"{str(effective_outfmt)}",
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

            columns = [BLAST_SPECIFIERS[key] for key in rest if key in BLAST_SPECIFIERS]
            df = pd.read_csv(output_file_path, sep="\t", header=None, names=columns)
            formatted_results = tabulate(
                df,
                headers=columns,
                tablefmt="pretty",
            )

            return f"""
            BLASTP Search Completed Successfully!

            Results saved in: `{experiment_folder}`
            - Query FASTA File: `{fasta_file_path}`
            - BLAST Output File: `{output_file_path}`

            Database Used: `{database_name}`

            Top Matches:
            {formatted_results}

            Total Matches Found: {len(df)}
            """

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running Blastp: {e.stderr}")
            raise ValueError("Failed to perform BLASTP search") from e

    async def _arun(self, *args, **kwargs) -> str:
        """Async method for blastp."""
        raise NotImplementedError("Async execution not implemented for Blastp.")
