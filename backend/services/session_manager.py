import uuid

from backend.services.lead_manager import lead_manager


class SessionManager:

    def __init__(self):

        self.sessions = {}

    def create_session(self):

        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {

            "lead": lead_manager.create_lead(),

            "conversation": [],

            "intent": "general",

            # Package recommendation state
            "package_recommendation_status": "idle",
            "package_recommendation": "",
            "package_recommendation_error": ""
        }

        return session_id

    def get(self, session_id):

        return self.sessions.get(session_id)

    def add_message(

        self,

        session_id,

        role,

        message

    ):

        session = self.get(session_id)

        if session is None:

            return

        session["conversation"].append(

            {

                "role": role,

                "message": message
            }

        )

    def clear(self, session_id):

        if session_id in self.sessions:

            del self.sessions[session_id]


session_manager = SessionManager()