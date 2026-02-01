"""Simple runner to exercise the FinanceDepartmentAgent manually.

Usage: python scripts/run_finance_agent.py
"""
from finance_agent import FinanceDepartmentAgent


def main():
    agent = FinanceDepartmentAgent()

    request = {
        "type": "finance_assessment",
        "location": "CityCenter",
        "estimated_cost": 5000,
        "details": {"project": "Repair main pipeline"}
    }

    resp = agent.decide(request)
    print("Finance agent response:")
    print(resp)


if __name__ == "__main__":
    main()
