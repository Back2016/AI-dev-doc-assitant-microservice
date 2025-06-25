import asyncio
import os
from dotenv import load_dotenv

from typing import List, Optional
from pydantic import BaseModel, Field, SecretStr
import json

from langchain.callbacks.base import AsyncCallbackHandler
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# ==== Load env ====
load_dotenv()
OPENAI_API_KEY = SecretStr(os.environ["OPENAI_API_KEY"])

# ==== Import your tools ====
from tools.math_tools import add, multiply, exponentiate, subtract, evaluate_expression
from tools.rag_tool import retrieval_tool
from tools.search_tools import serpapi, Article

# === Log management ===#
import logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)

@tool
async def final_answer(answer: str, tools_used: Optional[list[str]] = None) -> dict[str, str | list[str]]:
    """Use this tool to provide a final answer to the user."""
    return {"answer": answer, "tools_used": tools_used or []}

tools = [add, subtract, multiply, exponentiate, final_answer, retrieval_tool, evaluate_expression]
name2tool = {tool.name: tool.coroutine for tool in tools}

# ==== ConversationSummaryBufferMessageHistory ====

class ConversationSummaryBufferMessageHistory(BaseChatMessageHistory, BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    llm: ChatOpenAI
    k: int

    def __init__(self, llm: ChatOpenAI, k: int, **kwargs):
        super().__init__(llm=llm, k=k, **kwargs)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add messages to the history, summarizing anything beyond k messages."""
        existing_summary: SystemMessage | None = None
        old_messages: List[BaseMessage] | None = None

        if len(self.messages) > 0 and isinstance(self.messages[0], SystemMessage):
            existing_summary = self.messages.pop(0)

        self.messages.extend(messages)
        old_messages = None

        if len(self.messages) > self.k:
            num_to_drop = len(self.messages) - self.k
            old_messages = self.messages[:num_to_drop]
            self.messages = self.messages[-self.k:]

        if old_messages is None:
            return

        summary_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Given the existing conversation summary and the new messages, "
                "generate a new summary of the conversation. Ensure to keep as much relevant information as possible."
            ),
            HumanMessagePromptTemplate.from_template(
                "Existing conversation summary:\n{existing_summary}\n\n"
                "New messages:\n{old_messages}"
            )
        ])

        existing_summary_text = existing_summary.content if existing_summary else ""
        old_messages_text = "\n".join([msg.content for msg in old_messages])
        summary_messages = summary_prompt.format_messages(
            existing_summary=existing_summary_text,
            old_messages=old_messages_text
        )

        # Call LLM to get summary (sync here; adapt if you want async)
        new_summary = self.llm.invoke(summary_messages)
        self.messages = [SystemMessage(content=new_summary.content)] + self.messages

    def clear(self) -> None:
        self.messages = []

# ==== LLM and prompt ====

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    streaming=True,
    api_key=OPENAI_API_KEY
)

prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You're a helpful assistant. You have access to several tools: "
        "math functions including basic operation (add, subtract, multiply, and exp) tools based on natural language"
        "and a complex expression evaluation tool,"
        " web search, and a documentation retrieval tool. "
        "When passing an expression to evaluate_expression, ensure it is a valid mathematical formula"
        "and matches the user's original input, without omitting or changing any characters. "
        "Do not remove any operators, and do not add or omit spaces or numbers."
        "When a user asks about programming, code, APIs, or anything that may be covered in internal or project documentation, "
        "ALWAYS use the document retrieval tool first. "
        "For current events or things that aren't covered by documentation, use the web search tool."
        "After using a tool, the output will be provided back to you. When you have all the information, "
        "If you have already tried retrieving documentation or searching, and no relevant answer is found, "
        "you MUST use your own general knowledge and respond using the `final_answer` tool. "
        "Never repeat the same retrieval or search step more than once for the same question. "
        "If nothing is found after one attempt, use your own knowledge to answer the user's question via `final_answer`."
        "you MUST use the final_answer tool to provide a final answer."
    )),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# ==== Streaming Handler ====

class QueueCallbackHandler(AsyncCallbackHandler):
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self.final_answer_seen = False

    async def __aiter__(self):
        while True:
            if self.queue.empty():
                await asyncio.sleep(0.1)
                continue
            token_or_done = await self.queue.get()
            if token_or_done == "<<DONE>>":
                return
            if token_or_done:
                yield token_or_done

    async def on_llm_new_token(self, *args, **kwargs) -> None:
        chunk = kwargs.get("chunk")
        if chunk and chunk.message.additional_kwargs.get("tool_calls"):
            if chunk.message.additional_kwargs["tool_calls"][0]["function"]["name"] == "final_answer":
                self.final_answer_seen = True
        self.queue.put_nowait(kwargs.get("chunk"))

    async def on_llm_end(self, *args, **kwargs) -> None:
        if self.final_answer_seen:
            self.queue.put_nowait("<<DONE>>")
        else:
            self.queue.put_nowait("<<STEP_END>>")

async def execute_tool(tool_call: AIMessage, selected_source=None) -> ToolMessage:
    tool_name = tool_call.tool_calls[0]["name"]
    tool_args = tool_call.tool_calls[0]["args"]
    if tool_name == "retrieval_tool" and selected_source:
        tool_args["source"] = selected_source
    tool_out = await name2tool[tool_name](**tool_args)
    return ToolMessage(
        content=f"{tool_out}",
        tool_call_id=tool_call.tool_calls[0]["id"]
    )

# ==== Agent Executor ====

class CustomAgentExecutor:
    def __init__(self, max_iterations: int = 3, k: int = 6):
        # session_id -> ConversationSummaryBufferMessageHistory
        self.memory_map: dict[str, ConversationSummaryBufferMessageHistory] = {}
        self.max_iterations = max_iterations
        self.k = k
        self.llm = llm
        self.agent = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: x.get("agent_scratchpad", [])
            }
            | prompt
            | self.llm.bind_tools(tools, tool_choice="any")
        )

    def get_memory(self, session_id: str) -> ConversationSummaryBufferMessageHistory:
        if session_id not in self.memory_map:
            self.memory_map[session_id] = ConversationSummaryBufferMessageHistory(
                llm=self.llm, k=self.k
            )
        return self.memory_map[session_id]

    def print_chat_history(self, session_id: str):
        memory = self.get_memory(session_id)
        logging.info(f"\n===== Chat History for session '{session_id}' =====")
        for msg in memory.messages:
            if isinstance(msg, SystemMessage):
                logging.info(f"# ~~ summary:\n{msg.content}")
            elif isinstance(msg, HumanMessage):
                logging.info(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                logging.info(f"AI: {msg.content}")
        logging.info("==============================================\n")

    async def invoke(self, input: str, streamer: QueueCallbackHandler, session_id: str, selected_source: Optional[str] = None, verbose: bool = False) -> dict:
        memory = self.get_memory(session_id)
        chat_history = memory.messages
        count = 0
        final_answer: str | None = None
        final_answer_call: dict | None = None
        agent_scratchpad: list[AIMessage | ToolMessage] = []

        async def stream(query: str) -> list[AIMessage]:
            response = self.agent.with_config(
                callbacks=[streamer]
            )
            outputs = []
            async for token in response.astream({
                "input": query,
                "chat_history": chat_history,
                "agent_scratchpad": agent_scratchpad
            }):
                tool_calls = token.additional_kwargs.get("tool_calls")
                if tool_calls:
                    if tool_calls[0]["id"]:
                        outputs.append(token)
                    else:
                        outputs[-1] += token
                else:
                    pass
            return [
                AIMessage(
                    content=x.content,
                    tool_calls=x.tool_calls,
                    tool_call_id=x.tool_calls[0]["id"]
                ) for x in outputs
            ]

        while count < self.max_iterations:
            tool_calls = await stream(query=input)
            tool_obs = await asyncio.gather(
                *[execute_tool(tool_call, selected_source=selected_source) for tool_call in tool_calls]
            )
            id2tool_obs = {tool_call.tool_call_id: tool_obs for tool_call, tool_obs in zip(tool_calls, tool_obs)}
            for tool_call in tool_calls:
                agent_scratchpad.extend([
                    tool_call,
                    id2tool_obs[tool_call.tool_call_id]
                ])
            count += 1
            found_final_answer = False
            for tool_call in tool_calls:
                if tool_call.tool_calls[0]["name"] == "final_answer":
                    final_answer_call = tool_call.tool_calls[0]
                    final_answer = final_answer_call["args"]["answer"]
                    found_final_answer = True
                    break
            if found_final_answer:
                break

        # Add the input and final output as messages and update summary if needed
        memory.add_messages([
            HumanMessage(content=input),
            AIMessage(content=final_answer if final_answer else "No answer found")
        ])

        self.print_chat_history(session_id)
        return (final_answer_call if final_answer else {"answer": "No answer found", "tools_used": []}, agent_scratchpad)

# ==== Initialize agent_executor ====
agent_executor = CustomAgentExecutor()
