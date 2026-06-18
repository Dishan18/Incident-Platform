"""Phase 4: Migrate incident data from SQLite to Azure PostgreSQL using SQLAlchemy models."""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from backend.database.models import Incident

load_dotenv()


def main():
    print("Setting up database connections...")

    # 1. SQLite Connection
    sqlite_engine = create_engine("sqlite:///incident.db", echo=False)
    SQLiteSession = sessionmaker(bind=sqlite_engine, autoflush=False, autocommit=False)
    sqlite_session = SQLiteSession()

    # 2. PostgreSQL Connection
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=5432,
        database=os.getenv("POSTGRES_DB"),
    )
    postgres_engine = create_engine(url, connect_args={"sslmode": "require"}, future=True, echo=False)
    PostgresSession = sessionmaker(bind=postgres_engine, autoflush=False, autocommit=False)
    postgres_session = PostgresSession()

    print(f"SQLite URL: {sqlite_engine.url}")
    print(f"PostgreSQL URL: {postgres_engine.url}")

    print("Fetching records from SQLite...")
    sqlite_incidents = sqlite_session.query(Incident).order_by(Incident.created_at.asc()).all()
    records_read = len(sqlite_incidents)
    print(f"Read {records_read} records from SQLite.")

    records_inserted = 0
    records_skipped = 0
    errors = 0

    # Get list of columns dynamically
    columns = [c.key for c in Incident.__table__.columns]

    print("Migrating records to PostgreSQL...")
    for inc in sqlite_incidents:
        # Check if record already exists in Postgres
        existing = postgres_session.query(Incident).filter(Incident.incident_id == inc.incident_id).first()
        if existing:
            records_skipped += 1
            continue

        try:
            # Create a clean, transient copy of the Incident model instance
            new_inc = Incident()
            for col in columns:
                val = getattr(inc, col)
                setattr(new_inc, col, val)

            # Insert record into PostgreSQL session
            postgres_session.add(new_inc)
            postgres_session.commit()
            records_inserted += 1
        except Exception as e:
            postgres_session.rollback()
            print(f"Error migrating incident {inc.incident_id}: {e}")
            errors += 1

    print("\n--- Migration Statistics ---")
    print(f"Records read:     {records_read}")
    print(f"Records inserted: {records_inserted}")
    print(f"Records skipped:  {records_skipped}")
    print(f"Errors:           {errors}")

    print("\n--- Integrity Validation ---")
    sqlite_count = sqlite_session.query(Incident).count()
    postgres_count = postgres_session.query(Incident).count()
    
    print(f"SQLite Count:     {sqlite_count}")
    print(f"PostgreSQL Count: {postgres_count}")
    
    # Assert counts match
    assert sqlite_count == postgres_count, (
        f"Validation Error: Count mismatch! SQLite={sqlite_count}, Postgres={postgres_count}"
    )
    print("[OK] Row counts match perfectly.")

    # Fetch first/last records to verify ordering and IDs
    sqlite_first = sqlite_session.query(Incident).order_by(Incident.created_at.asc()).first()
    sqlite_last = sqlite_session.query(Incident).order_by(Incident.created_at.desc()).first()

    postgres_first = postgres_session.query(Incident).order_by(Incident.created_at.asc()).first()
    postgres_last = postgres_session.query(Incident).order_by(Incident.created_at.desc()).first()

    if sqlite_first and postgres_first:
        print(f"SQLite First ID:  {sqlite_first.incident_id}")
        print(f"Postgres First ID: {postgres_first.incident_id}")
        assert sqlite_first.incident_id == postgres_first.incident_id, "Validation Error: First incident ID mismatch!"
        print("[OK] First incident IDs match.")

    if sqlite_last and postgres_last:
        print(f"SQLite Last ID:   {sqlite_last.incident_id}")
        print(f"Postgres Last ID:  {postgres_last.incident_id}")
        assert sqlite_last.incident_id == postgres_last.incident_id, "Validation Error: Last incident ID mismatch!"
        print("[OK] Last incident IDs match.")

    print("\nMigration completed and verified successfully!")

    sqlite_session.close()
    postgres_session.close()


if __name__ == "__main__":
    main()
