#
# MIT License
#
# Copyright (c) 2025 GT4SD team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.#
"""Core tool utilities."""

import logging

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class BiocatalysisAssistantBaseTool(BaseTool):
    """Base class for tools used in the biocatalysis Assistant framework."""

    @classmethod
    def safe_tool_instantiation(cls, **kwargs) -> BaseTool | None:
        """
        Safely instantiate a tool, catching and logging any exceptions that occur during instantiation.

        Returns:
            An instance of the tool if successful, or None if an exception occurs.
        """
        try:
            if cls.check_requirements():
                return cls(**kwargs)
            else:
                logger.warning(
                    f"Requirements not met for {cls.__name__}. Tool will not be available."
                )
                return None
        except Exception as e:
            logger.error(f"Error instantiating {cls.__name__}: {str(e)}")
            return None

    @staticmethod
    def check_requirements() -> bool:
        """
        Check if the required directories for the tool exist.

        Returns:
            True if all required directories exist or if no checks are necessary, False otherwise.
        """
        return True
