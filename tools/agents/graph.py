# tools/agents/graph.py

from tools.agents.config_loader import ConfigLoader
from tools.agents.graph_builder import GraphBuilder

def create_graph():
    config_loader = ConfigLoader("config/architecture.yaml")
    graph_builder = GraphBuilder(config_loader)
    return graph_builder.build()

final_graph = create_graph()