# from backend.services.gemini_service import gemini_service
# from backend.services.session_manager import session_manager


# def handle_language(session_id, lead, user_message):

#     if lead.preferred_language != "":
#         return None

#     lead.preferred_language = user_message.strip()
#     lead.language = user_message.strip()

#     reply = gemini_service.chat(

#         question="""
# The customer selected their preferred language.

# Reply ONLY in that language.

# Greet the customer warmly.

# Ask:

# Which country are you contacting us from?

# Do not ask any other question.
# """,

#         context="",
#         conversation_history="",
#         lead_language=lead.preferred_language
#     )

#     session_manager.add_message(
#         session_id,
#         "assistant",
#         reply
#     )

#     return reply