#!/usr/bin/env python3
"""
Database Test Data Loader

Automatically loads schema and test data into PostgreSQL database.
Reads database configuration from .env file.

Usage:
    python migrations/load_test_data.py
    python migrations/load_test_data.py --schema-only
    python migrations/load_test_data.py --data-only
    python migrations/load_test_data.py --reset
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Database configuration from .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "departments")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Migration file paths
MIGRATIONS_DIR = Path(__file__).parent
SCHEMA_FILE = MIGRATIONS_DIR / "complete_schema.sql"
SEED_FILE = MIGRATIONS_DIR / "seed_test_data.sql"


def run_psql(sql_file, database=DB_NAME):
    """Execute SQL file using psql command"""
    
    print(f"\n{'='*60}")
    print(f"Executing: {sql_file.name}")
    print(f"Database: {database}")
    print(f"{'='*60}\n")
    
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD
    
    cmd = [
        "psql",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", database,
        "-f", str(sql_file)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(result.stdout)
        
        if result.stderr and not result.stderr.strip().startswith("NOTICE"):
            print("Warnings/Notices:")
            print(result.stderr)
        
        print(f"✅ Successfully executed {sql_file.name}\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing {sql_file.name}:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ Error: psql command not found!")
        print("Please ensure PostgreSQL is installed and psql is in your PATH")
        return False


def run_psql_command(command, database=DB_NAME):
    """Execute a single psql command"""
    
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD
    
    cmd = [
        "psql",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-d", database,
        "-c", command
    ]
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None


def check_database_exists():
    """Check if database exists"""
    
    result = run_psql_command(
        f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'",
        database="postgres"
    )
    
    return result is not None and "1" in result


def create_database():
    """Create database if it doesn't exist"""
    
    print(f"\n{'='*60}")
    print(f"Creating database: {DB_NAME}")
    print(f"{'='*60}\n")
    
    result = run_psql_command(
        f"CREATE DATABASE {DB_NAME}",
        database="postgres"
    )
    
    if result is not None:
        print(f"✅ Database '{DB_NAME}' created successfully\n")
        return True
    else:
        print(f"ℹ️  Database '{DB_NAME}' may already exist or creation failed\n")
        return True  # Continue anyway


def verify_data():
    """Verify that data was loaded correctly"""
    
    print(f"\n{'='*60}")
    print("Verifying data...")
    print(f"{'='*60}\n")
    
    tables = [
        "departments",
        "department_budgets",
        "workers",
        "reservoirs",
        "pipelines",
        "incidents",
        "projects",
        "work_schedules",
        "agent_decisions"
    ]
    
    all_good = True
    
    for table in tables:
        count = run_psql_command(f"SELECT COUNT(*) FROM {table}")
        if count:
            # Extract just the number
            count_value = count.split('\n')[2].strip() if len(count.split('\n')) > 2 else "?"
            print(f"  {table:.<30} {count_value:>5} records")
        else:
            print(f"  {table:.<30} ERROR")
            all_good = False
    
    print()
    
    if all_good:
        print("✅ All tables verified successfully!\n")
        print_edge_cases()
    else:
        print("⚠️  Some tables may have issues\n")
    
    return all_good


def print_edge_cases():
    """Print summary of edge cases in the data"""
    
    print(f"\n{'='*60}")
    print("Edge Cases Available for Testing:")
    print(f"{'='*60}\n")
    
    edge_cases = {
        "Depleted Budgets": "SELECT department, status FROM department_budgets WHERE status = 'depleted'",
        "Frozen Budgets": "SELECT department, status FROM department_budgets WHERE status = 'frozen'",
        "Critical Reservoirs": "SELECT name, status FROM reservoirs WHERE status = 'critical'",
        "Emergency Incidents": "SELECT incident_type, location FROM incidents WHERE severity = 'critical' AND status = 'open'",
        "Over-Budget Projects": "SELECT project_name FROM projects WHERE actual_cost > estimated_cost",
        "Unavailable Workers": "SELECT name, role FROM workers WHERE available = false"
    }
    
    for title, query in edge_cases.items():
        result = run_psql_command(query)
        if result:
            lines = result.strip().split('\n')
            # Skip header lines and get data rows
            data_rows = [line for line in lines[2:] if line.strip() and not line.startswith('(')]
            count = len(data_rows)
            print(f"  ✓ {title}: {count} cases")
        else:
            print(f"  ✗ {title}: Could not verify")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Load test data into City Governance database"
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Only create schema, skip test data"
    )
    parser.add_argument(
        "--data-only",
        action="store_true",
        help="Only load test data, skip schema creation"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate database before loading"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing data, don't load anything"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("CITY GOVERNANCE SYSTEM - DATABASE LOADER")
    print("="*60)
    print(f"\nTarget Database:")
    print(f"  Host:     {DB_HOST}:{DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User:     {DB_USER}")
    print()
    
    # Verify only mode
    if args.verify_only:
        if check_database_exists():
            verify_data()
        else:
            print(f"❌ Database '{DB_NAME}' does not exist")
        return
    
    # Reset mode - drop and recreate database
    if args.reset:
        print("⚠️  RESET MODE: Dropping and recreating database...\n")
        
        run_psql_command(f"DROP DATABASE IF EXISTS {DB_NAME}", database="postgres")
        print(f"  Dropped database '{DB_NAME}'")
        
        create_database()
    
    # Check/create database
    if not check_database_exists():
        print(f"ℹ️  Database '{DB_NAME}' does not exist. Creating...\n")
        create_database()
    else:
        print(f"✅ Database '{DB_NAME}' exists\n")
    
    # Load schema
    if not args.data_only:
        if not SCHEMA_FILE.exists():
            print(f"❌ Schema file not found: {SCHEMA_FILE}")
            sys.exit(1)
        
        if not run_psql(SCHEMA_FILE):
            print("❌ Failed to load schema")
            sys.exit(1)
    
    # Load test data
    if not args.schema_only:
        if not SEED_FILE.exists():
            print(f"❌ Seed data file not found: {SEED_FILE}")
            sys.exit(1)
        
        if not run_psql(SEED_FILE):
            print("❌ Failed to load test data")
            sys.exit(1)
    
    # Verify data was loaded
    if not args.schema_only:
        verify_data()
    
    print("="*60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*60)
    print("\nYou can now:")
    print("  1. Start the backend: python start_backend.py")
    print("  2. Test agents with edge cases from the loaded data")
    print("  3. Run tests: pytest tests/")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
