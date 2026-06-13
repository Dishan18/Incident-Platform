from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import DateTime

class Base(DeclarativeBase):
    pass


class Incident(Base):

    __tablename__ = "live_incidents"

    incident_id = Column(
        String,
        primary_key=True
    )

    description = Column(String)

    application = Column(String)

    affected_users = Column(Integer)

    impact_scope = Column(String)

    environment = Column(String)

    category = Column(String)

    ai_predicted_team = Column(String)

    ai_predicted_priority = Column(String)

    ai_predicted_resolution_time = Column(Float)

    assigned_team = Column(String)

    priority = Column(String)

    root_cause = Column(String)

    status = Column(String)

    team_overridden = Column(Boolean)

    priority_overridden = Column(Boolean)

    actual_resolution_time = Column(Integer)

    created_at = Column(DateTime)

    assigned_at = Column(DateTime)

    in_progress_at = Column(DateTime)

    resolved_at = Column(DateTime)

    closed_at = Column(DateTime)