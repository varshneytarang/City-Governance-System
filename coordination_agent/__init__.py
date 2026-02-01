"""
Coordination Agent Module

Orchestrates multi-agent workflows, resolves conflicts between department agents,
and manages human-in-the-loop decision-making using hybrid decision system
(rule-based for simple conflicts, LLM-powered for complex negotiations).
"""

from .agent import CoordinationAgent
from .state import CoordinationState
from .config import CoordinationConfig

__all__ = ["CoordinationAgent", "CoordinationState", "CoordinationConfig"]
