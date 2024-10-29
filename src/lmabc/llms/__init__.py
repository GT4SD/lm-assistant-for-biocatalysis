"""LLMs initialization."""

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

from typing import Any, Dict, Optional, Union

from genai.extensions.langchain import LangChainChatInterface
from langchain.chat_models.base import BaseChatModel
from langchain_core.language_models.llms import BaseLLM


def create_llm(
    model: str, provider: str, model_kwargs: Optional[Dict[str, Any]] = None
) -> Union[BaseChatModel, LangChainChatInterface, BaseLLM]:
    """
    Create and configure a language model interface based on the provider.

    Args:
    model: The model path.
    provider: The provider of the language model
    (e.g., 'watsonx', or any model supported in langchain: https://api.python.langchain.com/en/latest/chat_models/langchain.chat_models.base.init_chat_model.html).
    model_kwargs: Additional keyword arguments for model configuration.

    Returns:
    configured language model interface.
    """
    model_kwargs = model_kwargs or {}
    if provider.lower() == "watsonx":
        from ._watsonx import create_watsonx_llm

        return create_watsonx_llm(model=model, **model_kwargs)
    elif provider.lower() == "huggingface":
        from ._huggingface import create_huggingface_llm

        return create_huggingface_llm(model=model, **model_kwargs)
    elif provider.lower() == "ollama":
        from ._ollama import create_ollama_llm

        return create_ollama_llm(model=model)
    else:
        from langchain.chat_models import init_chat_model

        return init_chat_model(model=model, provider=provider, **model_kwargs)
