"""Biocatalysis Assistant Module."""

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
from typing import Any, Dict, List, Optional, Type, Union

from langchain.agents import AgentExecutor
from langchain_core.tools import BaseTool
from pydantic_settings import BaseSettings, SettingsConfigDict

from .llms import create_llm
from .tools.blast import Blastp
from .tools.core import BiocatalysisAssistantBaseTool
from .tools.enzyme_optimization import OptimizeEnzymeSequences
from .tools.md_simulations import MDSimulation
from .tools.mutagenesis import Mutagenesis
from .tools.pdb import DownloadPDBStructure, FindPDBStructure
from .tools.rxnaamapper import ExtractBindingSites, GetElementsOfReaction
from .utils.assistant_utils import create_agent

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Settings(BaseSettings):
    """Configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env", extra="allow", case_sensitive=False
    )


settings = Settings()

TOOL_FACTORY: Dict[str, Type[BiocatalysisAssistantBaseTool]] = {
    "ExtractBindingSites": ExtractBindingSites,
    "GetElementsOfReaction": GetElementsOfReaction,
    "Blastp": Blastp,
    "OptimizeEnzymeSequences": OptimizeEnzymeSequences,
    "FindPDBStructure": FindPDBStructure,
    "DownloadPDBStructure": DownloadPDBStructure,
    "Mutagenesis": Mutagenesis,
    "MDSimulation": MDSimulation,
}


class BiocatalysisAssistant:
    """
    A class representing a Biocatalysis Assistant with dynamic tool selection.
    """

    def __init__(
        self,
        tool_names: Optional[
            Union[List[str], Dict[str, Type[BiocatalysisAssistantBaseTool]]]
        ] = None,
        model: str = "HuggingFaceH4/zephyr-7b-beta",
        provider: str = "huggingface",
        use_memory: bool = True,
        model_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Initialize an agent with a dynamic set of tools."""
        self.tool_list: List[BaseTool] = []
        self.model = model
        self.provider = provider
        self.use_memory = use_memory
        self.model_kwargs = model_kwargs

        logger.info(
            f"Initializing BiocatalysisAssistant with model={model}, provider={provider}"
        )

        tool_names = list(TOOL_FACTORY.keys()) if tool_names is None else tool_names
        logger.info(f"Attempting to load the following tools: {tool_names}")

        successful_tools = []
        failed_tools = []

        for tool_name in tool_names:
            try:
                if tool_name not in TOOL_FACTORY:
                    raise ValueError(
                        f"Tool '{tool_name}' is not available in the tool factory."
                    )

                logger.debug(f"Attempting to instantiate {tool_name}")
                tool_class = TOOL_FACTORY[tool_name]

                # Use the safe_tool_instantiation method
                tool_instance = tool_class.safe_tool_instantiation()

                if tool_instance is not None:
                    self.tool_list.append(tool_instance)
                    successful_tools.append(tool_name)
                    logger.debug(f"Successfully instantiated {tool_name}")
                else:
                    failed_tools.append(tool_name)
                    logger.warning(f"Failed to instantiate tool '{tool_name}'")

            except Exception as e:
                failed_tools.append(tool_name)
                logger.error(
                    f"Error instantiating {tool_name}: {str(e)}", exc_info=True
                )

        if successful_tools:
            logger.info(f"Successfully loaded tools: {successful_tools}")
        if failed_tools:
            logger.warning(f"Failed to load tools: {failed_tools}")

    def get_available_tools(self) -> List[BaseTool]:
        """Get a list of all available tools."""
        return self.tool_list

    @staticmethod
    def get_supported_tools() -> List[str]:
        """Get a list of all supported tool names."""
        return list(TOOL_FACTORY.keys())

    def initiate_agent(self) -> AgentExecutor:
        """Create and return an agent with the specified tools."""
        if not self.tool_list:
            logger.error("No tools were successfully loaded. Agent creation may fail.")

        llm = create_llm(model=self.model, provider=self.provider)
        logger.info("Created LLM instance")

        try:
            agent = create_agent(
                tools=self.tool_list, llm=llm, use_memory=self.use_memory
            )
            logger.info("Successfully created agent")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent: {str(e)}", exc_info=True)
            raise
