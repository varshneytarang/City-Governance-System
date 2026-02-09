"""
Database connection and query utilities for Finance Department
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

from .config import settings

logger = logging.getLogger(__name__)


class FinanceDepartmentDatabase:
    """Finance DB connection and query helpers"""
    
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        import os
        try:
            # Use DATABASE_URL from Railway (mandatory)
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                self.conn = psycopg2.connect(database_url, sslmode="require")
                logger.info(f"✓ Connected to database (Finance) via DATABASE_URL")
            else:
                # Fallback to individual env vars (local development only)
                self.conn = psycopg2.connect(
                    host=settings.DB_HOST,
                    port=settings.DB_PORT,
                    database=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD
                )
                logger.info(f"✓ Connected to {settings.DB_NAME} (Finance)")
        except psycopg2.Error as e:
            logger.error(f"✗ Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results as list of dicts"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Query error: {e}")
            raise
    
    # ========== BUDGET QUERIES ==========
    
    def get_department_budgets(self, department: Optional[str] = None) -> List[Dict]:
        """Get budget status for all or specific department"""
        query = \"\"\"\n            SELECT budget_id, department, year, month, total_budget, allocated, spent,
                   remaining, utilization_percent, status
            FROM department_budgets
            WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)
        \"\"\"
        params = []
        
        if department:
            query += \" AND department = %s\"
            params.append(department)
        
        query += \" ORDER BY department, month DESC\"
        return self.execute_query(query, tuple(params))
    
    def get_financial_transactions(self, department: Optional[str] = None, days: int = 30) -> List[Dict]:
        """Get recent financial transactions\"\"\"
        query = \"\"\"\n            SELECT transaction_id, department, account_id, transaction_type, amount,
                   category, description, transaction_date, approved_by
            FROM financial_transactions
            WHERE transaction_date > CURRENT_DATE - INTERVAL '%s days'
        \"\"\"\n        params = [days]
        
        if department:
            query += \" AND department = %s\"
            params.append(department)
        
        query += \" ORDER BY transaction_date DESC LIMIT 100\"
        return self.execute_query(query, tuple(params))
    
    def get_grants(self, department: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        \"\"\"Get grant information\"\"\"
        query = \"\"\"\n            SELECT grant_id, grant_name, provider, department, amount_awarded,
                   amount_received, start_date, end_date, status, terms
            FROM grants
            WHERE 1=1
        \"\"\"
        params = []
        
        if department:
            query += \" AND department = %s\"
            params.append(department)
        
        if status:
            query += \" AND status = %s\"
            params.append(status)
        
        query += \" ORDER BY start_date DESC\"
        return self.execute_query(query, tuple(params))
    
    def get_revenue_forecasts(self, department: Optional[str] = None) -> List[Dict]:
        \"\"\"Get revenue forecasts\"\"\"
        query = \"\"\"\n            SELECT forecast_id, department, period_start, period_end, forecast_amount,
                   method, confidence, model_metadata
            FROM revenue_forecasts
            WHERE period_start >= CURRENT_DATE
        \"\"\"
        params = []
        
        if department:
            query += \" AND department = %s\"
            params.append(department)
        
        query += \" ORDER BY period_start\"
        return self.execute_query(query, tuple(params))
    
    def get_finance_accounts(self, department: Optional[str] = None) -> List[Dict]:
        \"\"\"Get finance account balances\"\"\"
        query = \"\"\"\n            SELECT account_id, department, account_name, account_type, currency,
                   balance, reserved_amount, metadata
            FROM finance_accounts
            WHERE 1=1
        \"\"\"
        params = []
        
        if department:
            query += \" AND department = %s\"
            params.append(department)
        
        query += \" ORDER BY department, account_name\"
        return self.execute_query(query, tuple(params))
    
    def get_tax_revenues(self, days: int = 90) -> List[Dict]:
        \"\"\"Get tax revenue data\"\"\"
        query = \"\"\"\n            SELECT revenue_id, tax_type, amount, collection_date, jurisdiction, metadata
            FROM tax_revenues
            WHERE collection_date > CURRENT_DATE - INTERVAL '%s days'
            ORDER BY collection_date DESC
        \"\"\"
        return self.execute_query(query, (days,))
    
    def get_reserve_funds(self) -> List[Dict]:
        \"\"\"Get reserve fund status\"\"\"
        query = \"\"\"\n            SELECT reserve_id, fund_name, fund_type, balance, minimum_required,
                   last_contribution, purpose, status
            FROM reserve_funds
            ORDER BY fund_name
        \"\"\"
        return self.execute_query(query)


# Factory for queries (for patching in tests)
def get_finance_queries():
    return FinanceDepartmentDatabase()

