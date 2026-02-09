"""
Examples for the Health Department Agent (quick smoke tests).
"""

from agents.health_agent import HealthDepartmentAgent


def example_sanitation_closure():
    agent = HealthDepartmentAgent()
    request = {
        'type': 'sanitation_work_schedule',
        'location': 'Zone-12',
        'details': 'Road closure for 5 days for sewer repair',
        'requested_days': 5
    }
    response = agent.decide(request)
    print('Health agent response:', response)
    agent.close()


if __name__ == '__main__':
    example_sanitation_closure()
