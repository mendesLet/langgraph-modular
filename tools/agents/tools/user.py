# tools/agents/tools/user.py

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

@tool
def fetch_client_information(config: RunnableConfig) -> dict:
    """
    Fetches client information.

    Returns:
      - A dictionary with client information.
    """
    return f"""
           The user id is: {config.get("configurable", {}).get("user_id")}
    """
