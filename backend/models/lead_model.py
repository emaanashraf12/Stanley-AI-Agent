from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from datetime import datetime

from backend.database.database import Base


class LeadModel(Base):

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    country = Column(String)
    language = Column(String)

    phone = Column(String)
    email = Column(String)

    destination = Column(String)
    travel_date = Column(String)
    travellers = Column(String)
    traveller_type = Column(String)
    children_travelling = Column(String)
    budget = Column(String)

    visa_required = Column(String)
    special_requests = Column(String)

    status = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)