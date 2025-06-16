## Langgraph Modular

This project provides a flexible and modular way to build AI agents using LangGraph. It allows you to define agent behaviors and configurations through YAML files, making it easy to modify and extend agent capabilities without changing the core code.

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your configuration (see Configuration section)

## Configuration

Create a `.env` file in the project root with the following variables:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## How to use


### YAML Configuration

The project uses YAML files to define agent behaviors and workflows. Here's how to configure your agents:

#### Basic Structure

```yaml
subgraphs:
  my_agent:
    prompt: "MY_AGENT_PROMPT"  # Name of the prompt variable
    tools:                     # Tools available to the agent
      - tool1
      - tool2
      - tool3
    route_function: "default_route_actor"  # Routing function to use
    agent_name: "actor"        # Agent implementation name
    next: "END"               # Next node in the graph
```

#### Router Configuration

```yaml
router:
  type: "function"
  function: "router_node"
  routes:
    agent1: "agent1_graph"
    agent2: "agent2_graph"
    agent3: "agent3_graph"
```

### Creating New Tools and Agents

1. **Add Prompts**
   - Add your prompt in `/tools/agent/prompts.py`
   - Use a descriptive variable name (e.g., `MY_AGENT_PROMPT`)

2. **Create Tools**
   - Create a new Python file in `/tools/agent/tools/` (e.g., `my_tool.py`)
   - Use the `@tool` decorator and provide a description:
   ```python
   @tool
   def my_tool():
       """Description of what the tool does."""
       # Tool implementation
   ```

3. **Register Tools**
   - Add your tool to `/tools/agent/tools/__init__.py`:
   ```python
   from .my_tool import my_tool
   
   __all__ = [
       # ... existing tools ...
       "my_tool"
   ]
   ```

4. **Register Prompts**
   - Register the prompt in `/tools/agent/prompts/__init__.py`:
   ```python
   from .prompts import MY_AGENT_PROMPT
   
   __all__ = [
       # ... existing prompts ...
       "MY_AGENT_PROMPT"
   ]
   ```

### Important Notes

- Route names in the YAML must match exactly with the prompt responses
- Each subgraph must specify a `next` node or `END`
- Tool names in the YAML must match the registered tool names
- The router configuration must be updated when adding new subgraphs
- The error handling expects an other agent in case the router prompt doesnt return a existing agent

## Future Work

- Integrate with other models as well as non API implementations (e.g.: ollama)
- Add option for creating graph image