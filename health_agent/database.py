"""
Health database helpers. Reuses `water_agent.database.DatabaseConnection` for
connection management and provides health-specific query methods.
"""

import logging
from typing import List, Dict, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

from .config import settings

logger = logging.getLogger(__name__)


class HealthDatabaseConnection:
    """Independent DB connection for Health Agent using HEALTH_ prefixed env vars."""

    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD
            )
            logger.info("✓ Connected to health database")
        except Exception as e:
            logger.error(f"Health DB connection failed: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Health DB query error: {e}")
            raise


class HealthQueries:
    def __init__(self, db: HealthDatabaseConnection = None):
        self.db = db or HealthDatabaseConnection()

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

        return self.db.execute_query(query, params)

    def get_vaccination_campaigns(self, location: Optional[str] = None) -> List[Dict]:
        query = (
            "SELECT campaign_id, name, location, start_date, end_date, target_groups, coverage_percent "
            "FROM vaccination_campaigns WHERE 1=1"
        )
        params: Tuple = ()
        if location:
            query += " AND location = %s"
            params = (location,)

        return self.db.execute_query(query, params)

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

        return self.db.execute_query(query, params)

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
