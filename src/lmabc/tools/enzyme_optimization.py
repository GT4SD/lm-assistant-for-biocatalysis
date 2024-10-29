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
    num_iterations: int = Field(
        default=3, description="Number of optimization iterations."
    )
    num_sequences: int = Field(
        default=5, description="Number of sequences to optimize."
    )
    num_mutations: int = Field(
        default=5, description="Number of mutations per iteration."
    )
    time_budget: int = Field(
        default=3600, description="Time budget for optimization in seconds."
    )
    batch_size: int = Field(default=5, description="Batch size for optimization.")
    top_k: int = Field(default=3, description="Top K sequences to consider.")
    selection_ratio: float = Field(
        default=0.25, description="Selection ratio for optimization."
    )
    tool_dir: Path = Field(
        default=BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path(
            "enzyme_optimization"
        ),
        description="Output directory.",
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

ENZEPTIONAL_DESCRIPTION = """OptimizeEnzymeSequences Tool also known as Enzeptional
This tool must be executed on the system.

Description:
The OptimizeEnzymeSequences tool is designed to optimize enzyme sequences for biocatalysed reactions using the Enzeptional framework. It employs advanced machine learning techniques to suggest mutations that may improve the enzyme's catalytic efficiency or substrate specificity.

Here is the format of a reaction SMILES or biocatalysed reaction: reactants|amino_acid_sequence>>products

Required: Make sure all the input you are about to use, have the correct type. In case the type do not match, exit and give an error message!

Functionality:
- Optimizes protein sequences based on given substrate and product SMILES representations
- Uses either a feasibility scorer or a kcat (turnover number) scorer for optimization
- Applies a sequence of mutations and crossovers to generate optimized enzyme variants
- Supports both synchronous and asynchronous execution

Key Parameters:
1. substrate_smiles (str, required): SMILES representation of the substrate molecule
2. product_smiles (str, required): SMILES representation of the desired product molecule
3. protein_sequence (str, required): Amino acid sequence of the enzyme to be optimized
4. scorer_type (str, required): Type of scoring model to use ('feasibility' or 'kcat'). Default is 'feasibility'
5. intervals (List[List[int]], optional): Specific regions of the protein sequence to focus mutations on This could be binding sites or active sites. If not provided, the entire sequence is considered
6. num_iterations (int, optional): Number of optimization iterations to perform. Default is 3
7. num_sequences (int, optional): Number of sequences to optimize in each iteration. Default is 5
8. num_mutations (int, optional): Number of mutations to apply per iteration. Default is 5
9. time_budget (int, optional): Maximum time (in seconds) allowed for optimization. Default is 3600 (1 hour)
10. batch_size (int, optional): Batch size for processing sequences. Default is 5
11. top_k (int, optional): Number of top sequences to consider for the next iteration. Default is 3
12. selection_ratio (float, optional): Ratio of sequences to select for the next iteration. Default is 0.25
13. tool_dir (Path, Optional): Output directory.
14. output_filename (str, Optional): Filename of the output file.
15. perform_crossover (bool, Optional): If crossover should be perform. Default is True"
15. crossover_type (str, Optional): The type of crossover to perform in case perform_crossover is True. Default is sp_crossover. Here are some that are implemented in the tool: sp_crossover (Performs a single point crossover between two sequences), and uniform_crossover (Performs a uniform crossover between two sequences)"
17. pad_intervals (bool, Optional): If to perform padding or not of the intervals. Default is False
18. minimum_interval_length (int, Optional): Minimum length per interval during padding. Default is 8
19. seed (int, Optional): Random seed. Default is 42
20: number_of_results (int, optional): Number of result to return. Default is 10.


Usage Notes:
- Provide SMILES strings for substrate and product that accurately represent the desired reaction
- The protein sequence should be in standard single-letter amino acid code
- When specifying intervals, use a list of [start, end] pairs, e.g., [[0, 50], [100, 150]] to focus on residues 1-50 and 101-150
- Adjust num_iterations, num_sequences, and num_mutations to balance between exploration and computation time
- The time_budget parameter can be used to limit long-running optimizations

Output:
The tool returns a dictionary containing the best sequences and their score, ranked by their predicted performance for the given substrate-product pair.
You should return the best sequence with its score, unless you are asked differently or to return a certain amount of sequences!.

Example Usage:
result = tool._run(
    substrate_smiles,
    product_smiles,
    protein_sequence,
    scorer_type,
    intervals,
    num_iterations,
    time_budget
    number_of_results,
)

This tool is particularly useful for enzyme engineering projects, metabolic engineering, and biocatalysis optimization. It can help researchers identify promising enzyme variants for experimental validation, potentially reducing the time and resources required for directed evolution experiments.
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

        protein_model = ModelFactory.create_embedder(
            language_model_path, language_model_path
        )
        chem_model = ModelFactory.create_embedder(chem_model_path, chem_model_path)

        mutation_config = {
            "type": "language-modeling",
            "embedding_model_path": language_model_path,
            "tokenizer_path": language_model_path,
            "unmasking_model_path": language_model_path,
        }

        mutator = SequenceMutator(
            sequence=protein_sequence, mutation_config=mutation_config
        )
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

        Returns:
            True if all required directories and files exist, False otherwise.
        """
        settings = ENZEPTIONAL_SETTINGS

        paths_to_check = [
            settings.tool_dir,
            settings.tool_dir / "models",
            settings.tool_dir / "output",
        ]

        for path in paths_to_check:
            if not path.exists():
                logger.warning(f"Directory {path} does not exist. Creating it now.")
                path.mkdir(parents=True, exist_ok=True)

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
            intervals: List of intervals for mutation (default: None).
            number_of_results: Number of results to return (default: 10).

        Returns:
            List of dictionaries containing optimized sequences.
        """
        try:
            config = ENZEPTIONAL_SETTINGS.model_copy(update=kwargs)

            use_xgboost_scorer = False
            if scorer_type == "kcat":
                use_xgboost_scorer = True
            logger.info(f"using {scorer_type} scorer")

            scorer_path, scaler_path = self._get_model_paths(scorer_type)

            intervals = intervals or [[0, len(protein_sequence)]]

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

            filename: Path = config.tool_dir / "output" / config.output_filename
            self._save_results(results=optimized_sequences, filename=filename)

            df = pd.read_json(f"{filename}", orient="records", lines=True).head(
                number_of_results
            )
            return df.to_dict("records")

        except Exception as e:
            logger.error(f"Error in OptimizeEnzymeSequences: {e}")
            raise ValueError(f"Failed to optimize enzyme sequences: {str(e)}")

    def _get_model_paths(
        self, scorer_type: str = "feasibility"
    ) -> Tuple[str, Optional[str]]:
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
        raise NotImplementedError(
            "Async execution not implemented for OptimizeEnzymeSequences."
        )
