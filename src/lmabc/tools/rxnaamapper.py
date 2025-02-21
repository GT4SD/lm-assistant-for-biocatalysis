"""RXNAAMapper tools and utilities."""

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
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from rxn_aa_mapper.aa_mapper import RXNAAMapper

from ..configuration import BIOCATALYSIS_AGENT_CONFIGURATION
from .core import BiocatalysisAssistantBaseTool

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class RXNAAMapperConfiguration(BaseSettings):
    """Configuration values for the RXNAAMapper tool.

    Attributes:
        vocabulary_file: Path to the vocabulary file.
        aa_sequence_tokenizer_filepath: Path to the AA sequence tokenizer file.
        aa_sequence_tokenizer_type: Type of AA sequence tokenizer.
        model_path: Path to the model.
        head: Head value for the model.
        layers: List of layers for the model.
        top_k: Top K value for predictions.
    """

    vocabulary_file: str = str(
        BIOCATALYSIS_AGENT_CONFIGURATION.get_tool_dir("rxnaamapper") / "vocabulary.txt"
    )
    aa_sequence_tokenizer_filepath: str = str(
        BIOCATALYSIS_AGENT_CONFIGURATION.get_tool_dir("rxnaamapper") / "tokenizer.json"
    )
    aa_sequence_tokenizer_type: str = "generic"
    model_path: str = str(BIOCATALYSIS_AGENT_CONFIGURATION.get_tool_dir("rxnaamapper") / "model")
    head: int = 3
    layers: List[int] = [11]
    top_k: int = 1

    model_config = SettingsConfigDict(
        env_prefix="RXN_AA_MAPPER_", protected_namespaces=("settings_",)
    )


RXNAAMAPPER_SETTINGS = RXNAAMapperConfiguration()


class ExtractBindingSites(BiocatalysisAssistantBaseTool):
    """Tool for extracting binding sites from reaction SMILES."""

    name: str = "ExtractBindingSites"
    description: str = """This tool extracts binding sites from a given reaction SMILES string using RXNAAMapper.
    
    Input Format:
        - Reaction SMILES must follow this structure: substrate SMILES | amino acid sequence >> product SMILES
        - Example:  CC(=O)Cc1ccccc1|MTENALVR>>CC(O)Cc1ccccc1
"""

    @staticmethod
    def check_requirements() -> bool:
        """
        Check if the required directories and files for RXNAAMapper exist.

        Returns:
            Boolean indicating if all requirements are met.
        """
        settings = RXNAAMAPPER_SETTINGS

        paths_to_check = [
            settings.model_path,
            settings.vocabulary_file,
            settings.aa_sequence_tokenizer_filepath,
        ]

        for path in paths_to_check:
            path_obj = Path(path)
            expected_type = "directory" if path == settings.model_path else "file"

            if not path_obj.exists():
                logger.warning(f"Required {expected_type} {path} does not exist.")
                return False

            if expected_type == "directory" and not path_obj.is_dir():
                logger.warning(f"{path} exists but is not a directory.")
                return False
            elif expected_type == "file" and not path_obj.is_file():
                logger.warning(f"{path} exists but is not a file.")
                return False

        return True

    def _run(self, reaction_smiles: str) -> str:
        """
        Run binding site extraction.

        Args:
            reaction_smiles: The reaction SMILES string.

        Returns:
            String containing the extracted binding sites or an error message.

        Raises:
            ValueError: If binding site extraction fails.
        """
        if not reaction_smiles:
            return "Reaction SMILES string is empty."

        try:
            mapper = RXNAAMapper(config=RXNAAMAPPER_SETTINGS.model_dump())
            intervals = mapper.get_predicted_active_site(
                mapper.get_reactant_aa_sequence_attention_guided_maps([reaction_smiles])[0][
                    "mapped_rxn"
                ],
                rxn_separator=">>",
                smiles_aa_sequence_separator="|",
            )
            intervals_str = ", ".join(f"{start}-{end}" for start, end in intervals)
            result = "The binding sites are: " + intervals_str
            return result

        except Exception as e:
            logger.error(f"Error in ExtractBindingSites: {e}")
            raise ValueError("Failed to extract binding sites.")

    async def _arun(self, reaction_smiles: str) -> str:
        """
        Async method for binding site extraction.

        Args:
            reaction_smiles: The reaction SMILES string.

        Raises:
            NotImplementedError: Async execution is not implemented.
        """
        raise NotImplementedError("Async execution not implemented for ExtractBindingSites.")


class GetElementsOfReaction(BiocatalysisAssistantBaseTool):
    """Tool for extracting elements of the reaction."""

    name: str = "GetElementsOfReaction"
    description: str = """Extracts and returns specific elements of a given reaction SMILES string using RXNAAMapper.
    Input Format:
        - Reaction SMILES must follow this structure: 'substrate SMILES | amino acid sequence >> product SMILES'
        - Example: 'CC(=O)Cc1ccccc1|MTENALVR>>CC(O)Cc1ccccc1'
    
    Components:
        1. Substrate SMILES: Chemical structure of starting material(s) in SMILES notation
           - Multiple substrates should be separated by '.'
        2. Amino Acid Sequence: Protein sequence in single-letter code
           - Must be separated from substrates by '|'
           - Valid characters are standard amino acid letters (A-Z)
        3. Product SMILES: Chemical structure of product(s) in SMILES notation
           - Separated from previous components by '>>'
           - Multiple products should be separated by '.'
    
    Output Format:
        Returns a formatted string with three components:
        'Reactants: [substrate SMILES], AA Sequence: [protein sequence], Products: [product SMILES]'
    
    Usage Notes:
        - All SMILES must be valid chemical structures
        - Protein sequence can be referenced as: enzyme, amino acid sequence, AA, or protein
        - Empty components should be indicated with an empty string
        - Spaces around separators (| and >>) are optional
"""

    def _run(self, reaction_smiles: str) -> str:
        logger.info("Extracting elements of a reaction.")
        """
        Run element extraction from reaction.

        Args:
            reaction_smiles: The reaction SMILES string.

        Returns:
            String containing the extracted reaction elements.

        Raises:
            ValueError: If element extraction fails.
        """
        if not reaction_smiles:
            return "Reaction SMILES string is empty."

        try:
            reaction_separator = ">>"
            smiles_aa_sequence_separator = "|"

            reactants, aa_sequence, products = "", "", ""
            try:
                precursors, products = reaction_smiles.split(reaction_separator)
            except Exception:
                precursors = reaction_smiles
            try:
                reactants, aa_sequence = precursors.split(smiles_aa_sequence_separator)
            except Exception:
                reactants = precursors
            result = (
                "Extracted Reaction Elements\n"
                "=============================\n"
                "Reactants: " + reactants + "\n"
                "Amino Acid Sequence: " + aa_sequence + "\n"
                "Products: " + products
            )
            return result
        except Exception as e:
            logger.error(f"Error in GetElementsOfReaction: {e}")
            raise ValueError("Failed to get elements of reaction.")
