"""Test suite for the biocatalysis assistant module."""

import logging

import pytest
from lmabc.core import TOOL_FACTORY, BiocatalysisAssistant

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@pytest.fixture
def mock_assistant():
    """Provides a mock assistant for testing."""
    return BiocatalysisAssistant()


def test_individual_tools():
    """Validates initialization of each tool independently."""
    successful_tools = []
    failed_tools = []

    for tool_name in TOOL_FACTORY:
        try:
            assistant = BiocatalysisAssistant(tool_names=[tool_name])
            tools = assistant.get_available_tools()
            if tools:
                successful_tools.append(tool_name)
            else:
                failed_tools.append(f"{tool_name}: No tools loaded")
        except Exception as e:
            failed_tools.append(f"{tool_name}: {str(e)}")

    assert (
        len(successful_tools) > 0
    ), f"Critical failure: No tools could be initialized. Failures: {', '.join(failed_tools)}"


def test_agent_with_tools():
    """Validates agent's integration with tools and input handling."""
    model = "HuggingFaceH4/zephyr-7b-beta"
    provider = "huggingface"
    agent = BiocatalysisAssistant(model=model, provider=provider).initiate_agent()

    input_text = {
        "input": "Extract elements of reaction for the following reaction CC(=O)Nc1ccc(cc1)S(=O)(=O)N|MASETFEFQAEITQLMSLIINTVYSNKEIFLRELISNASDALDKIRYKSLSDPKQLETEPDLFIRITPKPEQKIGRGTILRLFLKDDQLVAYPIQLVVTKEVEKEVPIP>>CC(=O)Nc1ccc(cc1)S(=O)(=O)O"
    }

    response = agent.invoke(input_text)

    print("Agent Response:", response)

    assert response is not None, "Agent response should not be None"
    assert isinstance(response, dict), "Agent response should be a dictionary"


@pytest.fixture(scope="module")
def individual_results():
    """Fixture to run individual tool tests and return results."""
    results = {}
    for tool_name in TOOL_FACTORY:
        try:
            assistant = BiocatalysisAssistant(tool_names=[tool_name])
            tools = assistant.get_available_tools()
            if tools:
                results[tool_name] = "Success"
            else:
                results[tool_name] = "Failed - No tools loaded"
        except Exception as e:
            results[tool_name] = f"Failed - {str(e)}"
    return results


@pytest.fixture(scope="module")
def full_assistant_results():
    """Fixture to run full assistant test and return results."""
    try:
        assistant = BiocatalysisAssistant()
        tools = assistant.get_available_tools()
        _ = assistant.initiate_agent()
        return True, len(tools)
    except Exception:
        return False, 0
