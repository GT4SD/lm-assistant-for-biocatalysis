"""Module configuration."""

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


import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BiocatalysisAgentConfiguration(BaseSettings):
    """Base configuration for biocatalysis tools."""

    local_cache_path: Path = Field(
        default=Path(os.getenv("LMABC_LOCAL_CACHE_PATH", str(Path.home() / ".lmabc"))),
        description="Local cache path for biocatalysis assistant.",
    )
    model_config = SettingsConfigDict(env_prefix="LMABC_")

    def __init__(self, **kwargs):
        """
        Initialize the configuration.
        """
        super().__init__(**kwargs)
        self._create_base_directories()

    def _create_base_directories(self):
        """Create base directories if they don't exist."""
        directories = [
            self.local_cache_path,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_tools_cache_path(self, tool_name: str) -> Path:
        """
        Get the path for a specific tool's files.

        Args:
            tool_name: Name of the tool.

        Returns:
            Path object representing the tool's cache directory.
        """
        tool_path = self.local_cache_path / tool_name
        tool_path.mkdir(parents=True, exist_ok=True)
        return tool_path


BIOCATALYSIS_AGENT_CONFIGURATION = BiocatalysisAgentConfiguration()
