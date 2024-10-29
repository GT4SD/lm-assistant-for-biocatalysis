#!/usr/bin/env python3
"""Test script for BiocatalysisAssistant"""

import logging

# Configure logging for both the test script and the module
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("biocatalysis_test.log")],
)

logger = logging.getLogger(__name__)


def test_individual_tools():
    """Test each tool individually to isolate issues."""
    from lmabc.core import TOOL_FACTORY, BiocatalysisAssistant

    logger.info("Testing individual tool initialization...")

    results = {}
    for tool_name in TOOL_FACTORY.keys():
        try:
            assistant = BiocatalysisAssistant(tool_names=[tool_name])
            tools = assistant.get_available_tools()
            if tools:
                results[tool_name] = "Success"
                logger.info(f"✓ {tool_name}: Successfully loaded")
            else:
                results[tool_name] = "Failed - No tools loaded"
                logger.error(f"✗ {tool_name}: Failed to load")
        except Exception as e:
            results[tool_name] = f"Failed - {str(e)}"
            logger.error(f"✗ {tool_name}: Failed with error: {str(e)}")

    return results


def test_full_assistant():
    """Test the assistant with all tools."""
    from lmabc.core import BiocatalysisAssistant

    logger.info("Testing full BiocatalysisAssistant initialization...")

    try:
        # Initialize with all tools
        assistant = BiocatalysisAssistant()

        # Get list of loaded tools
        tools = assistant.get_available_tools()
        logger.info(f"Successfully loaded {len(tools)} tools")

        # Print details about each loaded tool
        for tool in tools:
            logger.info(f"Loaded tool: {tool.__class__.__name__}")
            logger.debug(f"Tool description: {tool.description}")

        # Try to initiate the agent
        logger.info("Attempting to create agent...")
        _ = assistant.initiate_agent()
        logger.info("Successfully created agent")

        return True, len(tools)

    except Exception as e:
        logger.error(f"Failed to initialize assistant: {str(e)}", exc_info=True)
        return False, 0


def print_results(individual_results, full_success, total_tools):
    """Print test results in a formatted way."""
    print("\n=== BiocatalysisAssistant Test Results ===")
    print("\nIndividual Tool Tests:")
    print("-" * 50)
    for tool_name, result in individual_results.items():
        status = "✓" if result == "Success" else "✗"
        print(f"{status} {tool_name}: {result}")

    print("\nFull Assistant Test:")
    print("-" * 50)
    status = "✓" if full_success else "✗"
    print(
        f"{status} Assistant Initialization: {'Success' if full_success else 'Failed'}"
    )
    print(f"Total tools loaded: {total_tools}")

    print("\nFor detailed logs, check 'biocatalysis_test.log'")


def main():
    """Main test function."""
    logger.info("Starting BiocatalysisAssistant tests")

    # Test individual tools
    individual_results = test_individual_tools()

    # Test full assistant
    full_success, total_tools = test_full_assistant()

    # Print results
    print_results(individual_results, full_success, total_tools)


if __name__ == "__main__":
    main()
