import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Old SQLite connection format preserved for rollback/fallback:
# DATABASE_URL = "sqlite:///incident.db"
# engine = create_engine(DATABASE_URL, echo=False)

db_type = os.getenv("DATABASE_TYPE", "postgres").lower()

if db_type == "postgres":
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=5432,
        database=os.getenv("POSTGRES_DB"),
    )
    engine = create_engine(
        url,
        connect_args={"sslmode": "require"},
        future=True
    )
else:
    engine = create_engine(
        "sqlite:///incident.db",
        echo=False
    )

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)