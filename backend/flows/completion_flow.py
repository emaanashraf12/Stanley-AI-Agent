from backend.services.lead_manager import lead_manager
from backend.services.booking_manager import booking_manager
from backend.database.lead_repository import lead_repository
from backend.services.email_service import email_service
from backend.services.session_manager import session_manager


class CompleteBooking:

    def can_complete(self, lead):

        return lead.special_requests == ""

    def process(self, session_id, lead, user_message):

        lead.special_requests = user_message

        lead_manager.complete_booking(lead)

        lead_repository.save(lead)

        email_service.send_lead(lead)

        reply = booking_manager.final_message(lead)

        session_manager.add_message(

            session_id,

            "assistant",

            reply
        )

        return reply


complete_booking = CompleteBooking()