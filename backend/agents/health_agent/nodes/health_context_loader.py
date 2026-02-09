"""
Node: health_context_loader
Populates `state['context']` with health-related context using `health_agent.database`.
"""

import logging
from typing import Dict

from ..database import get_health_queries

logger = logging.getLogger(__name__)


def health_context_loader(state: Dict) -> Dict:
    logger.info("📊 [NODE: Health Context Loader] - STARTING")
    try:
        input_event = state.get('input_event', {})
        location = input_event.get('location')
        
        # Ignore generic/placeholder location values - treat them as "no location filter"
        if location and location.lower() in ['general', 'all', 'any', 'city', 'citywide']:
            logger.info(f"⚠ Ignoring generic location filter: '{location}' - loading ALL data")
            location = None
        elif location:
            logger.info(f"📍 Loading data for specific location: '{location}'")
        else:
            logger.info(f"📊 No location filter - loading ALL data")
        
        logger.info(f"Attempting to connect to database and load health context...")
        queries = get_health_queries()
        logger.info(f"✓ Database connection established")

        context = {}
        
        # Load disease incidents
        try:
            if location:
                context['disease_incidents'] = queries.get_disease_incidents(location=location, days=30)
            else:
                context['disease_incidents'] = queries.get_disease_incidents(days=30)
        except Exception as e:
            logger.error(f"Failed to load disease_incidents: {e}", exc_info=True)
            context['disease_incidents'] = []
        
        # Load vaccination campaigns  
        try:
            if location:
                context['vaccination_campaigns'] = queries.get_vaccination_campaigns(location=location)
            else:
                context['vaccination_campaigns'] = queries.get_vaccination_campaigns()
        except Exception as e:
            logger.error(f"Failed to load vaccination_campaigns: {e}", exc_info=True)
            context['vaccination_campaigns'] = []
        
        # Load sanitation inspections
        try:
            if location:
                context['sanitation_inspections'] = queries.get_sanitation_inspections(location=location)
            else:
                context['sanitation_inspections'] = queries.get_sanitation_inspections()
        except Exception as e:
            logger.error(f"Failed to load sanitation_inspections: {e}", exc_info=True)
            context['sanitation_inspections'] = []
        
        # Load vulnerable populations
        try:
            if location:
                context['vulnerable_populations'] = queries.get_vulnerable_populations(location=location)
            else:
                context['vulnerable_populations'] = queries.get_vulnerable_populations()
        except Exception as e:
            logger.error(f"Failed to load vulnerable_populations: {e}", exc_info=True)
            context['vulnerable_populations'] = []
        
        # Load health facilities
        try:
            if location:
                context['health_facilities'] = queries.get_health_facilities(location=location)
            else:
                context['health_facilities'] = queries.get_health_facilities()
        except Exception as e:
            logger.error(f"Failed to load health_facilities: {e}", exc_info=True)
            context['health_facilities'] = []
        
        # ALWAYS load health resources (medical supplies)
        try:
            if location:
                context['health_resources'] = queries.get_health_resources(location=location)
            else:
                context['health_resources'] = queries.get_health_resources()
        except Exception as e:
            logger.error(f"Failed to load health_resources: {e}", exc_info=True)
            context['health_resources'] = []
        
        # Load health policies
        try:
            context['health_policies'] = queries.get_health_policies()
        except Exception as e:
            logger.error(f"Failed to load health_policies: {e}", exc_info=True)
            context['health_policies'] = []
        
        # Load health surveillance reports
        try:
            context['health_surveillance_reports'] = queries.get_health_surveillance_reports(days=30)
        except Exception as e:
            logger.error(f"Failed to load health_surveillance_reports: {e}", exc_info=True)
            context['health_surveillance_reports'] = []

        state['context'] = context
        
        # Detailed logging of what was loaded
        logger.info(f'✓ Health context loaded:')
        logger.info(f'  - Health Resources (supplies): {len(context.get("health_resources", []))} items')
        logger.info(f'  - Vaccination Campaigns: {len(context.get("vaccination_campaigns", []))} campaigns')
        logger.info(f'  - Health Facilities: {len(context.get("health_facilities", []))} facilities')
        logger.info(f'  - Disease Incidents: {len(context.get("disease_incidents", []))} incidents')
        logger.info(f'  - Sanitation Inspections: {len(context.get("sanitation_inspections", []))} inspections')
        logger.info(f'  - Vulnerable Populations: {len(context.get("vulnerable_populations", []))} groups')
        logger.info(f'  - Health Policies: {len(context.get("health_policies", []))} policies')
        logger.info(f'  - Surveillance Reports: {len(context.get("health_surveillance_reports", []))} reports')
        
        # Log sample data if available
        if context.get("health_resources"):
            logger.debug(f'  Sample health resource: {context["health_resources"][0]}')
        
        return state
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR in health_context_loader: {e}", exc_info=True)
        # Return empty context to prevent agent from crashing
        state['context'] = {
            'health_resources': [],
            'vaccination_campaigns': [],
            'health_facilities': [],
            'disease_incidents': [],
            'sanitation_inspections': [],
            'vulnerable_populations': [],
            'health_policies': [],
            'health_surveillance_reports': []
        }
        return state
