# tools/agents/nodes/router.py

from typing import Dict, Any, Literal
from langchain_openai import ChatOpenAI
from tools.agents.state import MessagesState
from tools.agents.prompts import ROUTER_PROMPT
from tools.logger import log_message
from tools.agents.config_loader import ConfigLoader
from tools.agents.nodes.types import create_router_type

class RouterState(MessagesState):
    """State for the router node."""
    
    def __init__(self, config_loader: ConfigLoader):
        router_config = config_loader.get_router_config()
        self.route: Literal = router_config.get('routes', {}).keys()
        super().__init__()

def router_node(state: RouterState):
    """Inference to define the agent's route."""

    system_message = ROUTER_PROMPT 
    messages = [{"role": "system", "content": system_message}] + state["messages"]
    
    # Create a new Router type with the current config
    config_loader = ConfigLoader("config/architecture.yaml")
    Router = create_router_type(config_loader)

    model = ChatOpenAI(temperature=0, model_name="gpt-4o").with_structured_output(Router)
    route = model.invoke(messages)
    
    if not route or "route" not in route:
        log_message("error", "Router returned invalid response format")
        return {"route": "other"}
        
    return {"route": route["route"]}

    

class DynamicRouter:
    def __init__(self, route_config: Dict[str, Any]):
        self.route_config = route_config
        self.routes = route_config.get('routes', {})
        
    def route_after_prediction(self, state: RouterState) -> str:
        """
        Dynamic routing based on configuration.
        
        Args:
            state: The current state containing the route decision
            
        Returns:
            str: The name of the next node to execute
        """
        route = state.get('route')
        if not route:
            log_message("error", "No route found in state")
            return "other_graph"
            
        log_message("info", f"Route taken by agent: {route}")
        
        # Get the configured route
        next_node = self.routes.get(route)
        if not next_node:
            log_message("error", f"No configured route found for: {route}")
            return "other_graph"
            
        return next_node