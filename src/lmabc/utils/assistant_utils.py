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
"""Agent executor creation for handling tasks in the biocatalysis Assistant."""

from typing import Union

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.chat_models.base import BaseChatModel
from langchain.memory import ConversationBufferMemory
from langchain.tools.render import render_text_description_and_args
from langchain_core.language_models.llms import BaseLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool


def create_agent(
    tools: list[BaseTool],
    llm: Union[BaseChatModel, BaseLLM],
    use_memory: bool = True,
    verbose: bool = True,
) -> AgentExecutor:
    """Create an agent executor.

    Args:
        tools: list of tools for the agent.
        llm: a langchain base chat model.

    Returns:
        an agent executor.
    """

    system_prompt = """
You are an intelligent assistant with access to tools that can help you answer various questions and perform tasks.
Respond to the human as helpfully and accurately as possible. Your responses to be straight to the point. No need for additional information not needed.

Use JSON BLOBS of single actions to interact with tools or provide answers. Ensure that you evaluate each step before proceeding and avoid infinite loops or repeating inputs unnecessarily.
Always determine if the final answer has been reached before moving to further actions. You main goal is to aswer to the question asked, Do not over analyse it! Keep it short and simple!

Here are the tools that you can use:
{tools}

JSON Blob Structure:
Use a json blob to specify a tool by providing an `action` key (tool name) and an `action_input` key (tool input).
- Valid `action` values: "Final Answer" or {tool_names}
- Always provide only ONE action per JSON blob, formatted as:
    ```json
    {{
        "action": $TOOL_NAME,
        "action_input": $INPUT
    }}
    ```

Process Framework
Follow these steps to reason and act effectively:

1. Question: Input the human's question or task that requires solving.

2. Thought:
    - Evaluate the current question in context with previous and subsequent steps.
    - Review prior steps to avoid unnecessary repetition. If repetition is detected, provide the Final Answer directly:
        ```json
        {{
            "action": "Final Answer",
            "action_input": "I'm sorry, I cannot answer that question with the information available."
        }}
        ```
    - Assess if the current information is sufficient to provide the Final Answer.
        - If yes, proceed directly to Final Answer.
        - If no, proceed to the next step (Action).

3. Action:
    - Select the most appropriate action from `[ "Final Answer", {tool_names} ]` based on your reasoning.
    - Provide the tool name and its required input in the JSON blob.

4. Observation:
    - Report the result of the chosen action.
    - Reassess whether the output provides sufficient information to answer the user's question or complete the task:
        - If yes, proceed to Final Answer.
        - If no, repeat the Thought → Action → Observation loop with updated reasoning or inputs.
        - Avoid repeating the cycle unnecessarily if the task can already be completed.

5. Final Answer:
    - If you have sufficient information to answer the user’s question or task, respond with a JSON blob:
        ```json
        {{
            "action": "Final Answer",
            "action_input": "Your complete and accurate response here."
        }}
        ```
    - If the information remains insufficient despite following the above steps, respond with:
        ```json
        {{
            "action": "Final Answer",
            "action_input": "I'm sorry, I cannot answer that question with the information available."
        }}
        ```
    in both cases the content of "action_input" can only be a string!


Strictly answer to the question asked. Do not over analysed things!. Begin!
"""

    human_prompt = """{input}
    {agent_scratchpad}
    (reminder to respond in a JSON blob no matter what)"""

    memory = (
        ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, output_key="output"
        )
        if use_memory
        else None
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human_prompt),
    ]).partial(
        tools=render_text_description_and_args(list(tools)),
        tool_names=", ".join([t.name for t in tools]),
    )

    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
            chat_history=lambda x: (  #  noqa: ARG005
                memory.chat_memory.messages if (use_memory and memory is not None) else []
            ),
        )
        | prompt
        | llm
        | JSONAgentOutputParser()
    )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        handle_parsing_errors=True,
        verbose=verbose,
        memory=memory,
        max_iterations=5,
        early_stopping_method="force",
        return_intermediate_steps=True,
    )
