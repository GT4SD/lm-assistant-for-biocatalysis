"""Watsonx initialization."""

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

from dotenv import load_dotenv
from langchain_ibm import ChatWatsonx
from pydantic import (
    SecretStr,
)

load_dotenv()

watsonx_api_key = os.getenv("WATSONX_API_KEY")
watsonx_url = SecretStr(os.getenv("WATSONX_URL", default="https://us-south.ml.cloud.ibm.com"))
watsonx_project_id = os.getenv("WATSONX_PROJECT_ID")

DEFAULT_PARAMETERS = {
    "max_new_tokens": 2048,
    "min_new_tokens": 1,
    "temperature": 0,
    "random_seed": None,
    "repetition_penalty": None,
    "top_k": None,
    "top_p": None,
    "truncate_input_tokens": None,
    "decoding_method": "sample",
}


def create_watsonx_llm(model: str, **model_kwargs) -> ChatWatsonx:
    """
    Create and configure a language model interface using ChatWatsonx.

    Args:
        model: The model ID to be used (e.g., "meta-llama/llama-3-1-70b-instruct").

    Returns:
        Configured language model interface.
    """
    return ChatWatsonx(
        model_id=model,
        url=watsonx_url,
        project_id=watsonx_project_id,
        params={**DEFAULT_PARAMETERS, **model_kwargs},
    )
