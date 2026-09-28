from backend.rag.retriever import retriever
from backend.services.gemini_service import gemini_service
from backend.services.session_manager import session_manager


def handle_general(session_id, lead, user_message):

    query = user_message

    if lead.booking_started:

        query += f"""

        Destination: {lead.destination}

        Traveller type: {lead.traveller_type}

        Number of travellers: {lead.travellers}
        """

    context = ""

    try:

        results = retriever.retrieve(query)

        if (

            results
            and "documents" in results
            and results["documents"]
            and len(results["documents"][0]) > 0

        ):

            context = "\n\n".join(

                results["documents"][0]
            )

    except Exception as e:

        print("RAG ERROR:", e)
        context = ""

    session = session_manager.get(session_id)
    
    answer = gemini_service.chat(

        question=user_message,

        context=context,

        conversation_history=session["conversation"],

        lead_language=lead.language
    )
    
    lead.conversation_mode = "general"

    session_manager.add_message(

        session_id,

        "assistant",

        answer
    )

    return answer