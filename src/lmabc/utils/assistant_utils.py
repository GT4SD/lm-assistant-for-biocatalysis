"""Agent executor creation for handling tasks in the biocatalysis Assistant."""

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


import json
import re
from typing import Union

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.chat_models.base import BaseChatModel
from langchain.memory import ConversationBufferMemory
from langchain.schema import AgentAction, AgentFinish
from langchain.tools.render import render_text_description_and_args
from langchain_core.language_models.llms import BaseLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import BaseTool


class CustomJSONAssistantOutputParser(JSONAgentOutputParser):
    """Custom json parser to process the LLMs outputs."""

    def _extract_clean_json(self, text: str) -> str:
        """
        Extract a clean json from the LLM output text.
        Args:
            text: The text output from the LLM.
        Returns:
            Cleaned string.
        """
        text = text.strip()

        pattern = r"(?:```json\s*|\s*json\s*|\s*```\s*)"
        text = re.sub(pattern, "", text)

        text = text.replace("```", "").strip()

        return text

    def parse(self, text: str) -> AgentAction | AgentFinish:
        """
        Parse the LLM output text.
        Args:
            text: The text output from the LLM.
        Returns:
            Serializable object based on the parsed output.
        """
        try:
            cleaned_text = self._extract_clean_json(text)
            parsed = json.loads(cleaned_text)

            if (
                parsed.get("action") == "Final Answer"
                or parsed.get("action") == "response"
            ):
                action_input = parsed.get("action_input")
                if isinstance(action_input, (dict, list)):
                    formatted_output = json.dumps(action_input, indent=2)
                else:
                    formatted_output = str(action_input)

                return AgentFinish(return_values={"output": formatted_output}, log=text)

            return AgentAction(
                tool=str(parsed.get("action", "")),
                tool_input=parsed.get("action_input", ""),
                log=text,
            )

        except json.JSONDecodeError:
            return AgentFinish(return_values={"output": text}, log=text)


def create_agent(
    tools: list[BaseTool],
    llm: Union[BaseChatModel, BaseLLM],
    use_memory: bool = True,
):
    """
    Create and configure an agent with the provided tools and language model interface.

    Args:
        tools: List of BaseTool objects to be used by the agent.
        llm: Language model interface (either BaseChatModel or BaseLLM).
        use_memory: Boolean indicating whether to use conversation memory (default: True).

    Returns:
        AgentExecutor object configured with the specified tools, language model, and memory.
    """
    system_prompt = """
You are an AI assistant specializing in biocatalysis, computational biology, and molecular dynamics. Your task is to respond to questions or solve problems using the following tools: {tools} with names {tool_names}.

Only respond as the AI assistant. Never generate or simulate human messages or questions. Provide direct answers to the actual human input. Do not create hypothetical dialogue or conversation. Focus solely on the specific task or question asked.

Always provide the action in a single JSON blob, one JSON blob at a time unless strictly needed to reply with multiple. Do not anticipate the user/human questions or tasks.

Here is an example of valid JSON blob (do not include additional text or title outside of the JSON blob):
```json
{{
 "action": "Tool Name or Final Answer",
 "action_input": "Input for the tool or your final answer"
}}
```

Instructions:
1. Analyze the user's input carefully. Clearly restate the user's question or problem.

2. If you can answer directly without tools, provide a Final Answer immediately. Keep in mind that generic questions on reactions or biocatalyzed reactions can be directly answered with Final Answer.

3. If you need more information or are ready to give your final answer, ask the user directly in your Final Answer.

4. When using tools, follow this format strictly:
   Thought: Briefly explain your reasoning and check if you have all the necessary input for the next step; otherwise give immediately your Final Answer. The answer can be incomplete, that's fine.
   
   Then, provide the action in a single JSON blob:
   ```json
    {{
    "action": "Tool Name or Final Answer",
    "action_input": "Input for the tool or your final answer"
    }}
    ```

5. Use only one tool at a time.

6. Ensure data is correctly formatted between tool uses.

7. Don't repeat tool execution unless inputs change.

8. For PDB structures, always select the highest-scoring or first option.

Valid "action" values: Final Answer or {tool_names}. Do not use action values that are not valid.

Example of invalid JSON blob:
```json
{{
 "action": "Thought",
 "action_input": "Your thoughts"
}}
```

or

```json
{{
 "response": "Thought",
 "action_input": "Your thoughts"
}}
```

In this case, return "action_input" as Final Answer.

Ensure that when a tool saves results in a file or returns data associated with a file or path, the full file path is included in the Final Answer, along with any relevant data or output from the tool.

For tools like Blastp, DownloadPDBStructure, and others, it is important to return the path where the data have been saved. Also, return a brief description of the data when available.

Remember:
- Be concise and direct
- Provide actionable and well-formatted information
- Include all relevant results and observations
- Always use the JSON blob format for valid actions, including Final Answer
- Do not use Thought as an action

Begin!
"""

    human_prompt = """{input}
    {agent_scratchpad}
    (Reminder: Only respond in a valid JSON blob, "response" is not a valid JSON blob key. Any deviation will be flagged and ignored.)"""

    memory = (
        ConversationBufferMemory(memory_key="history", return_messages=True)
        if use_memory
        else None
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", human_prompt),
        ]
    ).partial(
        tools=render_text_description_and_args(list(tools)),
        tool_names=", ".join([t.name for t in tools]),
    )

    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
            chat_history=lambda x: (  #  noqa: ARG005
                memory.chat_memory.messages
                if (use_memory and memory is not None)
                else []
            ),
        )
        | prompt
        | llm
        | CustomJSONAssistantOutputParser()
    )

    return AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=True, memory=memory, max_iterations=5)  # type: ignore[arg-type]
