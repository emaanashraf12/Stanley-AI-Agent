from backend.database.database import Base, engine

# Import all models here
from backend.models.lead_model import LeadModel


def init_db():
    Base.metadata.create_all(bind=engine)