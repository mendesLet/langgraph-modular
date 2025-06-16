"""State for the agent."""

from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, MessagesState, add_messages


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class State(TypedDict):
    """State for the agent."""

    messages: Annotated[list[AnyMessage], add_messages]
    about_context: bool
    user_info: str
    dialog_state: Annotated[
        list[
            Literal[
                "informer",
                "actor",
            ]
        ],
        update_dialog_stack,
    ]
