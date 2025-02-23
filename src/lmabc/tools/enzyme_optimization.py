"""Enzyme optimization tools and utilities."""

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
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from enzeptional import (  # type: ignore
    CrossoverGenerator,
    EnzymeOptimizer,
    HuggingFaceEmbedder,
    HuggingFaceModelLoader,
    HuggingFaceTokenizerLoader,
    SelectionGenerator,
    SequenceMutator,
    SequenceScorer,
)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from tabulate import tabulate
from transformers import logging as transformers_logging

from ..configuration import BIOCATALYSIS_AGENT_CONFIGURATION
from .core import BiocatalysisAssistantBaseTool

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

transformers_logging.set_verbosity_error()


class EnzeptinalConfiguration(BaseSettings):
    """Configuration values for the Enzeptinal tool."""

    scorer_type: str = Field(
        default="feasibility",
        description="Type of scoring model ('feasibility' or 'kcat').",
    )
    num_iterations: int = Field(default=2, description="Number of optimization iterations.")
    num_sequences: int = Field(default=3, description="Number of sequences to optimize.")
    num_mutations: int = Field(default=5, description="Number of mutations per iteration.")
    time_budget: int = Field(default=3600, description="Time budget for optimization in seconds.")
    batch_size: int = Field(default=2, description="Batch size for optimization.")
    top_k: int = Field(default=2, description="Top K sequences to consider.")
    selection_ratio: float = Field(default=0.25, description="Selection ratio for optimization.")
    tool_dir: Path = Field(
        default=BIOCATALYSIS_AGENT_CONFIGURATION.get_tool_dir("enzyme_optimization"),
        description="Tool directory.",
    )
    cache_dir: Path = Field(
        default_factory=lambda: BIOCATALYSIS_AGENT_CONFIGURATION.get_tool_cache_dir(
            "enzyme_optimization"
        )
        / "output",
        description="Cache directory",
    )
    output_filename: str = Field(
        default="OptimizationOutput.json", description="Filename of the output file."
    )
    perform_crossover: bool = Field(default=True, description="Perform crossover.")
    crossover_type: str = Field(
        default="single_point",
        description="Type of crossover in case perform_crossover is True.",
    )
    pad_intervals: bool = Field(
        default=False, description="Pad interval to minimum_interval_length."
    )
    minimum_interval_length: int = Field(
        default=8, description="Minimum length per interval during padding."
    )
    seed: int = Field(default=42, description="Random seed.")

    model_config = SettingsConfigDict(env_prefix="ENZEPTINAL_")


ENZEPTIONAL_SETTINGS = EnzeptinalConfiguration()

ENZEPTIONAL_DESCRIPTION = """ OptimizeEnzymeSequences (Enzeptional) - Enzyme Sequence Optimization Tool

    Description:
    This tool optimizes enzyme sequences for biocatalytic reactions, enhancing catalytic efficiency and substrate specificity. The tool applies mutation in the intervals to optimize the reaction. The sequence optimized can be refered to as wildtype.

    Required Input Parameters:
    1. `substrate_smiles` (str) - SMILES representation of the reactant molecule.
    2. `product_smiles` (str) - SMILES representation of the desired product molecule.
    3. `protein_sequence` (str) - Amino acid sequence of the enzyme to optimize.
    4. `scorer_type` (str) - The scoring model type, either `'feasibility'` (default) or `'kcat'`.

    Optional Parameters:
    - `intervals` (List[List[int]]) - List of regions (start, end) to focus mutations on.
    - `num_iterations` (int) - Number of optimization iterations. Default: 2.
    - `num_sequences` (int) - Number of sequences optimized per iteration. Default: 5.
    - `num_mutations` (int) - Number of mutations per iteration. Default: 5.
    - `time_budget` (int) - Max optimization time (seconds). Default: 3600.
    - `batch_size` (int) - Number of sequences processed in parallel. Default: 5.
    - `top_k` (int) - Top sequences to consider per iteration. Default: 3.
    - `selection_ratio` (float) - Fraction of top sequences selected for the next iteration. Default: 0.25.
    - `perform_crossover` (bool) - Whether to apply sequence crossover. Default: True.
    - `crossover_type` (str) - Type of crossover (`'sp_crossover'`, `'uniform_crossover'`). Default: `'sp_crossover'`.
    - `pad_intervals` (bool) - Whether to pad mutation regions. Default: False.
    - `minimum_interval_length` (int) - Min length for padded intervals. Default: 8.
    - `seed` (int) - Random seed for reproducibility. Default: 42.
    - `number_of_results` (int) - Number of optimized sequences to return. Default: 10.

    Output (Tabulated Format):
    The tool returns a table of optimized enzyme sequences ranked by predicted performance for the given reaction.

    Example output:

    +--------+-----------------------------+--------+
    | Index  | Sequence                    | Score  |
    +--------+-----------------------------+--------+
    | 1      | MVLSPADKTNVKAA...           | 0.9200 |
    | 2      | MVLAPADKTNVKAA...           | 0.8900 |
    | 3      | MVLSPADRTNVKAA...           | 0.8750 |
    | 4      | MVLSAADRNVKAA...            | 0.8600 |
    | 5      | MVLSPADRKVKAA...            | 0.8450 |
    +--------+-----------------------------+--------+

    Usage:
    ```python
    result = tool._run(
        substrate_smiles="CCOCC",
        product_smiles="CCO",
        protein_sequence="MVLSPADKTNVKAA...",
        scorer_type="feasibility",
        number_of_results=5,
        
    )
    ```

"""


class ModelFactory:
    """Factory class for creating model-related components such as embedders."""

    @staticmethod
    def create_embedder(model_path: str, tokenizer_path: str) -> HuggingFaceEmbedder:
        """Create a HuggingFace embedder for a given model and tokenizer.

        Args:
            model_path: Path to the HuggingFace model.
            tokenizer_path: Path to the HuggingFace tokenizer.

        Returns:
            An embedder instance initialized with the given model and tokenizer.
        """
        model_loader = HuggingFaceModelLoader()
        tokenizer_loader = HuggingFaceTokenizerLoader()
        return HuggingFaceEmbedder(
            model_loader=model_loader,
            tokenizer_loader=tokenizer_loader,
            model_path=model_path,
            tokenizer_path=tokenizer_path,
            cache_dir=None,
            device="cpu",
        )


class OptimizerFactory:
    """Factory class for creating enzyme optimization components such as the optimizer."""

    @staticmethod
    def create_optimizer(
        protein_sequence: str,
        substrate_smiles: str,
        product_smiles: str,
        intervals: List[List[int]],
        scorer_path: str,
        scaler_path: Optional[str],
        use_xgboost_scorer: bool,
    ) -> EnzymeOptimizer:
        """Create an enzyme optimizer instance.

        Args:
            protein_sequence: The amino acid sequence of the enzyme to be optimized.
            substrate_smiles: SMILES representation of the substrate molecule.
            product_smiles: SMILES representation of the product molecule.
            intervals: Specific regions of the protein sequence to focus mutations on.
            scorer_path: Path to the scoring model.
            scaler_path: Path to the scaler model, if applicable.
            use_xgboost_scorer: Whether to use an XGBoost-based scorer.

        Returns:
            EnzymeOptimizer: An instance of the enzyme optimizer initialized with the given parameters.
        """
        language_model_path = "facebook/esm2_t33_650M_UR50D"
        chem_model_path = "seyonec/ChemBERTa-zinc-base-v1"

        protein_model = ModelFactory.create_embedder(language_model_path, language_model_path)
        chem_model = ModelFactory.create_embedder(chem_model_path, chem_model_path)

        mutation_config = {
            "type": "language-modeling",
            "embedding_model_path": language_model_path,
            "tokenizer_path": language_model_path,
            "unmasking_model_path": language_model_path,
        }

        mutator = SequenceMutator(sequence=protein_sequence, mutation_config=mutation_config)
        mutator.set_top_k(ENZEPTIONAL_SETTINGS.top_k)

        scorer = SequenceScorer(
            protein_model=protein_model,
            scorer_filepath=scorer_path,
            use_xgboost=use_xgboost_scorer,
            scaler_filepath=scaler_path,
        )

        concat_order = ["substrate", "sequence"]
        if not use_xgboost_scorer:
            concat_order.append("product")

        return EnzymeOptimizer(
            sequence=protein_sequence,
            mutator=mutator,
            scorer=scorer,
            intervals=intervals,
            substrate_smiles=substrate_smiles,
            product_smiles=product_smiles,
            chem_model=chem_model,
            selection_generator=SelectionGenerator(),
            crossover_generator=CrossoverGenerator(),
            concat_order=concat_order,
            batch_size=ENZEPTIONAL_SETTINGS.batch_size,
            selection_ratio=ENZEPTIONAL_SETTINGS.selection_ratio,
            perform_crossover=ENZEPTIONAL_SETTINGS.perform_crossover,
            crossover_type=ENZEPTIONAL_SETTINGS.crossover_type,
            pad_intervals=ENZEPTIONAL_SETTINGS.pad_intervals,
            minimum_interval_length=ENZEPTIONAL_SETTINGS.minimum_interval_length,
            seed=ENZEPTIONAL_SETTINGS.seed,
        )


class OptimizeEnzymeSequences(BiocatalysisAssistantBaseTool):
    """Tool for optimizing enzyme sequences using Enzeptinal."""

    name: str = "OptimizeEnzymeSequences"
    description: str = ENZEPTIONAL_DESCRIPTION

    @staticmethod
    def check_requirements() -> bool:
        """
        Check if the required directories and files for enzyme optimization exist.
        If a required directory does not exist, attempt to create it.

        Returns:
            True if all required directories exist or were successfully created,
            False if any directory creation fails.
        """
        settings = ENZEPTIONAL_SETTINGS

        paths_to_check = [
            settings.tool_dir,
            settings.tool_dir / "models",
            settings.cache_dir,
        ]

        for path in paths_to_check:
            if not path.exists():
                logger.warning(f"Directory {path} does not exist. Creating it now.")
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    logger.error(f"Could not create directory {path}: {e}")
                    return False

        return True

    def _run(
        self,
        substrate_smiles: str,
        product_smiles: str,
        protein_sequence: str,
        scorer_type: str = "feasibility",
        intervals: Optional[List[List[int]]] = [],
        number_of_results: Optional[int] = 10,
        **kwargs,
    ) -> str:
        """
        Run enzyme sequence optimization.

        Args:
            substrate_smiles: SMILES string of the substrate.
            product_smiles: SMILES string of the product.
            protein_sequence: Amino acid sequence of the protein.
            scorer_type: Type of scorer to use (default: "feasibility").
            intervals: List of intervals for mutation (default: []).
            number_of_results: Number of results to return (default: 10).

        Returns:
            A formatted string containing the optimization results.

        Raises:
            ValueError: If input validation fails or optimization fails.
        """
        if not substrate_smiles or not product_smiles or not protein_sequence:
            return "Error: Missing required input parameters. Please provide substrate_smiles, product_smiles, and protein_sequence."

        if scorer_type not in ["feasibility", "kcat"]:
            return f"Error: Invalid scorer_type '{scorer_type}'. Must be either 'feasibility' or 'kcat'."

        if number_of_results is None or number_of_results < 1:
            number_of_results = 10

        try:
            if not protein_sequence.isalpha():
                return "Error: Invalid protein sequence. Must contain only amino acid letters."

            config = ENZEPTIONAL_SETTINGS.model_copy(update=kwargs)
            use_xgboost_scorer = scorer_type == "kcat"
            scorer_path, scaler_path = self._get_model_paths(scorer_type)

            if not intervals:
                intervals = [[0, len(protein_sequence)]]
            else:
                for start, end in intervals:
                    if start < 0 or end > len(protein_sequence) or start >= end:
                        return f"Error: Invalid interval [{start}, {end}]. Must be within sequence length (0-{len(protein_sequence)})."

            optimizer = OptimizerFactory.create_optimizer(
                protein_sequence,
                substrate_smiles,
                product_smiles,
                intervals,
                scorer_path,
                scaler_path,
                use_xgboost_scorer,
            )

            optimized_sequences = optimizer.optimize(
                num_iterations=config.num_iterations,
                num_sequences=config.num_sequences,
                num_mutations=config.num_mutations,
                time_budget=config.time_budget,
            )

            optimized_sequences = [
                d for d in optimized_sequences if d["sequence"] != protein_sequence
            ]

            optimized_sequences = list(
                {seq["sequence"]: seq for seq in optimized_sequences}.values()
            )

            if not optimized_sequences:
                return "No improved sequences found."

            filename: Path = config.cache_dir / config.output_filename
            self._save_results(results=optimized_sequences, filename=filename)

            df = pd.read_json(f"{filename}", orient="records", lines=True).head(number_of_results)

            table_data = [
                [idx, row["sequence"], f"{row['score']:.4f}"]
                for idx, row in enumerate(df.to_dict("records"), 1)
            ]
            result = f"Found {len(table_data)} optimized sequences.\n\n" + tabulate(
                table_data, headers=["Index", "Sequence", "Score"], tablefmt="grid"
            )

            return result

        except Exception as e:
            logger.error(f"Error in OptimizeEnzymeSequences: {e}")
            return f"Error during optimization: {str(e)}"

    def _get_model_paths(self, scorer_type: str = "feasibility") -> Tuple[str, Optional[str]]:
        """
        Get paths for the scorer model and scaler.

        Args:
            scorer_type: Type of scorer (default: "feasibility").

        Returns:
            Tuple of paths for the scorer model and scaler.
        """
        base_path = ENZEPTIONAL_SETTINGS.tool_dir / "models" / scorer_type
        scorer_path = f"{base_path}/model.pkl"
        scaler_path = f"{base_path}/scaler.pkl" if scorer_type == "kcat" else None
        return scorer_path, scaler_path

    def _save_results(self, results: List[Dict[Any, Any]], filename: Path) -> None:
        """
        Save optimized sequences to a file.

        Args:
            results: List of optimized sequence results.
            filename: Path to save the results.
        """
        df = pd.DataFrame(results)
        df.to_json(filename, orient="records", lines=True)
        logger.info(f"Optimized sequences saved to {filename}")

    async def _arun(self, *args, **kwargs) -> str:
        """
        Async method for enzyme optimization (not implemented).

        Raises:
            NotImplementedError: Async execution is not implemented.
        """
        raise NotImplementedError("Async execution not implemented for OptimizeEnzymeSequences.")
