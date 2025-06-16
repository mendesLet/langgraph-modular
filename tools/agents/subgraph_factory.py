# automacall-agents/tools/agents/subgraph_factory.py

from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from tools.agents.runnable_llm import Assistant
from tools.agents.nodes import create_tool_node_with_fallback
from tools.agents.nodes.core import default_route_actor
from tools.agents.state import State
from tools.logger import log_message

import dotenv

dotenv.load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def make_subgraph(
    prompt,
    tools,
    complete_or_escalate,
    route_actor_fn=None,
    agent_name="actor",
    memory=None,
):
    if memory is None:
        memory = MemorySaver()
    if route_actor_fn is None:
        route_actor_fn = default_route_actor

    # Build agent runnable
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", prompt), ("placeholder", "{messages}")]
    ).partial(time=datetime.now)
    agent_runnable = prompt_template | llm.bind_tools(tools + [complete_or_escalate])

    # Build subgraph
    subgraph_builder = StateGraph(State)
    subgraph_builder.add_node(agent_name, Assistant(agent_runnable))
    subgraph_builder.add_node(
        f"{agent_name}_tools", create_tool_node_with_fallback(tools)
    )
    subgraph_builder.add_edge(f"{agent_name}_tools", agent_name)
    subgraph_builder.add_conditional_edges(
        agent_name,
        route_actor_fn,
        [f"{agent_name}_tools", END],
    )
    subgraph_builder.add_edge(f"{agent_name}_tools", agent_name)
    subgraph_builder.add_edge(START, agent_name)
    return subgraph_builder.compile(checkpointer=memory)