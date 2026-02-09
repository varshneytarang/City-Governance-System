"""
Quick test script to verify health database connectivity and data availability
"""

import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agents.health_agent.database import get_health_queries

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and query health_resources"""
    
    logger.info("=" * 80)
    logger.info("HEALTH DATABASE CONNECTION TEST")
    logger.info("=" * 80)
    
    try:
        logger.info("\n1. Connecting to database...")
        queries = get_health_queries()
        logger.info("   ✓ Connection successful!\n")
        
        logger.info("2. Querying health_resources table...")
        resources = queries.get_health_resources()
        logger.info(f"   ✓ Query successful! Retrieved {len(resources)} resources\n")
        
        if resources:
            logger.info("3. Sample data:")
            for i, resource in enumerate(resources[:3], 1):
                logger.info(f"\n   Resource #{i}:")
                logger.info(f"      Type: {resource.get('resource_type')}")
                logger.info(f"      Quantity: {resource.get('quantity')}")
                logger.info(f"      Location: {resource.get('location')}")
                logger.info(f"      Status: {resource.get('status')}")
        else:
            logger.warning("   ⚠ No resources found in table!")
            
        logger.info("\n4. Querying other tables...")
        campaigns = queries.get_vaccination_campaigns()
        logger.info(f"   Vaccination campaigns: {len(campaigns)}")
        
        facilities = queries.get_health_facilities()
        logger.info(f"   Health facilities: {len(facilities)}")
        
        incidents = queries.get_disease_incidents()
        logger.info(f"   Disease incidents: {len(incidents)}")
        
        logger.info("\n" + "=" * 80)
        logger.info("TEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error("\n" + "=" * 80)
        logger.error("TEST FAILED")
        logger.error("=" * 80)
        logger.error(f"Error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
