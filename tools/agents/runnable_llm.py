"""Runnable LLM class."""

from langchain_core.runnables import Runnable, RunnableConfig
from tools.agents.state import State
from tools.logger import log_message, format_response


# Assistant that will wrap each agent and will be triggered whenever the agent needs to respond.
# pylint: disable=too-few-public-methods
class Assistant:
    """Assistant that wraps the agent and processes the response."""

    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)

            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [
                    ("user", "Please respond with a valid output.")
                ]
                state = {**state, "messages": messages}
            else:
                break

        log_message("info", f"Agent response: {format_response(result)}")

        return {"messages": result}