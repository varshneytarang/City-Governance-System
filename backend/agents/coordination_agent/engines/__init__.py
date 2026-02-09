"""
Engines package for coordination agent

Includes:
- Conflict Detector: Identifies conflicts between agent decisions
- Rule Engine: Rule-based resolution for simple conflicts
- LLM Engine: LLM-powered negotiation for complex conflicts
"""

from .conflict_detector import ConflictDetector
from .rule_engine import RuleEngine
from .llm_engine import LLMNegotiationEngine

__all__ = ["ConflictDetector", "RuleEngine", "LLMNegotiationEngine"]
