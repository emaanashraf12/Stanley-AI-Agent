from backend.services.session_manager import session_manager
from backend.services.intent_detector import intent_detector
from backend.services.lead_manager import lead_manager

from backend.flows.language_flow import handle_language
from backend.flows.booking_flow import handle_booking
from backend.flows.package_flow import handle_package
from backend.flows.general_flow import handle_general
from backend.flows.completion_flow import complete_booking


class ConversationEngine:

    def process(

        self,

        session_id,

        user_message

    ):

        session = session_manager.get(session_id)

        if session is None:
            return "Invalid session."

        lead = session["lead"]

        session_manager.add_message(

            session_id,

            "user",

            user_message
        )

        session["intent"] = intent_detector.detect(

            user_message
        )

        greetings = [

            "hi",

            "hello",

            "hey",

            "good morning",

            "good afternoon",

            "good evening"
        ]

        lower = user_message.lower().strip()

        if (

            any(

                lower.startswith(g)

                for g in greetings

            )

            and not lead.booking_started

        ):

            lead_manager.start_booking(

                lead
            )

            reply = (

                "Hello!\n\n"

                "Welcome to Stanley Tours.\n\n"

                "What is your preferred language?"
            )

            session_manager.add_message(

                session_id,

                "assistant",

                reply
            )

            return reply

        if (

            lead.booking_started

            and lead.preferred_language == ""

        ):

            return handle_language(

                session_id,

                lead,

                user_message
            )

        if handle_package.can_handle(lead):

            return handle_package.process(

                session_id,

                lead,

                user_message
            )
            
        print("INTENT =", session["intent"])
        print("BOOKING STARTED =", lead.booking_started)
        
        if handle_booking.can_handle(lead):

            return handle_booking.process(

                session_id,

                lead,

                user_message
            )

        if complete_booking.can_complete(lead):

            return complete_booking.process(

                session_id,

                lead,

                user_message
            )

        return handle_general(

            session_id,

            lead,

            user_message
        )


conversation_engine = ConversationEngine()