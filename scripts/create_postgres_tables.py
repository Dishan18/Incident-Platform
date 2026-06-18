"""Phase 2: Generate PostgreSQL schema and verify created tables."""

from sqlalchemy import inspect
from backend.database.db import engine
from backend.database.models import Base


def main():
    print(f"Creating tables on active database engine: {engine.url.drivername} at {engine.url.host}...")
    
    # Generate schema
    Base.metadata.create_all(engine)
    print("Base.metadata.create_all executed successfully.")

    # Inspect created tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\nVerified Tables in the Database:")
    for table in tables:
        print(f"- {table}")
        
    if "live_incidents" in tables:
        print("\nSuccess: Table 'live_incidents' successfully created/verified on PostgreSQL.")
    else:
        raise ValueError("Error: Table 'live_incidents' was not found after schema creation.")


if __name__ == "__main__":
    main()
