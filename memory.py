from typing import List
from pydantic import BaseModel, Field
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI

class ConversationSummaryBufferMessageHistory(BaseChatMessageHistory, BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    llm: ChatOpenAI
    k: int

    def add_messages(self, messages: List[BaseMessage]) -> None:
        existing_summary = None
        old_messages = None

        if self.messages and isinstance(self.messages[0], SystemMessage):
            existing_summary = self.messages.pop(0)

        self.messages.extend(messages)

        if len(self.messages) > self.k:
            num_to_drop = len(self.messages) - self.k
            old_messages = self.messages[:num_to_drop]
            self.messages = self.messages[-self.k:]

        if old_messages:
            summary_prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(
                    "Given the existing conversation summary and the new messages, "
                    "generate a new summary of the conversation. Ensure to maintain "
                    "as much relevant information as possible."
                ),
                HumanMessagePromptTemplate.from_template(
                    "Existing conversation summary:\n{existing_summary}\n\n"
                    "New messages:\n{old_messages}"
                )
            ])

            existing_summary_text = existing_summary.content if existing_summary else ""
            old_messages_text = "\n".join([msg.content for msg in old_messages])
            new_summary = self.llm.invoke(
                summary_prompt.format_messages(
                    existing_summary=existing_summary_text,
                    old_messages=old_messages_text
                )
            )
            self.messages = [SystemMessage(content=new_summary.content)] + self.messages

    def clear(self) -> None:
        self.messages = []
