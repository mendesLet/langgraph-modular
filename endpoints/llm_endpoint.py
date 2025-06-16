"""LLM WebSocket Endpoint"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from endpoints.models import LlmRequest
from tools.agents.graph import final_graph
from tools.logger import log_message

router = APIRouter()


@router.websocket("/ws/llm_processing/")
async def llm_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for processing real-time LLM requests.

    This endpoint receives JSON messages with user queries, processes them using
    a graph-based text generation system, and streams responses back to the client.

    Expected JSON structure:
    {
        "id": "<unique_request_id>",
        "flag": "<request_flag>",
        "details": {
            "request": "<user_query>",
            "user_info": {
                "user_id": "<user_id>"
            }
        }
    }

    Workflow:
    - Accepts WebSocket connections.
    - Processes user queries and streams responses.
    - Handles errors and disconnections gracefully.
    """
    try:
        await websocket.accept()
        same_message_id = []

        while True:
            try:
                data = await websocket.receive_json()
                request = LlmRequest(**data)
                query = request.details.request
                id_call = request.id

                config = {
                    "configurable": {
                        "thread_id": id_call,
                        "user_id": request.details.user_info.user_id,
                    }
                }

                def text_generator():
                    for message, _ in final_graph.stream(
                        {"messages": ("user", query)},
                        config,
                        stream_mode="messages",
                    ):
                        if message.content != "":
                            if message.id.split("-")[0] == "run":
                                if not message.response_metadata:
                                    yield message.content
                            elif (
                                "I apologize, but I cannot handle your specific request."
                                in message.content
                            ):
                                if message.id not in same_message_id:
                                    same_message_id.append(message.id)
                                    yield message.content

                for text_chunk in text_generator():
                    if text_chunk and text_chunk.strip():
                        await websocket.send_json(
                            {
                                "id": id_call,
                                "flag": "generating",
                                "details": {"response": text_chunk},
                            }
                        )

                await websocket.send_json(
                    {
                        "id": id_call,
                        "flag": "completed",
                        "details": {"response": "Processing complete."},
                    }
                )

            except json.JSONDecodeError:
                log_message("error", "Invalid JSON received, ignoring...")
                continue

            except WebSocketDisconnect:
                log_message("warning", f"WebSocket disconnected for ID: {id_call}")
                break

            except Exception as e: # pylint: disable=broad-except
                log_message("error", f"Unexpected WebSocket error: {str(e)}")
                await websocket.send_json(
                    {
                        "id": id_call,
                        "flag": "ERROR_LLM",
                        "details": str(e),
                    }
                )

    except Exception as e: # pylint: disable=broad-except
        log_message("error", f"Fatal error in WebSocket: {e}")
