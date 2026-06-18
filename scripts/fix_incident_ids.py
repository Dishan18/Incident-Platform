"""One-off script to correct incident IDs and rename the associated Azure Blob PDF."""

import os
import sqlite3
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from backend.cloud.azure_blob import get_container_client

load_dotenv()


def main():
    print("Starting data correction script...")

    # 1. Rename Azure Blob resource if it exists
    container_name = "rca-files"
    old_blob_name = "INC-2026-01000-RCA-2026-06-18.pdf"
    new_blob_name = "INC-2026-00011-RCA-2026-06-18.pdf"

    print("Checking Azure Blob Storage for PDF file...")
    try:
        container_client = get_container_client(container_name)
        old_blob_client = container_client.get_blob_client(old_blob_name)
        new_blob_client = container_client.get_blob_client(new_blob_name)

        if old_blob_client.exists():
            print(f"Renaming cloud PDF blob '{old_blob_name}' to '{new_blob_name}'...")
            new_blob_client.start_copy_from_url(old_blob_client.url)
            old_blob_client.delete_blob()
            print("Successfully renamed blob in Azure Storage.")
        else:
            print("Blob 'INC-2026-01000-RCA-2026-06-18.pdf' does not exist in Azure Blob Storage. Skipping cloud rename.")
    except Exception as e:
        print(f"Warning: Cloud renaming failed or skipped: {e}")

    # 2. SQLite Update
    print("Updating SQLite database 'incident.db'...")
    try:
        sqlite_path = "incident.db"
        if os.path.exists(sqlite_path):
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()

            # Update INC-2026-01000
            cursor.execute(
                "UPDATE live_incidents SET incident_id = 'INC-2026-00011', rca_pdf_url = 'INC-2026-00011-RCA-2026-06-18.pdf' "
                "WHERE incident_id = 'INC-2026-01000'"
            )
            # Update INC-2026-01001
            cursor.execute(
                "UPDATE live_incidents SET incident_id = 'INC-2026-00012' "
                "WHERE incident_id = 'INC-2026-01001'"
            )
            # Update INC-2026-01002
            cursor.execute(
                "UPDATE live_incidents SET incident_id = 'INC-2026-00013' "
                "WHERE incident_id = 'INC-2026-01002'"
            )

            conn.commit()
            conn.close()
            print("SQLite records updated successfully.")
        else:
            print("SQLite 'incident.db' not found. Skipping.")
    except Exception as e:
        print(f"Error updating SQLite: {e}")

    # 3. PostgreSQL Update
    print("Updating Azure PostgreSQL database...")
    try:
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=5432,
            database=os.getenv("POSTGRES_DB"),
        )
        postgres_engine = create_engine(url, connect_args={"sslmode": "require"}, future=True)

        with postgres_engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE live_incidents SET incident_id = 'INC-2026-00011', rca_pdf_url = 'INC-2026-00011-RCA-2026-06-18.pdf' "
                    "WHERE incident_id = 'INC-2026-01000'"
                )
            )
            conn.execute(
                text(
                    "UPDATE live_incidents SET incident_id = 'INC-2026-00012' "
                    "WHERE incident_id = 'INC-2026-01001'"
                )
            )
            conn.execute(
                text(
                    "UPDATE live_incidents SET incident_id = 'INC-2026-00013' "
                    "WHERE incident_id = 'INC-2026-01002'"
                )
            )

        print("PostgreSQL records updated successfully.")
    except Exception as e:
        print(f"Error updating PostgreSQL: {e}")

    print("Data correction complete!")


if __name__ == "__main__":
    main()
