from dataclasses import dataclass, asdict


@dataclass
class Lead:

    # Customer information

    preferred_language: str = ""

    country: str = ""

    name: str = ""

    language: str = "English"

    # Contact details

    phone: str = ""

    phone_verified: bool = False
    
    email: str = ""

    # Booking details

    destination: str = ""

    travel_date: str = ""

    travellers: str = ""

    traveller_type: str = ""

    children_travelling: str = ""

    budget: str = ""

    visa_required: str = ""

    special_requests: str = ""

    # Status

    booking_started: bool = False

    booking_completed: bool = False

    conversation_mode: str = "booking"

    status: str = "Pending"


class LeadManager:

    def create_lead(self):

        return Lead()

    def to_dict(self, lead: Lead):

        return asdict(lead)

    def start_booking(self, lead: Lead):

        lead.booking_started = True
        lead.booking_completed = False

        lead.phone_verified = False

    def complete_booking(self, lead: Lead):

        lead.booking_started = False
        lead.booking_completed = True
        lead.status = "Completed"

    def reset_booking(self, lead: Lead):

        lead.preferred_language = ""

        lead.country = ""

        lead.name = ""

        lead.language = "English"

        lead.phone = ""
        
        lead.phone_verified = False

        lead.email = ""

        lead.destination = ""

        lead.travel_date = ""

        lead.travellers = ""

        lead.traveller_type = ""

        lead.children_travelling = ""

        lead.budget = ""

        lead.visa_required = ""

        lead.special_requests = ""

        lead.booking_started = False

        lead.booking_completed = False

        lead.status = "Pending"


lead_manager = LeadManager()