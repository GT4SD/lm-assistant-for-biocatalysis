"""Test suite for the biocatalysis assistant module."""

import logging

import pytest
from lmabc.core import TOOL_FACTORY, BiocatalysisAssistant

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_agent_with_tools():
    """Validates agent's integration with tools and input handling."""
    model = "meta-llama/llama-3-1-70b-instruct"
    provider = "watsonx"
    agent = BiocatalysisAssistant(model=model, provider=provider).initiate_agent()

    input_text = {
        "input": "Find the components of the given reaction: CC(=O)Nc1ccc(cc1)S(=O)(=O)N|MASETFEFQAEITQLMSLIINTVYSNKEIFLRELISNASDALDKIRYKSLSDPKQLETEPDLFIRITPKPEQKLLEIRDSGIGMTKAELINNLGTIAKSGTKAFMEALSAGADLSMIGQFGLEGFYSLFLLADRLQVISKSNDDEQYIWESNAGGSFTVTLDEVNERIGRGTILRLFLKDDQLEYLEEKRIKEVIKRHSEFVAYPIQLVVTKEVEKEVPIP>>CC(=O)Nc1ccc(cc1)S(=O)(=O)O"
    }

    try:
        response = agent.invoke(input_text)
        assert response is not None
        assert isinstance(response, dict)
    except Exception as e:
        pytest.fail(f"Unexpected error occurred: {str(e)}")


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
        except Exception as e:
            failed_tools.append(f"{tool_name}: {str(e)}")

    assert (
        len(successful_tools) > 0
    ), f"Critical failure: No tools could be initialized. Failures: {', '.join(failed_tools)}"


def test_full_assistant():
    """Validates complete assistant initialization with all tools."""
    assistant = BiocatalysisAssistant()
    tools = assistant.get_available_tools()
    assert tools, "No tools were loaded"
    assert len(tools) > 0, "No tools were successfully loaded"

    agent = assistant.initiate_agent()
    assert agent, "Agent initialization failed"


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Configure logging for test session."""
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)


@pytest.fixture
def mock_assistant():
    """Provides a mock assistant for testing."""
    return BiocatalysisAssistant()
