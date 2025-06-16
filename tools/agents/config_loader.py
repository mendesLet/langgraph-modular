# tools/agents/config_loader.py

import yaml
from typing import Dict, Any
from pathlib import Path

class ConfigLoader:
    def __init__(self, config_path: str):
        
        if not Path(config_path).is_absolute():
            self.config_path = Path(__file__).parent.parent.parent / config_path
        else:
            self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config

    def get_router_config(self) -> Dict[str, Any]:
        """Get the router configuration from the YAML file."""
        return self.config.get('core_nodes', {}).get('router', {})
    
    def get_llm_config(self) -> Dict[str, Any]:
        return self.config['llm']
    
    def get_core_nodes(self) -> Dict[str, Any]:
        return self.config['core_nodes']
    
    def get_subgraphs(self) -> Dict[str, Any]:
        return self.config['subgraphs']
    
    def get_tools(self) -> Dict[str, Any]:
        return self.config['tools']