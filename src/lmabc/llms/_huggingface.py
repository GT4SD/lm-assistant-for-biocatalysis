"""Huggingface initialization."""

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
from typing import Any, Dict

from dotenv import load_dotenv
from huggingface_hub import login
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

HUGGINGFACEHUB_API_TOKEN = os.getenv("HuggingFaceHUB_API_TOKEN")
token = os.environ["HUGGINGFACEHUB_API_TOKEN"]
login(token)

DIRECT_PARAMETERS = {
    "max_new_tokens": 4048,
    "max_length": 4048,
    "do_sample": False,
    "repetition_penalty": 1.03,
    "return_full_text": True,
}


def create_huggingface_llm(model: str, **model_kwargs) -> ChatHuggingFace:
    """
    Create and configure a chat language model interface using HuggingFaceEndpoint.

    Args:
        model: The model ID to be used (e.g., "HuggingFaceH4/zephyr-7b-beta").

    Returns:
        Configured language model interface.
    """

    direct_params = DIRECT_PARAMETERS.copy()
    other_kwargs: Dict[str, Any] = {}

    if model_kwargs:
        for key, value in model_kwargs.items():
            if key in DIRECT_PARAMETERS:
                direct_params[key] = value
            else:
                other_kwargs[key] = value

    llm = HuggingFaceEndpoint(
        repo_id=model,
        huggingfacehub_api_token=token,
        max_new_tokens=int(direct_params["max_new_tokens"]),
        do_sample=bool(direct_params["do_sample"]),
        repetition_penalty=direct_params["repetition_penalty"],
        return_full_text=bool(direct_params["return_full_text"]),
        **other_kwargs
    )
    return ChatHuggingFace(llm=llm, verbose=True)
