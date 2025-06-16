# tools/agents/graph_builder.py

import importlib
import inspect
from typing import Dict, Any, Callable, List
from langgraph.graph import StateGraph, START, END
from tools.agents.config_loader import ConfigLoader
from tools.agents.subgraph_factory import make_subgraph
from tools.agents.state import State
from tools.agents.tools import CompleteOrEscalate  
from tools.agents.nodes import (
    input_guardrail,
    is_about_agent_content,
    hardcoded_input_response,
    router_node,
    DynamicRouter,
    create_router_type
)


class GraphBuilder:
    def __init__(self, config_loader: ConfigLoader) -> None:
        self.config: ConfigLoader = config_loader
        self.builder: StateGraph = StateGraph(State)
        self.router: DynamicRouter = DynamicRouter(self.config.get_router_config())
        self.router_type = create_router_type(config_loader)

    def _get_function(self, function_name: str):
        nodes_module = importlib.import_module("tools.agents.nodes")
        function = inspect.getmembers(nodes_module, inspect.isfunction)

        for name, func in function:
            if name == function_name:
                return func

        raise ValueError(f"Function {function_name} not found")

    def _convert_end(self, value: str) -> Any:
        """Convert string 'END' to END constant if needed."""
        if value == "END":
            return END
        return value

    def _get_tools(self, tool_names: list):
        """Get a list of tools by their names."""
        tools_module = importlib.import_module("tools.agents.tools")
        found_tools = []
        
        for tool_name in tool_names:
            if hasattr(tools_module, tool_name):
                found_tools.append(getattr(tools_module, tool_name))
            else:
                raise ValueError(f"Tool {tool_name} not found")
                
        return found_tools
        
    def _get_prompt(self, prompt_name: str):
        """Get a prompt by name."""
        prompts_module = importlib.import_module("tools.agents.prompts")
        if hasattr(prompts_module, prompt_name):
            return getattr(prompts_module, prompt_name)
        raise ValueError(f"Prompt {prompt_name} not found")
        
    def build_core_nodes(self):
        core_nodes = self.config.get_core_nodes()
        
        # Add fetch_user_info
        self.builder.add_node(
            "fetch_user_info",
            self._get_function(core_nodes['fetch_user_info']['function'])
        )
        
        # Add input_guardrail
        self.builder.add_node(
            "input_guardrail_node",
            input_guardrail
        )
        
        # Add hardcoded_input_response
        self.builder.add_node(
            "hardcoded_input_response",
            hardcoded_input_response
        )
        
        # Add router
        self.builder.add_node(
            "router",
            router_node
        )
        
        # Add edges
        self.builder.add_edge(START, "fetch_user_info")
        self.builder.add_edge("fetch_user_info", "input_guardrail_node")
        self.builder.add_conditional_edges(
            "input_guardrail_node",
            is_about_agent_content,
            ["hardcoded_input_response", "router"]
        )
        
        # Add dynamic conditional edges for router
        routes = [self._convert_end(route) for route in self.router.routes.values()]
        self.builder.add_conditional_edges(
            "router",
            self.router.route_after_prediction,
            routes
        )

    def build_subgraphs(self):
        subgraphs = self.config.get_subgraphs()
        
        for name, config in subgraphs.items():
            subgraph = make_subgraph(
                prompt=self._get_prompt(config['prompt']),
                tools=self._get_tools(config['tools']),
                complete_or_escalate=CompleteOrEscalate,
                route_actor_fn=self._get_function(config['route_function']),
                agent_name=config['agent_name']
            )
            
            self.builder.add_node(f"{name}_graph", subgraph)
            self.builder.add_edge(f"{name}_graph", END)
            
    def build(self):
        self.build_core_nodes()
        self.build_subgraphs()
        return self.builder.compile()