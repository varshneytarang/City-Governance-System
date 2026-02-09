"""
Node: health_planner
Simple planner wrapper: can call an LLM-based planner (reusing `water_agent` planner)
or return deterministic health mitigation suggestions.
"""

import logging
from typing import Dict

from .health_planner_llm import health_planner_llm_node

# health_planner_llm_node implements the planner for the health agent

def health_planner_node(state: Dict) -> Dict:
    return health_planner_llm_node(state)
