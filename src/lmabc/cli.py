"""Biocatalysis Assistant CLI."""

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

import importlib.metadata
import os
import sys
import textwrap

import colorama
from colorama import Fore, Style
from pydantic_settings import BaseSettings, SettingsConfigDict

from lmabc.core import BiocatalysisAssistant

USER_COLOR = Fore.LIGHTRED_EX
AGENT_COLOR = Fore.YELLOW
HIGHLIGHT_COLOR = Fore.CYAN
ERROR_COLOR = Fore.RED
SUCCESS_COLOR = Fore.GREEN
INFO_COLOR = Fore.BLUE
PRIMARY_COLOR = Fore.RED
BUTTON_TEXT_COLOR = Fore.WHITE

colorama.init()


class Settings(BaseSettings):
    """Parameter settings for the CLI."""

    default_model: str = "meta-llama/llama-3-1-70b-instruct"
    default_provider: str = "watsonx"

    model_config = SettingsConfigDict(env_prefix="CLI_")


def print_welcome():
    """Display the welcome message and description of the Biocatalysis Assistant."""

    print(
        HIGHLIGHT_COLOR
        + Style.BRIGHT
        + """
    
  ╔══════════════════════════════════════════════════╗
  ║ ╔══════════════════════════════════════════════╗ ║
  ║ ║  Welcome to the Biocatalysis Assistant CLI   ║ ║
  ║ ╚══════════════════════════════════════════════╝ ║
  ╚══════════════════════════════════════════════════╝
          
    """
        + Style.RESET_ALL
    )

    description = f"""
{AGENT_COLOR}The Biocatalysis Assistant is a tool designed for automating
and optimizing workflows in bioinformatics and biocatalysis. Built on large language
models like GPT and LLaMA, it simplifies complex scientific processes by
interpreting natural language inputs to run various specialized tools. Key features
include enzyme binding site extraction, enzyme sequence optimization, and
molecular dynamics simulations, all integrated into an easy-to-use,
language-guided interface. The assistant dynamically selects tools based on
user inputs, enabling seamless execution of tasks like mutagenesis and protein
structure analysis. By unifying these functionalities, it accelerates research
in enzyme design, making advanced computational methods more accessible to
researchers.{Style.RESET_ALL}
 """
    print(textwrap.dedent(description))

    print(INFO_COLOR + "Type 'exit' to quit, 'help' for commands." + Style.RESET_ALL)
    print(
        INFO_COLOR
        + "Before starting please set up the following parameters:"
        + Style.RESET_ALL
    )


def clear_screen():
    """Clear the console screen."""
    os.system("cls" if os.name == "nt" else "clear")


def wrap_text(text, width=80):
    """
    Wrap text to a specified width.

    Args:
        text: The text to wrap.
        width: The maximum width of each line (default: 80).

    Returns:
        The wrapped text as a string.
    """
    return "\n".join(textwrap.wrap(text, width=width))


def get_verbosity():
    """
    Prompt the user to set the verbosity level.

    Returns:
        Boolean indicating whether verbose mode is enabled.
    """
    while True:
        verbosity = input(
            "\n"
            + INFO_COLOR
            + "Set verbosity (Enter or T for verbose, F for quiet mode): "
            + Style.RESET_ALL
        ).lower()
        if verbosity == "" or verbosity == "t":
            return True
        elif verbosity == "f":
            return False
        else:
            print(
                "\n"
                + ERROR_COLOR
                + "Invalid input. Please try again."
                + Style.RESET_ALL
            )


def get_model_and_provider(default_model, default_provider):
    """
    Prompt the user to confirm or change the model and provider.

    Args:
        default_model: The default model name.
        default_provider: The default provider name.

    Returns:
        Tuple containing the selected model and provider names.
    """
    print("\n" + INFO_COLOR + f"Current model: {default_model}" + Style.RESET_ALL)
    print(INFO_COLOR + f"Current provider: {default_provider}" + Style.RESET_ALL)
    choice = input(
        "\n"
        + INFO_COLOR
        + "Press Enter to keep these settings, or type new values (model provider): "
        + Style.RESET_ALL
    )
    if choice.strip() == "":
        return default_model, default_provider
    else:
        try:
            new_model, new_provider = choice.split()
            return new_model, new_provider
        except ValueError:
            print(
                ERROR_COLOR + "Invalid input. Using default settings." + Style.RESET_ALL
            )
            return default_model, default_provider


def print_help():
    """Display the help information for the CLI."""
    help_text = f"""
{Fore.GREEN}Biocatalysis Assistant CLI Help{Style.RESET_ALL}

{Fore.CYAN}DESCRIPTION:{Style.RESET_ALL}
    This CLI provides an interface to interact with the Biocatalysis Assistant,
    allowing users to ask questions and receive responses related to biocatalysis.

{Fore.CYAN}USAGE:{Style.RESET_ALL}
    python biocatalysis_cli.py

{Fore.CYAN}INITIAL SETUP:{Style.RESET_ALL}
    Upon starting, you will be prompted to:
    1. Set verbosity level
    2. Confirm or change the model and provider

{Fore.CYAN}COMMANDS:{Style.RESET_ALL}
    help   : Display this help message
    exit   : Exit the program
    clear  : Clear the screen

{Fore.CYAN}INTERACTION:{Style.RESET_ALL}
    After setup, you can start asking questions. The assistant will process your
    input and provide responses based on its knowledge of biocatalysis.

{Fore.CYAN}EXAMPLES:{Style.RESET_ALL}
    - To ask a question:
      > Enter your question: What are the main types of enzyme catalysis?

    - To clear the screen:
      > Enter your question: clear

    - To exit the program:
      > Enter your question: exit

{Fore.YELLOW}For more information or support, please contact the development team.{Style.RESET_ALL}
    """
    print(textwrap.dedent(help_text))


def print_version():
    """Display the version information of the Biocatalysis Assistant CLI."""
    try:
        version = importlib.metadata.version("lmabc")
        print(
            INFO_COLOR
            + f"Biocatalysis Assistant CLI Version {version}"
            + Style.RESET_ALL
        )
    except importlib.metadata.PackageNotFoundError:
        print(INFO_COLOR + "Version information could not be found." + Style.RESET_ALL)


def main():
    """
    Main function to run the Biocatalysis Assistant CLI.

    This function initializes the assistant, handles user input, and manages the interaction loop.
    """
    if "--help" in sys.argv:
        print_help()
        sys.exit(0)

    if "--version" in sys.argv:
        print_version()
        sys.exit(0)

    settings = Settings()

    print_welcome()

    verbose = get_verbosity()

    model, provider = get_model_and_provider(
        settings.default_model, settings.default_provider
    )

    print(
        HIGHLIGHT_COLOR + "\nInitializing Biocatalysis Assistant..." + Style.RESET_ALL
    )
    agent = BiocatalysisAssistant(
        model=model, provider=provider, verbose=verbose
    ).initiate_agent()

    print(
        SUCCESS_COLOR
        + "\nAssistant initialized. You can start asking questions now.\n"
        + Style.RESET_ALL
    )

    while True:
        user_input = input(USER_COLOR + "\nEnter your question: " + Style.RESET_ALL)

        if user_input.lower() == "exit":
            print(
                INFO_COLOR
                + "Thank you for using the Biocatalysis Assistant CLI. Goodbye!"
                + Style.RESET_ALL
            )
            break
        elif user_input.lower() == "help":
            print_help()
            continue
        elif user_input.lower() == "clear":
            clear_screen()
            print_welcome()
            continue

        print(HIGHLIGHT_COLOR + "\nProcessing your request..." + Style.RESET_ALL)
        try:
            response = agent.invoke({"input": user_input})
            print(AGENT_COLOR + "\nAssistant response:" + Style.RESET_ALL)
            print(AGENT_COLOR + wrap_text(response["output"]) + Style.RESET_ALL)
        except Exception as e:
            print(ERROR_COLOR + f"\nAn error occurred: {str(e)}" + Style.RESET_ALL)


if __name__ == "__main__":
    main()
