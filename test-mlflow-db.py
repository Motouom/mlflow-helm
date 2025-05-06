#!/usr/bin/env python3
"""
Test script to verify MLflow's connection to PostgreSQL.
This creates a simple experiment and logs a metric to test that the database is working.
"""

import os
import sys
import mlflow
import argparse
from urllib.parse import urlparse
import psycopg2

def test_postgres_connection(host, port, database, username, password):
    """Test direct connection to PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ PostgreSQL connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        return False

def test_mlflow_tracking(tracking_uri):
    """Test MLflow tracking with the database."""
    try:
        # Set tracking URI
        mlflow.set_tracking_uri(tracking_uri)
        
        # Print the current tracking URI
        print(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")
        
        # Create a new experiment
        experiment_name = "db-test-experiment"
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"Created new experiment: {experiment_name} (ID: {experiment_id})")
        else:
            experiment_id = experiment.experiment_id
            print(f"Using existing experiment: {experiment_name} (ID: {experiment_id})")
        
        # Log a metric to test the database connection
        with mlflow.start_run(experiment_id=experiment_id):
            mlflow.log_metric("test_metric", 1.0)
            run_id = mlflow.active_run().info.run_id
            print(f"✅ Successfully logged metric to run {run_id}")
        
        return True
    except Exception as e:
        print(f"❌ Error with MLflow tracking: {e}")
        return False

def parse_tracking_uri(tracking_uri):
    """Parse tracking URI to extract database connection details."""
    parsed = urlparse(tracking_uri)
    
    if parsed.scheme != 'postgresql':
        raise ValueError(f"Tracking URI scheme must be postgresql, got {parsed.scheme}")
    
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5443,
        'database': parsed.path.lstrip('/'),
        'username': parsed.username,
        'password': parsed.password
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test MLflow PostgreSQL connection")
    parser.add_argument("--tracking-uri", required=True, 
                        help="MLflow tracking URI (e.g., postgresql://username:password@host:port/database)")
    
    args = parser.parse_args()
    tracking_uri = args.tracking_uri
    
    # Parse the tracking URI
    try:
        db_params = parse_tracking_uri(tracking_uri)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Test direct PostgreSQL connection
    print("Testing direct PostgreSQL connection...")
    postgres_success = test_postgres_connection(
        db_params['host'],
        db_params['port'],
        db_params['database'],
        db_params['username'],
        db_params['password']
    )
    
    # Test MLflow tracking
    if postgres_success:
        print("\nTesting MLflow tracking with PostgreSQL...")
        mlflow_success = test_mlflow_tracking(tracking_uri)
        
        if mlflow_success:
            print("\n✅ All tests passed! MLflow is properly configured with PostgreSQL.")
        else:
            print("\n❌ MLflow tracking test failed.")
            sys.exit(1)
    else:
        print("\n❌ PostgreSQL connection test failed. Cannot proceed with MLflow test.")
        sys.exit(1)
