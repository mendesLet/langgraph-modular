# tools/agents/nodes/types.py

from typing import TypedDict, Literal
from tools.agents.config_loader import ConfigLoader

def create_router_type(config_loader: ConfigLoader):
    """Creates a dynamic Router type based on configuration."""
    router_config = config_loader.get_router_config()
    routes = router_config.get('routes', {})
    
    route_literals = Literal[tuple(routes.keys())]
    
    class Router(TypedDict):
        """Router node output."""
        route: route_literals
    
    return Router

class AboutAgentContent(TypedDict):
    """Is the user query within context?"""
    about_context: bool