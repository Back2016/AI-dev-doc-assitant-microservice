# prompts/agent_prompt.py

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

agent_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful assistant that can call the `retrieval_tool` to fetch relevant document chunks.\n"
     "When you need to look up information in our indexed documents, call `retrieval_tool(query)` with the exact user question.\n"
     "Then use that output in your reasoning."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])
