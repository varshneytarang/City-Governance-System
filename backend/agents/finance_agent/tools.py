"""Finance tools (scaffold).

Lightweight helpers used by the Finance agent. Keep deterministic and
safe for initial scaffold.
"""

from typing import Dict
from .config import settings


class FinanceTools:
    def __init__(self, settings):
        self.settings = settings

    def check_budget_availability(self, estimated_cost: float = None) -> Dict:
        total = float(self.settings.BUDGET_TOTAL)
        # Scaffold: no spent tracking, assume full budget available
        remaining = total
        can_afford = True if (estimated_cost is None or remaining >= estimated_cost) else False

        return {
            "total_budget": total,
            "remaining": remaining,
            "estimated_cost": estimated_cost,
            "can_afford": can_afford,
        }


def create_tools(settings) -> FinanceTools:
    return FinanceTools(settings)
