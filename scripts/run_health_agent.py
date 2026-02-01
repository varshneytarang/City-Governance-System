"""Simple runner to exercise the HealthDepartmentAgent manually.

Usage: python scripts/run_health_agent.py
"""
from health_agent.agent import HealthDepartmentAgent


def main():
    agent = HealthDepartmentAgent()

    request = {
        "type": "health_assessment",
        "location": "Industrial Zone A",
        "symptoms_reported": ["fever", "nausea"],
        "details": {"reported_by": "clinic_123"}
    }

    resp = agent.decide(request)
    print("Health agent response:")
    print(resp)


if __name__ == "__main__":
    main()
