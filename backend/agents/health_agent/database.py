"""
Health database helpers. Reuses `water_agent.database.DatabaseConnection` for
connection management and provides health-specific query methods.
"""

import logging
import os
from typing import List, Dict, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

from .config import settings

logger = logging.getLogger(__name__)


class HealthDatabaseConnection:
    """Independent DB connection for Health Agent using HEALTH_ prefixed env vars."""

    def __init__(self):
        logger.info("🔌 Initializing HealthDatabaseConnection...")
        self.conn = None
        self.connect()
        logger.info("✓ HealthDatabaseConnection initialized successfully")

    def connect(self):
        try:
            # Prefer DATABASE_URL from Railway
            database_url = os.getenv("DATABASE_URL") or os.getenv("HEALTH_DATABASE_URL")
            if database_url:
                self.conn = psycopg2.connect(database_url, sslmode="require")
                logger.info(f"✓ Connected to health database via DATABASE_URL")
            else:
                # Fallback to individual env vars (local development only)
                self.conn = psycopg2.connect(
                    host=settings.DB_HOST,
                    port=settings.DB_PORT,
                    database=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD
                )
                logger.info(f"✓ Connected to health database: {settings.DB_NAME}@{settings.DB_HOST}:{settings.DB_PORT}")
            
            # Test connection with a simple query
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM health_resources")
                count = cur.fetchone()[0]
                logger.info(f"  Database verification: health_resources table has {count} records")
                
        except Exception as e:
            # Helpful context without leaking credentials
            logger.error(f"❌ Health DB connection failed!")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"   Host: {settings.DB_HOST}")
            logger.error(f"   Port: {settings.DB_PORT}")
            logger.error(f"   Database: {settings.DB_NAME}")
            logger.error(f"   User: {settings.DB_USER}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        try:
            if not self.conn or self.conn.closed:
                logger.warning("Database connection closed, reconnecting...")
                self.connect()
            
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Log at INFO level for debugging
                logger.info(f"🔍 Executing query: {query}")
                logger.info(f"   With params: {params}")
                cur.execute(query, params or ())
                results = cur.fetchall()
                logger.info(f"Query returned {len(results)} rows")
                if results:
                    sample = str(dict(results[0]))
                    logger.info(f"   First row sample: {sample[:150]}...")
                return results
        except Exception as e:
            logger.error(f"❌ Health DB query FAILED!")
            logger.error(f"   Error: {e}")
            logger.error(f"   Query: {query}")
            logger.error(f"   Params: {params}")
            logger.error(f"   Connection status: {self.conn.closed if self.conn else 'No connection'}")
            # Re-raise to see actual error in logs
            raise


class HealthQueries:
    def __init__(self, db: HealthDatabaseConnection = None):
        logger.info("📊 Initializing HealthQueries...")
        self.db = db or HealthDatabaseConnection()
        logger.info("✓ HealthQueries initialized successfully")

    def get_disease_incidents(self, location: Optional[str] = None, days: int = 30) -> List[Dict]:
        query = (
            "SELECT incident_id, incident_type, location, severity, reported_date, status, description "
            "FROM disease_incidents "
            "WHERE reported_date > CURRENT_TIMESTAMP - INTERVAL %s "
            "ORDER BY reported_date DESC"
        )
        params: Tuple = (f"{days} days",)
        if location:
            # add location filter
            query = query.replace("ORDER BY", "AND location = %s ORDER BY")
            params = (f"{days} days", location)

        results = self.db.execute_query(query, params)
        logger.info(f"✓ Retrieved {len(results)} disease incidents")
        return results

    def get_vaccination_campaigns(self, location: Optional[str] = None) -> List[Dict]:
        query = (
            "SELECT campaign_id, name, location, start_date, end_date, target_groups, coverage_percent, status "
            "FROM vaccination_campaigns WHERE 1=1"
        )
        params: Tuple = ()
        if location:
            query += " AND location = %s"
            params = (location,)

        results = self.db.execute_query(query, params)
        logger.info(f"✓ Retrieved {len(results)} vaccination campaigns")
        return results

    def get_sanitation_inspections(self, location: Optional[str] = None, recent_days: int = 90) -> List[Dict]:
        query = (
            "SELECT inspection_id, location, facility, inspection_date, outcome, notes "
            "FROM sanitation_inspections "
            "WHERE inspection_date > CURRENT_TIMESTAMP - INTERVAL %s "
            "ORDER BY inspection_date DESC"
        )
        params: Tuple = (f"{recent_days} days",)
        if location:
            query = query.replace("ORDER BY", "AND location = %s ORDER BY")
            params = (f"{recent_days} days", location)

        return self.db.execute_query(query, params)

    def get_vulnerable_populations(self, location: Optional[str] = None) -> List[Dict]:
        query = (
            "SELECT id, location, population_group, population_count, vulnerability_index "
            "FROM vulnerable_populations WHERE 1=1"
        )
        params: Tuple = ()
        if location:
            query += " AND location = %s"
            params = (location,)

        return self.db.execute_query(query, params)

    def get_health_facilities(self, location: Optional[str] = None) -> List[Dict]:
        query = (
            "SELECT facility_id, name, location, capacity, services, status "
            "FROM health_facilities WHERE 1=1"
        )
        params: Tuple = ()
        if location:
            query += " AND location = %s"
            params = (location,)

        results = self.db.execute_query(query, params)
        logger.info(f"✓ Retrieved {len(results)} health facilities")
        return results

    def get_health_resources(self, location: Optional[str] = None, resource_type: Optional[str] = None) -> List[Dict]:
        """Get medical supplies and equipment from health_resources table"""
        query = (
            "SELECT resource_id, resource_type, quantity, location, status, metadata "
            "FROM health_resources WHERE 1=1"
        )
        params: Tuple = ()
        conditions = []
        values = []
        
        if location:
            conditions.append("location ILIKE %s")
            values.append(f"%{location}%")
        if resource_type:
            conditions.append("resource_type ILIKE %s")
            values.append(f"%{resource_type}%")
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
            params = tuple(values)

        results = self.db.execute_query(query, params)
        logger.info(f"✓ Retrieved {len(results)} health resources (medical supplies)")
        if results:
            logger.info(f"  Sample resource: {results[0].get('resource_type')} - {results[0].get('quantity')} units at {results[0].get('location')}")
        return results

    def get_health_policies(self) -> List[Dict]:
        """Get health policies from health_policies table"""
        query = (
            "SELECT policy_id, policy_name, description, effective_date, metadata "
            "FROM health_policies "
            "ORDER BY effective_date DESC"
        )
        results = self.db.execute_query(query)
        logger.info(f"✓ Retrieved {len(results)} health policies")
        return results

    def get_health_surveillance_reports(self, days: int = 30) -> List[Dict]:
        """Get health surveillance reports from health_surveillance_reports table"""
        query = (
            "SELECT report_id, source, report_date, summary, severity_assessment "
            "FROM health_surveillance_reports "
            "WHERE report_date > CURRENT_TIMESTAMP - INTERVAL %s "
            "ORDER BY report_date DESC"
        )
        params: Tuple = (f"{days} days",)
        results = self.db.execute_query(query, params)
        logger.info(f"✓ Retrieved {len(results)} surveillance reports")
        return results

    def check_health_location_exists(self, location: str) -> bool:
        query = (
            "SELECT COUNT(*) as count FROM ("
            "SELECT DISTINCT location FROM health_facilities "
            "UNION SELECT DISTINCT location FROM vaccination_campaigns "
            "UNION SELECT DISTINCT location FROM sanitation_inspections) as locations "
            "WHERE location = %s"
        )
        result = self.db.execute_query(query, (location,))
        return bool(result and result[0].get('count', 0) > 0)


def get_health_queries(db: HealthDatabaseConnection = None) -> HealthQueries:
    return HealthQueries(db)
