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
"""Module configuration."""

__copyright__ = """
MIT License

Copyright (c) 2024 GT4SD team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

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

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BiocatalysisAgentConfiguration(BaseSettings):
    """Base configuration for biocatalysis tools."""

    base_dir: Path = Field(
        default=Path.home() / ".lmabc",
        description="Base directory for biocatalysis assistant (tools will be stored here).",
    )
    cache_dir: Path = Field(
        default=Path.home() / ".lmabc" / ".cache",
        description="Cache directory for biocatalysis assistant tools.",
    )

    model_config = SettingsConfigDict(env_prefix="LMABC_")

    def __init__(self, **kwargs):
        """
        Initialize the configuration.
        """
        super().__init__(**kwargs)
        self._create_base_directories()

    def _create_base_directories(self):
        """Create the base directories if they don't exist."""
        for directory in [self.base_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_tool_dir(self, tool_name: str) -> Path:
        """
        Get the directory for a specific tool within the base directory.

        Args:
            tool_name: Name of the tool.

        Returns:
            Path object representing the tool's directory.
        """
        tool_path = self.base_dir / tool_name
        tool_path.mkdir(parents=True, exist_ok=True)
        return tool_path

    def get_tool_cache_dir(self, tool_name: str) -> Path:
        """
        Get the cache directory for a specific tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            Path object representing the tool's cache directory.
        """
        cache_path = self.cache_dir / tool_name
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path


BIOCATALYSIS_AGENT_CONFIGURATION = BiocatalysisAgentConfiguration()
