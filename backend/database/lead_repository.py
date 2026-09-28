from backend.database.database import SessionLocal
from backend.models.lead_model import LeadModel


class LeadRepository:

    def save(self, lead):

        print("========== SAVE CALLED ==========")

        db = SessionLocal()

        try:

            new_lead = LeadModel(

                name=lead.name,
                country=lead.country,
                language=lead.language,

                phone=lead.phone,
                email=lead.email,

                destination=lead.destination,
                travel_date=lead.travel_date,
                travellers=lead.travellers,
                traveller_type=lead.traveller_type,
                children_travelling=lead.children_travelling,
                budget=lead.budget,

                visa_required=lead.visa_required,
                special_requests=lead.special_requests,

                status=lead.status
            )

            db.add(new_lead)
            db.commit()
            db.refresh(new_lead)

            print("Lead saved with ID:", new_lead.id)

            return new_lead.id

        except Exception as e:
            db.rollback()
            print("DATABASE ERROR:", e)
            raise

        finally:
            db.close()


lead_repository = LeadRepository()