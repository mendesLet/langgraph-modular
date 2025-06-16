"""Logger for registering messages, errors, and other information"""

import logging

# Logging configuration
LOG_FILE = "agent.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def log_message(level, message):
    """
    Adds a message to the log.

    Args:
        level (str): Log level ('info', 'warning', 'error', 'debug', 'critical').
        message (str): Message to be logged.
    """
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)
    elif level == "critical":
        logging.critical(message)
    else:
        logging.info(f"UNKNOWN LEVEL: {message}")


def format_response(result):
    """Formats the model response into the desired format."""
    formatted = {
        "content": result.content,
        "tool_calls": [],
        "metadata": {
            "token_usage": result.response_metadata.get("token_usage", {}),
            "model_name": result.response_metadata.get("model_name"),
            "finish_reason": result.response_metadata.get("finish_reason"),
        },
        "id": result.id,
    }

    # Format tool calls if any
    if result.tool_calls:
        for tool in result.tool_calls:
            formatted["tool_calls"].append(
                {
                    "name": tool.get("name"),
                    "arguments": tool.get("args"),
                    "id": tool.get("id"),
                    "type": tool.get("type"),
                }
            )

    return formatted
