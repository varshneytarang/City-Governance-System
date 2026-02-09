"""
Health tools for the Health Agent. Tools gather facts (surveillance, vaccination,
inspections, resources) and return normalized dicts. They reuse `health_agent.database`.
"""

from typing import Dict, Any
import logging

from .database import get_health_queries

logger = logging.getLogger(__name__)


class HealthTools:
    def __init__(self, queries=None):
        self.queries = queries or get_health_queries()

    def disease_surveillance_tool(self, location: str, days: int = 30) -> Dict[str, Any]:
        incidents = self.queries.get_disease_incidents(location=location, days=days)
        total = len(incidents)
        critical = [i for i in incidents if i.get('severity') == 'critical']

        return {
            'location': location,
            'incidence_count': total,
            'critical_incidents': len(critical),
            'recent_incidents': incidents[:10]
        }

    def vaccination_status_tool(self, location: str) -> Dict[str, Any]:
        campaigns = self.queries.get_vaccination_campaigns(location=location)
        coverage = None
        if campaigns:
            # take latest coverage if present
            coverage = campaigns[0].get('coverage_percent')

        return {
            'location': location,
            'campaigns': campaigns,
            'coverage_percent': coverage
        }

    def sanitation_inspection_tool(self, location: str) -> Dict[str, Any]:
        inspections = self.queries.get_sanitation_inspections(location=location)
        failed = [i for i in inspections if i.get('outcome') in ('fail', 'critical')]

        return {
            'location': location,
            'inspections_count': len(inspections),
            'failed_inspections': len(failed),
            'recent_inspections': inspections[:5]
        }

    def mobile_unit_availability(self) -> Dict[str, Any]:
        # Use health DB to infer mobile unit availability from facilities/services
        try:
            facilities = self.queries.get_health_facilities()
            # Count facilities that list 'mobile_unit' in services JSON or capacity>0
            count = 0
            locations = []
            for f in facilities:
                services = f.get('services') or {}
                # services may be JSON/object or text; try to detect mobile service
                svc_names = []
                if isinstance(services, dict):
                    svc_names = [k.lower() for k in services.keys()]
                elif isinstance(services, list):
                    svc_names = [str(s).lower() for s in services]
                elif isinstance(services, str):
                    svc_names = [s.strip().lower() for s in services.split(',')]

                if 'mobile_unit' in svc_names or 'mobile clinic' in svc_names:
                    count += 1
                    locations.append(f.get('location'))

            return {'available_units': count, 'locations': list(set(locations))}
        except Exception:
            return {'available_units': 0, 'locations': []}

    def public_messaging_capacity(self) -> Dict[str, Any]:
        return {'channels': ['radio', 'sms', 'social_media'], 'daily_capacity_messages': 1000}


def create_health_tools(queries=None) -> HealthTools:
    return HealthTools(queries)
