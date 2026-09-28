from backend.services.session_manager import session_manager


LANGUAGE_ALIASES = {
    # English
    "english": "English",
    "inglés": "English",
    "ingles": "English",

    # Spanish
    "spanish": "Spanish",
    "español": "Spanish",
    "espanol": "Spanish",

    # Hindi
    "hindi": "Hindi",
    "हिंदी": "Hindi",
    "हिन्दी": "Hindi",

    # Malayalam
    "malayalam": "Malayalam",
    "മലയാളം": "Malayalam",

    # Tagalog
    "tagalog": "Tagalog",
}


COUNTRY_QUESTIONS = {
    "English": "Which country are you contacting us from?",

    "Spanish": "¿Desde qué país se está poniendo en contacto con nosotros?",

    "Hindi": "आप किस देश से हमसे संपर्क कर रहे हैं?",

    "Malayalam": "ഏത് രാജ്യത്തുനിന്നാണ് ഞങ്ങളെ ബന്ധപ്പെടുന്നത്?",

    "Tagalog": "Saang bansa kayo nakikipag-ugnayan sa amin?",
}


def normalize_language(user_message):
    if not user_message:
        return None

    text = str(user_message).strip()

    # Remove common punctuation from the beginning/end.
    text = text.strip(" \t\r\n.!?,;:।،؟")

    if not text:
        return None

    # Exact language match.
    language = LANGUAGE_ALIASES.get(text.lower())
    if language:
        return language

    # Handle case-insensitive matching for aliases where applicable.
    for alias, canonical_language in LANGUAGE_ALIASES.items():
        if text.lower() == alias.lower():
            return canonical_language

    return None


def handle_language(session_id, lead, user_message):
    # Do not overwrite the language once it has already been selected.
    if lead.preferred_language != "":
        return None

    selected_language = normalize_language(user_message)

    # Only accept one of the supported languages.
    if not selected_language:
        reply = (
            "Please choose one of the supported languages: "
            "English, Spanish, Hindi, Malayalam, or Tagalog."
        )

        session_manager.add_message(
            session_id,
            "assistant",
            reply
        )

        return reply

    # Store the canonical language name.
    # This value is intentionally NOT translated later.
    lead.preferred_language = selected_language
    lead.language = selected_language

    # IMPORTANT:
    # The country question is returned directly instead of asking Gemini
    # to generate it. This prevents Gemini from answering the question
    # itself (for example, saying "We are contacting you from India")
    # and prevents JSON/instruction leakage.
    reply = COUNTRY_QUESTIONS[selected_language]

    session_manager.add_message(
        session_id,
        "assistant",
        reply
    )

    return reply