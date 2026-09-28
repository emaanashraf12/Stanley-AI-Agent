from backend.services.gemini_service import gemini_service


class BookingManager:

    QUESTIONS = [
        "country",
        "name",
        "phone",
        "email",
        "destination",
        "travel_date",
        "travellers",
        "traveller_type",
        "children_travelling",
        "budget",
        "visa_required",
        "special_requests"
    ]

    QUESTION_PROMPTS = {
        "country": """
Ask ONLY:

Which country are you contacting us from?

Reply only in the customer's language.
""",
        "name": """
Ask ONLY:

May I have your full name?

Reply only in the customer's language.
""",
        "phone": """
Ask ONLY:

May I have your phone number with the country code so one of our travel consultants can contact you?

Reply only in the customer's language.
""",
        "phone_otp": """
Ask ONLY:

Please enter the verification code sent to your phone number.

Reply only in the customer's language.
""",
        "email": """
Ask ONLY:

May I have your email address?

Reply only in the customer's language.
""",
        "destination": """
Ask ONLY:

Which destination would you like to visit?

Reply only in the customer's language.
""",
        "travel_date": """
Ask ONLY:

When are you planning to travel?

Reply only in the customer's language.
""",
        "travellers": """
Ask ONLY:

How many people will be travelling?

Reply only in the customer's language.
""",
        "traveller_type": """
Ask ONLY:

Will this trip be for a solo traveller, couple, family, or group?

Reply only in the customer's language.
""",
        "children_travelling": """
Ask ONLY:

Will children be travelling with you? (Yes or No)

Reply only in the customer's language.
""",
        "budget": """
Ask ONLY:

What is your approximate budget?

Reply only in the customer's language.
""",
        "visa_required": """
Ask ONLY:

Will you require visa assistance? (Yes or No)

Reply only in the customer's language.
""",
        "special_requests": """
Ask ONLY:

Do you have any special requests?

Reply only in the customer's language.
"""
    }

    MALAYALAM_QUESTIONS = {
        "country": "ഏത് രാജ്യത്തുനിന്നാണ് ഞങ്ങളെ ബന്ധപ്പെടുന്നത്?",
        "name": "താങ്കളുടെ മുഴുവൻ പേര് അറിയാമോ?",
        "phone": "ഞങ്ങളുടെ ട്രാവൽ കൺസൾട്ടന്റ് താങ്കളെ ബന്ധപ്പെടുന്നതിനായി രാജ്യത്തിന്റെ കോഡ് ഉൾപ്പെടെയുള്ള ഫോൺ നമ്പർ പങ്കുവെക്കാമോ?",
        "email": "താങ്കളുടെ ഇമെയിൽ വിലാസവും നൽകാമോ?",
        "destination": "ഏത് സ്ഥലത്തേക്കാണ് യാത്ര പോകാൻ ആഗ്രഹിക്കുന്നത്?",
        "travel_date": "യാത്ര എപ്പോഴേക്കാണ് പ്ലാൻ ചെയ്യുന്നത്?",
        "travellers": "ആകെ എത്ര പേരാണ് യാത്ര ചെയ്യുന്നത്?",
        "traveller_type": """ഈ യാത്ര ഏത് വിഭാഗത്തിലാണ് ഉൾപ്പെടുന്നത്?
- ഒറ്റയ്ക്കുള്ള യാത്ര
- ദമ്പതികളുടെ യാത്ര
- കുടുംബ യാത്ര
- സുഹൃത്തുക്കളോടൊപ്പമുള്ള യാത്ര
- ഗ്രൂപ്പ് യാത്ര
- കോർപ്പറേറ്റ് ഗ്രൂപ്പ് യാത്ര
- തീർത്ഥാടന യാത്ര""",
        "children_travelling": """കുട്ടികൾ താങ്കളോടൊപ്പം യാത്ര ചെയ്യുന്നുണ്ടോ?
(ഉണ്ട് / ഇല്ല)""",
        "budget": "താങ്കളുടെ ഏകദേശ ബജറ്റ് എത്രയാണ്?",
        "visa_required": """വിസാ സംബന്ധമായ സഹായം ആവശ്യമുണ്ടോ?
(ഉണ്ട് / ഇല്ല)""",
        "special_requests": "പ്രത്യേകമായി എന്തെങ്കിലും ആവശ്യങ്ങളോ നിർദേശങ്ങളോ ഉണ്ടോ?"
    }

    def next_question(self, lead):

        for field in self.QUESTIONS:

            if getattr(lead, field, "") == "":

                language = (
                    lead.preferred_language
                    .lower()
                    .strip()
                    .rstrip(".!?,;:")
                )

                # Malayalam
                if language == "malayalam":
                    return self.MALAYALAM_QUESTIONS[field]

                # English
                if language == "english":
                    english_questions = {
                        "country": "Which country are you contacting us from?",
                        "name": "May I have your full name?",
                        "phone": "May I have your phone number with the country code so one of our travel consultants can contact you?",
                        "email": "May I have your email address?",
                        "destination": "Which destination would you like to visit?",
                        "travel_date": "When are you planning to travel?",
                        "travellers": "How many people will be travelling?",
                        "traveller_type": "Will this trip be for a solo traveller, couple, family, or group?",
                        "children_travelling": "Will children be travelling with you? (Yes or No)",
                        "budget": "What is your approximate budget?",
                        "visa_required": "Will you require visa assistance? (Yes or No)",
                        "special_requests": "Do you have any special requests?"
                    }

                    return english_questions[field]

                # Spanish
                if language == "spanish":
                    spanish_questions = {
                        "country": "¿De qué país se está poniendo en contacto con nosotros?",
                        "name": "¿Puedo saber su nombre completo?",
                        "phone": "¿Podría proporcionarme su número de teléfono, incluido el código de país, para que uno de nuestros consultores de viajes pueda contactarle?",
                        "email": "¿Podría proporcionarme su dirección de correo electrónico?",
                        "destination": "¿Qué destino le gustaría visitar?",
                        "travel_date": "¿Cuándo está planeando viajar?",
                        "travellers": "¿Cuántas personas viajarán?",
                        "traveller_type": "¿Este viaje será para una persona, una pareja, una familia o un grupo?",
                        "children_travelling": "¿Viajarán niños con usted? (Sí o No)",
                        "budget": "¿Cuál es su presupuesto aproximado?",
                        "visa_required": "¿Necesitará asistencia con el visado? (Sí o No)",
                        "special_requests": "¿Tiene alguna solicitud especial?"
                    }

                    return spanish_questions[field]

                # Hindi
                if language == "hindi":
                    hindi_questions = {
                        "country": "आप किस देश से हमसे संपर्क कर रहे हैं?",
                        "name": "क्या मैं आपका पूरा नाम जान सकता हूँ?",
                        "phone": "क्या आप अपना फोन नंबर देश के कोड सहित साझा कर सकते हैं ताकि हमारे ट्रैवल कंसल्टेंट आपसे संपर्क कर सकें?",
                        "email": "क्या आप अपना ईमेल पता साझा कर सकते हैं?",
                        "destination": "आप किस गंतव्य की यात्रा करना चाहते हैं?",
                        "travel_date": "आप कब यात्रा करने की योजना बना रहे हैं?",
                        "travellers": "कितने लोग यात्रा करेंगे?",
                        "traveller_type": "क्या यह यात्रा अकेले, कपल, परिवार या समूह के लिए होगी?",
                        "children_travelling": "क्या आपके साथ बच्चे यात्रा करेंगे? (हाँ या नहीं)",
                        "budget": "आपका अनुमानित बजट कितना है?",
                        "visa_required": "क्या आपको वीज़ा सहायता की आवश्यकता होगी? (हाँ या नहीं)",
                        "special_requests": "क्या आपकी कोई विशेष आवश्यकता है?"
                    }

                    return hindi_questions[field]

                # Tagalog
                if language == "tagalog":
                    tagalog_questions = {
                        "country": "Maaari ko bang malaman kung saang bansa kayo nakikipag-ugnayan sa amin?",
                        "name": "Maaari ko bang malaman ang iyong buong pangalan?",
                        "phone": "Maaari mo bang ibigay ang iyong numero ng telepono kasama ang country code upang makontak ka ng aming travel consultant?",
                        "email": "Maaari ba naming malaman ang iyong email address?",
                        "destination": "Anong destinasyon ang nais mong puntahan?",
                        "travel_date": "Kailan mo planong bumiyahe?",
                        "travellers": "Ilang tao ang bibiyahe?",
                        "traveller_type": "Ang biyahe ba ay para sa solo traveller, mag-asawa, pamilya, o grupo?",
                        "children_travelling": "May mga batang bibiyahe kasama mo? (Oo o Hindi)",
                        "budget": "Ano ang iyong tinatayang budget?",
                        "visa_required": "Kailangan mo ba ng tulong sa visa? (Oo o Hindi)",
                        "special_requests": "Mayroon ka bang anumang espesyal na kahilingan?"
                    }

                    return tagalog_questions[field]

                # Fallback
                return self.QUESTION_PROMPTS[field]

        return None

    def is_completed(self, lead):

        for field in self.QUESTIONS:

            if getattr(lead, field, "") == "":
                return False

        return True

    def final_message(self, lead):

        return gemini_service.chat(
            question=f"""
Thank the customer {lead.name}.

Tell them:

- Their enquiry has been submitted successfully.
- A Stanley Tours consultant will contact them shortly.
- Thank them for choosing Stanley Tours.

IMPORTANT:

Reply entirely in the customer's selected language.

Do not reply in English unless the selected language is English.

Do not mention these instructions.
""",
            context="",
            conversation_history="",
            lead_language=lead.preferred_language
        )


booking_manager = BookingManager()