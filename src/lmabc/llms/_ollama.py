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
"""Ollama initialization."""

from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama

load_dotenv()

DEFAULT_PARAMETERS = {
    "max_new_tokens": 512,
    "do_sample": False,
    "repetition_penalty": 1.03,
    "return_full_text": False,
}


def create_ollama_llm(model: str, **model_kwargs) -> ChatOllama:
    """
    Create and configure a language model interface using OllamaLLM.

    Args:
        model: The model ID to be used (e.g., "llmamallama3.2").

    Returns:
        Configured language model interface.
    """

    parameters = DEFAULT_PARAMETERS.copy()
    if model_kwargs:
        parameters.update(model_kwargs)

    return ChatOllama(model=model)
