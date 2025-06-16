# tools/agents/nodes/core.py

from typing import Literal
from langchain_core.messages import ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from tools.agents.state import State
from tools.agents.prompts import INPUT_GUARDRAIL_PROMPT
from tools.agents.tools import fetch_client_information
from tools.logger import log_message
from tools.agents.nodes.types import AboutAgentContent
from langgraph.prebuilt import tools_condition
from langgraph.graph import END

def pop_dialog_state(state: State) -> dict:
    """Opens the dialog stack and returns to supervisor."""
    messages = []
    if state["messages"][-1].tool_calls:
        messages.append(
            ToolMessage(
                content="Resuming dialogue with supervisor. "
                "Reflect on the previous conversation and help the user "
                "as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }

def normal_llm_node(state: State):
    """Default agent route. PLACEHOLDER"""
    system_message = "Respond normally"
    messages = [{"role": "system", "content": system_message}] + state["messages"]
    model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    response = model.invoke(messages)
    return {"messages": [response]}

def input_guardrail(state: State):
    """Inference to determine if the subject is within the agent's context."""
    messages = state["messages"]
    about_context_prompt = INPUT_GUARDRAIL_PROMPT
    messages = [{"role": "system", "content": about_context_prompt}] + messages
    model = ChatOpenAI(temperature=0, model_name="gpt-4o").with_structured_output(
        AboutAgentContent
    )
    response = model.invoke(messages)
    return {"about_context": response["about_context"]}

def is_about_agent_content(
    state: State,
) -> Literal["hardcoded_input_response", "router"]:
    """Route to take after determining if the user query is within the agent's context."""
    log_message("info", f"Input Guardrail: {state['about_context']}")
    if not state["about_context"]:
        return "hardcoded_input_response"
    return "router"

def hardcoded_input_response(state: State):
    """Returns a standard response when the user query is not within context."""
    response = {
        "messages": [
            AIMessage(
                content="I apologize, but I cannot handle your specific request. "
            )
        ]
    }
    return response

def user_info(state: State):
    """Returns the user information."""
    return {"user_info": fetch_client_information.invoke({})}

def default_route_actor(state: State):
    """Default routing function for actor nodes."""
    route = tools_condition(state)
    log_message("info", "Agent is in the flow using the Actor")
    if route == END:
        return END
    return "actor_tools"
