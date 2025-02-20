"""Streamlit App."""

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

import base64
import json
from typing import Any, Dict, List, cast

import streamlit as st
from examples_config import TOOL_EXAMPLES
from importlib_resources import files
from langchain_community.callbacks import StreamlitCallbackHandler

from lmabc.core import BiocatalysisAssistant

PROVIDER_MODELS: Dict[str, List[str]] = {
    "huggingface": [
        "HuggingFaceH4/zephyr-7b-beta",
        "Qwen/Qwen2.5-72B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.2",
    ],
    "watsonx": [
        "mistralai/mistral-large",
        "meta-llama/llama-3-3-70b-instruct",
        "meta-llama/llama-3-2-3b-instruct",
        "meta-llama/llama-3-1-8b-instruct",
        "ibm/granite-34b-code-instruct",
        "ibm/granite-3-8b-instruct",
        "ibm/granite-3-2b-instruct",
        "ibm/granite-3-2-8b-instruct-preview-rc",
    ],
    "openai": ["gpt-4-0125-preview", "gpt-4", "gpt-3.5-turbo"],
    "anthropic": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
    ],
    "ollama": ["llama3.2", "llama3.2:1b", "gemma2:2b", "llama3.1:8b-instruct-fp16"],
}

st.set_page_config(
    page_title="Biocatalysis Assistant: An LM Agent for biocatalysis",
    page_icon="🧪",
    layout="wide",
)


def load_css(file_name: str) -> None:
    """
    Load CSS file for styling.

    Args:
        file_name: Name of the CSS file to load.
    """
    try:
        css_path = files("lmabc.resources").joinpath(file_name)
        css_content = css_path.read_text()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file '{file_name}' not found in the styles directory")
    except Exception as e:
        st.error(f"Error loading CSS file '{file_name}': {str(e)}")


load_css("styles.css")


def get_local_img(file_name: str) -> str:
    """
    Load and encode local image to base64.

    Args:
        file_name: Name of the image file.

    Returns:
        Base64 encoded image string.
    """
    try:
        img_path = files("lmabc.resources").joinpath(file_name)
        with img_path.open("rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error(f"Image file '{file_name}' not found in the images directory")
        return ""
    except Exception as e:
        st.error(f"Error loading image file '{file_name}': {str(e)}")
        return ""


tool_descriptions = {
    "**GetElementsOfReaction**": """Parses reaction SMILES to extract specific reactants, amino acid sequences, and products. This tool is essential for deconstructing complex biochemical reactions, allowing for detailed analysis of individual components.
    """,
    "**ExtractBindingSites**": """Utilizes [RXNAAMapper](https://doi.org/10.1016/j.csbj.2024.04.012) to extract binding sites from reaction SMILES strings. This tool is crucial for understanding enzyme functionality, as it identifies key sites that can be targeted for mutations to enhance catalytic activity or optimize user-specified fitness functions.
    """,
    "**OptimizeEnzymeSequences**": """Optimizes enzyme sequences for biocatalytic reactions using [Enzeptional](https://chemrxiv.org/engage/chemrxiv/article-details/65f0746b9138d23161510400). This powerful tool supports multiple optimization iterations based on substrate and product SMILES, featuring customizable scoring models and interval-specific mutations. It employs Genetic Algorithms to explore the vast sequence space and identify promising enzyme variants with improved catalytic properties. The tool outputs a ranked list of optimized sequences for experimental validation, significantly accelerating the enzyme engineering process.
    """,
    "**Blastp**": """Performs BLASTP (Basic Local Alignment Search Tool for Proteins) searches to identify protein sequences similar to a given query using [NCBI](https://www.ncbi.nlm.nih.gov). This tool allows customization of key parameters and generates comprehensive output including aligned sequences, descriptions, and statistical data, facilitating detailed protein homology and function analysis. By leveraging the vast NCBI database, it enables researchers to discover evolutionarily related proteins, predict functional similarities, and identify conserved domains. The results can guide further experimental investigations and provide insights into protein structure-function relationships.
    """,
    "**FindPDBStructure**": """Finds and retrieves [PDB](https://www.rcsb.org) structures based on a query using the [RCSB python package](https://rcsbsearchapi.readthedocs.io/en/latest/).
    """,
    "**DownloadPDBStructure**": """Downloads specific PDB structures based on a PDB code using the [RCSB Search API](https://search.rcsb.org). This tool complements the FindPDBStructure functionality by allowing direct retrieval of identified structures.
    """,
    "**Mutagenesis**": """Employs [PyMOL](https://www.pymol.org) to perform targeted mutations on protein structures, enabling the transformation of a protein structure to match a specified target sequence. It can optionally perform additional analyses like RMSD (Root Mean Square Deviation) calculations to assess structural changes. This tool can be used for predicting the structural consequences of amino acid substitutions, allowing researchers to visualize potential changes in protein conformation and stability. By integrating with PyMOL's powerful visualization capabilities, it provides both quantitative and qualitative insights into the effects of mutations on protein structure and function.
    """,
    "**MDSimulation**": """Facilitates Molecular Dynamics simulations using [GROMACS](https://www.gromacs.org). This tool automates the setup and execution of standard MD simulation stages, including Minimization, NVT (constant Number, Volume, Temperature) equilibration, and NPT (constant Number, Pressure, Temperature) equilibration.
    """,
}


def create_expanded_card(title: str, description: str):
    """
    Create expandable card for tool description.

    Args:
        title: Title of the tool.
        description: Description of the tool.
    """
    expanded = st.expander(title, expanded=False)
    with expanded:
        st.write(description)


def tools_page() -> None:
    """Initialize and display the Tools page."""
    st.title("🛠️ Tools")
    st.write("Explore our powerful set of tools to supercharge your biocatalysis research!")

    available_tools = []
    if "agent" in st.session_state and st.session_state.agent:
        available_tools = [tool.name for tool in st.session_state.agent.tools]

    cols = st.columns(4)

    for i, (tool_name, description) in enumerate(tool_descriptions.items()):
        with cols[i % 4]:
            tool_name_clean = tool_name.strip("*").strip()
            is_available = any(tool_name_clean in tool for tool in available_tools)

            expanded = st.expander(tool_name, expanded=False)
            with expanded:
                if not is_available:
                    st.warning("⚠️ Tool currently unavailable", icon="⚠️")
                st.write(description)


def get_chat_message(contents: str = "", align: str = "left") -> str:
    """
    Generate HTML for chat message with styling.

    Args:
        contents: Message content.
        align: Message alignment ('left' for AI, 'right' for human).

    Returns:
        Formatted HTML string for the chat message.
    """
    div_class = "AI-line" if align == "left" else "human-line"
    color = "var(--chat-bubble-ai)" if align == "left" else "var(--chat-bubble-human)"
    file_name = "robot.png" if align == "left" else "user.png"
    src = f"data:image/gif;base64,{get_local_img(file_name)}"

    icon_code = f"<img class='chat-icon' src='{src}' width=32 height=32 alt='avatar'>"
    return f"""
    <div class="{div_class}">
        {icon_code}
        <div class="chat-bubble" style="background: {color};">
        &#8203;{contents}
        </div>
    </div>
    """


def create_biocatalysis_assistant(
    model: str, provider: str, use_memory: bool = True, **model_kwargs: Dict[str, Any]
) -> Any:
    """
    Create and initialize the Biocatalysis Assistant.

    Args:
        model: Name of the AI model.
        provider: Name of the model provider.
        **model_kwargs: Additional model parameters.

    Returns:
        Initialized Biocatalysis Assistant.
    """
    agent = BiocatalysisAssistant(
        model=model, provider=provider, use_memory=use_memory, model_kwargs=model_kwargs
    )
    return agent.initiate_agent()


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "page" not in st.session_state:
        st.session_state.page = "🏠 Home"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = create_biocatalysis_assistant(
            model=PROVIDER_MODELS["watsonx"][0], provider="watsonx"
        )
    if "stream_output" not in st.session_state:
        st.session_state.stream_output = True
    if "sessions" not in st.session_state:
        st.session_state.sessions = {"default": {"agent": st.session_state.agent}}
    if "current_session" not in st.session_state:
        st.session_state.current_session = "default"
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = "watsonx"
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = PROVIDER_MODELS["watsonx"][0]
    if "use_memory" not in st.session_state:
        st.session_state.use_memory = True


initialize_session_state()


def sidebar() -> None:
    """Initialize and display the sidebar."""
    with st.sidebar:
        st.subheader("🚀 Quick Actions")

        for page in [
            "🏠 Home",
            "🛠️ Tools",
            "⚙️ Settings",
            "📚 Python API Docs",
            "📝 Examples",
        ]:
            if st.button(page, key=f"{page.lower()}_button"):
                st.session_state.page = page

        st.markdown("---")
        st.subheader("📚 Github")
        st.markdown("[🔗 View Source Code](https://github.com/GT4SD/lm-assistant-for-biocatalysis)")

        st.markdown("---")
        st.subheader("📄 Citation")
        st.code(
            """@software{LMABC,
            author = {Yves Gaetan Nana Teukam, Francesca Grisoni, Matteo Manica},
            month = {10},
            title = {The biocatalysis assistant: a language model agent for biocatalysis (lmabc)},
            url = {https://github.com/GT4SD/lm-assistant-for-biocatalysis},
            version = {main},
            year = {2024}
        }""",
            language="bibtex",
        )


def docs_page() -> None:
    """Python API Documentation page setup"""
    st.title("📚 Python API Documentation")

    docs = files("lmabc.resources").joinpath("documentation.md").read_text()
    st.markdown(docs)


def try_example(example_input: str) -> None:
    """Handle 'Try it!' button click."""
    st.session_state.previous_memory_state = getattr(st.session_state, "use_memory", True)

    st.session_state.use_memory = False

    st.session_state.messages.append({"role": "user", "content": example_input})
    st.session_state.current_example = example_input
    st.session_state.executing_example = True
    st.session_state.page = "🏠 Home"


def render_tool_example(example: dict) -> None:
    """Render a single tool example."""
    st.markdown(f"### {example['emoji']} {example['name']}")
    with st.expander("Show details", expanded=False):
        st.markdown("#### Example Input")
        st.code(example["example_input"], language="python")
        if st.button("🚀 Try this example!", key=f"try_{example['id']}", type="primary"):
            try_example(example["example_input"])


def handle_example_execution():
    """Execute example query and store response."""
    if st.session_state.get("executing_example", False):
        with st.spinner("🤖 Processing example..."):
            temp_agent = BiocatalysisAssistant(
                model=st.session_state.selected_model,
                provider=st.session_state.selected_provider,
                use_memory=False,
            ).initiate_agent()

            response = temp_agent.invoke({"input": st.session_state.current_example})
            if response:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["output"],
                })

            st.session_state.use_memory = st.session_state.previous_memory_state
            st.session_state.executing_example = False
            st.session_state.current_example = None


def examples_page() -> None:
    """Render the examples page."""
    if "agent" not in st.session_state:
        st.error("Please initialize the agent in Settings first!")
        return

    if st.session_state.get("executing_example", False):
        st.session_state.executing_example = False
        st.session_state.current_example = None
        # Restore memory state if needed
        if hasattr(st.session_state, "previous_memory_state"):
            st.session_state.use_memory = st.session_state.previous_memory_state

    st.title("💡 Interactive Examples")
    st.markdown(
        """
    Explore our tools with these ready-to-use examples. Click 'Try it!' to run any example directly in the chat interface.
    """
    )
    st.markdown("## 🛠️ Tool Examples")
    st.markdown("Click on any example to see details and try it out.")

    cols = st.columns(2)
    for i, example in enumerate(TOOL_EXAMPLES):
        with cols[i % 2]:
            render_tool_example(example)


def display_chat_messages() -> None:
    """Display chat messages in the UI."""
    for message in st.session_state.messages:
        st.markdown(
            get_chat_message(message["content"], "right" if message["role"] == "user" else "left"),
            unsafe_allow_html=True,
        )


def handle_user_input() -> None:
    """Process user input and generate AI response."""
    if prompt := st.chat_input("Enter your query:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(get_chat_message(prompt, "right"), unsafe_allow_html=True)

        with st.spinner("🤔 Thinking..."):
            response_container = st.empty()
            streamlit_handler = StreamlitCallbackHandler(
                response_container, collapse_completed_thoughts=True
            )

            try:
                response = st.session_state.agent.invoke(
                    {"input": prompt},
                    {
                        "callbacks": (
                            [streamlit_handler] if st.session_state.stream_output else None
                        )
                    },
                )
                full_response = response["output"]

                if isinstance(full_response, list):
                    full_response = " ".join(full_response)

                st.markdown(get_chat_message(full_response, "left"), unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                st.markdown(get_chat_message(error_message, "left"), unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": error_message})


def home_page() -> None:
    """Initialize and display the Home page."""
    st.title("Language Model Assistant for Biocatalysis (LM-ABC)")
    st.write(
        "Welcome to your hub for innovative biocatalysis solutions where you can explore, analyze and optimize with ease."
    )

    handle_example_execution()
    display_chat_messages()
    handle_user_input()


def get_default_provider() -> str:
    """Get the default provider name."""
    return next(iter(PROVIDER_MODELS))


def get_default_model(provider: str) -> str:
    """Get the default model for a given provider."""
    return PROVIDER_MODELS[provider][0]


def settings_page() -> None:
    """Initialize and display the Settings page."""
    st.title("⚙️ Settings")

    current_provider = cast(
        str, getattr(st.session_state, "selected_provider", get_default_provider())
    )
    if current_provider not in PROVIDER_MODELS:
        current_provider = get_default_provider()

    selected_provider = st.selectbox(
        "☁️ Choose Provider",
        options=list(PROVIDER_MODELS.keys()),
        index=list(PROVIDER_MODELS.keys()).index(current_provider),
    )

    provider = selected_provider if selected_provider is not None else get_default_provider()
    st.session_state.selected_provider = provider

    current_model = cast(
        str, getattr(st.session_state, "selected_model", get_default_model(provider))
    )

    if current_provider != provider:
        current_model = get_default_model(provider)

    if current_model not in PROVIDER_MODELS[provider]:
        current_model = get_default_model(provider)

    selected_model = st.selectbox(
        "🤖 Choose AI Model",
        options=PROVIDER_MODELS[provider],
        index=PROVIDER_MODELS[provider].index(current_model),
    )

    model = selected_model if selected_model is not None else get_default_model(provider)
    st.session_state.selected_model = model

    st.session_state.stream_output = st.checkbox(
        "🌊 Stream Output", value=st.session_state.stream_output
    )

    st.session_state.use_memory = st.checkbox("🧠 Use Memory", value=st.session_state.use_memory)

    additional_settings = st.text_area("🔧Additional Settings (JSON)")

    additional_params: Dict[str, Any] = {}
    if additional_settings:
        try:
            additional_params = json.loads(additional_settings)
            st.write("Parsed JSON:", additional_params)
        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please check your input.")

    if st.button("💾 Save Settings", key="save_settings", use_container_width=True):
        with st.spinner("Initializing new model... Please wait..."):
            try:
                new_agent = create_biocatalysis_assistant(
                    model=model,
                    provider=provider,
                    use_memory=st.session_state.use_memory,
                    **additional_params,
                )
                st.session_state.sessions[st.session_state.current_session]["agent"] = new_agent
                st.session_state.agent = new_agent
                st.success("✅ Settings saved successfully!")
            except Exception as e:
                st.error(f"❌ Error initializing model: {str(e)}")


def main() -> None:
    """Main function to run the Streamlit app."""
    sidebar()

    if st.session_state.page == "⚙️ Settings":
        settings_page()
    elif st.session_state.page == "🛠️ Tools":
        tools_page()
    elif st.session_state.page == "📚 Python API Docs":
        docs_page()
    elif st.session_state.page == "📝 Examples":
        examples_page()
    else:
        home_page()


if __name__ == "__main__":
    main()
