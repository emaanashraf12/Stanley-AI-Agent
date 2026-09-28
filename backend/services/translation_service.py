import re

from google import genai
from google.genai import types

from backend.apps.config import settings


class TranslationService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = "gemini-3.6-flash"

    # ==========================================================
    # COUNTRY NORMALIZATION
    # ==========================================================

    COUNTRY_VALUES = {

        # Pakistan
        "pakistan": "Pakistan",
        "pk": "Pakistan",

        # India
        "india": "India",
        "in": "India",

        # United States
        "usa": "United States",
        "u.s.a": "United States",
        "u.s.a.": "United States",
        "us": "United States",
        "u.s": "United States",
        "u.s.": "United States",
        "united states": "United States",
        "united states of america": "United States",
        "america": "United States",

        # United Kingdom
        "uk": "United Kingdom",
        "u.k": "United Kingdom",
        "u.k.": "United Kingdom",
        "united kingdom": "United Kingdom",
        "great britain": "United Kingdom",
        "england": "United Kingdom",
        "scotland": "United Kingdom",
        "wales": "United Kingdom",

        # Philippines
        "philippines": "Philippines",
        "the philippines": "Philippines",
        "ph": "Philippines",

        # UAE
        "uae": "United Arab Emirates",
        "u.a.e": "United Arab Emirates",
        "u.a.e.": "United Arab Emirates",
        "united arab emirates": "United Arab Emirates",

        # Canada
        "canada": "Canada",
        "ca": "Canada",

        # Australia
        "australia": "Australia",
        "au": "Australia",

        # New Zealand
        "new zealand": "New Zealand",
        "nz": "New Zealand",

        # Bangladesh
        "bangladesh": "Bangladesh",
        "bd": "Bangladesh",

        # Sri Lanka
        "sri lanka": "Sri Lanka",
        "srilanka": "Sri Lanka",
        "lk": "Sri Lanka",

        # Nepal
        "nepal": "Nepal",
        "np": "Nepal",

        # Europe
        "france": "France",
        "germany": "Germany",
        "spain": "Spain",
        "italy": "Italy",
        "portugal": "Portugal",
        "netherlands": "Netherlands",
        "holland": "Netherlands",
        "belgium": "Belgium",
        "switzerland": "Switzerland",
        "austria": "Austria",
        "sweden": "Sweden",
        "norway": "Norway",
        "denmark": "Denmark",
        "finland": "Finland",
        "iceland": "Iceland",
        "poland": "Poland",
        "greece": "Greece",
        "romania": "Romania",
        "ukraine": "Ukraine",
        "turkey": "Turkey",

        # Middle East
        "saudi arabia": "Saudi Arabia",
        "saudi": "Saudi Arabia",
        "qatar": "Qatar",
        "kuwait": "Kuwait",
        "bahrain": "Bahrain",
        "oman": "Oman",
        "jordan": "Jordan",
        "israel": "Israel",
        "egypt": "Egypt",

        # Asia
        "singapore": "Singapore",
        "malaysia": "Malaysia",
        "indonesia": "Indonesia",
        "thailand": "Thailand",
        "vietnam": "Vietnam",
        "japan": "Japan",
        "south korea": "South Korea",
        "korea": "South Korea",
        "china": "China",
        "hong kong": "Hong Kong",
        "taiwan": "Taiwan",

        # Africa
        "south africa": "South Africa",
        "kenya": "Kenya",
        "nigeria": "Nigeria",
        "morocco": "Morocco",
        "ghana": "Ghana",
        "tanzania": "Tanzania",

        # Americas
        "mexico": "Mexico",
        "brazil": "Brazil",
        "argentina": "Argentina",
        "chile": "Chile",
        "colombia": "Colombia",
        "peru": "Peru",
        "cuba": "Cuba",
        "jamaica": "Jamaica",
        "dominican republic": "Dominican Republic",
        "costa rica": "Costa Rica"
    }

    # ==========================================================
    # MULTILINGUAL COUNTRY VALUES
    # ==========================================================

    MULTILINGUAL_COUNTRIES = {

        # Pakistan
        "پاکستان": "Pakistan",
        "पाकिस्तान": "Pakistan",
        "പാകിസ്ഥാൻ": "Pakistan",
        "പാക്കിസ്ഥാൻ": "Pakistan",

        # India
        "भारत": "India",
        "हिंदुस्तान": "India",
        "इंडिया": "India",
        "ഇന്ത്യ": "India",

        # United States
        "संयुक्त राज्य अमेरिका": "United States",
        "संयुक्त राज्य": "United States",
        "अमेरिका": "United States",
        "الولايات المتحدة": "United States",

        # United Kingdom
        "यूनाइटेड किंगडम": "United Kingdom",
        "इंग्लैंड": "United Kingdom",
        "المملكة المتحدة": "United Kingdom",

        # Philippines
        "फिलीपींस": "Philippines",
        "फिलिपींस": "Philippines",
        "फिलिपिन्स": "Philippines",
        "Pilipinas": "Philippines",
        "pilipinas": "Philippines",

        # UAE
        "संयुक्त अरब अमीरात": "United Arab Emirates",
        "यूएई": "United Arab Emirates",
        "الإمارات العربية المتحدة": "United Arab Emirates",

        # Bangladesh
        "बांग्लादेश": "Bangladesh",
        "বাংলাদেশ": "Bangladesh",

        # Nepal
        "नेपाल": "Nepal",

        # Sri Lanka
        "श्रीलंका": "Sri Lanka",
        "ශ්‍රී ලංකාව": "Sri Lanka",

        # Canada
        "कनाडा": "Canada",

        # Australia
        "ऑस्ट्रेलिया": "Australia",

        # New Zealand
        "न्यूज़ीलैंड": "New Zealand",
        "न्यूजीलैंड": "New Zealand",

        # Singapore
        "सिंगापुर": "Singapore",
        "സിംഗപ്പൂർ": "Singapore",

        # Malaysia
        "मलेशिया": "Malaysia",
        "മലേഷ്യ": "Malaysia",

        # Indonesia
        "इंडोनेशिया": "Indonesia",
        "ഇൻഡോനേഷ്യ": "Indonesia",

        # Thailand
        "थाईलैंड": "Thailand",
        "തായ്‌ലൻഡ്": "Thailand",

        # Japan
        "जापान": "Japan",
        "ജപ്പാൻ": "Japan",

        # China
        "चीन": "China",
        "ചൈന": "China",

        # South Korea
        "दक्षिण कोरिया": "South Korea",
        "ദക്ഷിണ കൊറിയ": "South Korea",

        # Saudi Arabia
        "सऊदी अरब": "Saudi Arabia",
        "المملكة العربية السعودية": "Saudi Arabia",

        # Qatar
        "कतर": "Qatar",
        "قطر": "Qatar",

        # Kuwait
        "कुवैत": "Kuwait",
        "الكويت": "Kuwait",

        # Oman
        "ओमान": "Oman",
        "عمان": "Oman",

        # Germany
        "जर्मनी": "Germany",

        # France
        "फ्रांस": "France",

        # Spain
        "स्पेन": "Spain",

        # Italy
        "इटली": "Italy"
    }

    # ==========================================================
    # LANGUAGE NORMALIZATION
    # ==========================================================

    LANGUAGE_VALUES = {
        "english": "English",
        "spanish": "Spanish",
        "español": "Spanish",
        "espanol": "Spanish",
        "hindi": "Hindi",
        "हिंदी": "Hindi",
        "हिन्दी": "Hindi",
        "malayalam": "Malayalam",
        "മലയാളം": "Malayalam",
        "tagalog": "Tagalog"
    }

    def normalize_language(self, text):

        if not text:
            return None

        value = str(text).strip()

        value = re.sub(
            r"[.!?,;:।،؟]+$",
            "",
            value
        ).strip()

        return self.LANGUAGE_VALUES.get(
            value.lower()
        )

    # ==========================================================
    # COUNTRY NORMALIZATION
    # ==========================================================

    def normalize_country(self, text):

        if not text:
            return None

        value = str(text).strip()

        value = re.sub(
            r"[.!?,;:।،؟]+$",
            "",
            value
        ).strip()

        if not value:
            return None

        # ------------------------------------------------------
        # Direct country match
        # ------------------------------------------------------

        key = value.lower()

        if key in self.COUNTRY_VALUES:
            return self.COUNTRY_VALUES[key]

        if value in self.MULTILINGUAL_COUNTRIES:
            return self.MULTILINGUAL_COUNTRIES[value]

        # ------------------------------------------------------
        # Normalize common speech-recognition punctuation
        # ------------------------------------------------------

        cleaned = re.sub(
            r"[,;:!?]+",
            " ",
            value
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned
        ).strip()

        cleaned_key = cleaned.lower()

        if cleaned_key in self.COUNTRY_VALUES:
            return self.COUNTRY_VALUES[cleaned_key]

        if cleaned in self.MULTILINGUAL_COUNTRIES:
            return self.MULTILINGUAL_COUNTRIES[cleaned]

        # ------------------------------------------------------
        # English spoken phrases
        # ------------------------------------------------------

        english_prefixes = [
            r"^i am from\s+",
            r"^i'm from\s+",
            r"^im from\s+",
            r"^i come from\s+",
            r"^i am in\s+",
            r"^i'm in\s+",
            r"^im in\s+",
            r"^from\s+",
            r"^my country is\s+",
            r"^country is\s+",
            r"^the country is\s+"
        ]

        for pattern in english_prefixes:

            candidate = re.sub(
                pattern,
                "",
                cleaned,
                flags=re.IGNORECASE
            ).strip()

            candidate_key = candidate.lower()

            if candidate_key in self.COUNTRY_VALUES:
                return self.COUNTRY_VALUES[candidate_key]

            if candidate in self.MULTILINGUAL_COUNTRIES:
                return self.MULTILINGUAL_COUNTRIES[candidate]

        # ------------------------------------------------------
        # Hindi phrases
        # ------------------------------------------------------

        hindi_prefixes = [
            r"^मैं\s+",
            r"^मेरा देश\s+",
            r"^मेरा देश है\s+",
            r"^मैं\s+से\s+"
        ]

        hindi_suffixes = [
            r"\s+से हूँ$",
            r"\s+से हूं$",
            r"\s+से है$",
            r"\s+में हूँ$",
            r"\s+में हूं$",
            r"\s+से$"
        ]

        hindi_candidate = value

        for pattern in hindi_prefixes:

            hindi_candidate = re.sub(
                pattern,
                "",
                hindi_candidate
            ).strip()

        for pattern in hindi_suffixes:

            hindi_candidate = re.sub(
                pattern,
                "",
                hindi_candidate
            ).strip()

        if hindi_candidate in self.MULTILINGUAL_COUNTRIES:
            return self.MULTILINGUAL_COUNTRIES[hindi_candidate]

        hindi_key = hindi_candidate.lower()

        if hindi_key in self.COUNTRY_VALUES:
            return self.COUNTRY_VALUES[hindi_key]

        # ------------------------------------------------------
        # Malayalam phrases
        # ------------------------------------------------------

        malayalam_candidate = value

        malayalam_prefixes = [
            r"^ഞാൻ\s+",
            r"^എന്റെ രാജ്യം\s+",
            r"^രാജ്യം\s+"
        ]

        malayalam_suffixes = [
            r"\s*ൽ നിന്നാണ്$",
            r"\s*യിൽ നിന്നാണ്$",
            r"\s*ആണ്$"
        ]

        for pattern in malayalam_prefixes:

            malayalam_candidate = re.sub(
                pattern,
                "",
                malayalam_candidate
            ).strip()

        for pattern in malayalam_suffixes:

            malayalam_candidate = re.sub(
                pattern,
                "",
                malayalam_candidate
            ).strip()

        if malayalam_candidate in self.MULTILINGUAL_COUNTRIES:
            return self.MULTILINGUAL_COUNTRIES[malayalam_candidate]

        # ------------------------------------------------------
        # Spanish phrases
        # ------------------------------------------------------

        spanish_prefixes = [
            r"^soy de\s+",
            r"^vengo de\s+",
            r"^mi país es\s+",
            r"^estoy en\s+"
        ]

        for pattern in spanish_prefixes:

            candidate = re.sub(
                pattern,
                "",
                cleaned,
                flags=re.IGNORECASE
            ).strip()

            candidate_key = candidate.lower()

            if candidate_key in self.COUNTRY_VALUES:
                return self.COUNTRY_VALUES[candidate_key]

        # ------------------------------------------------------
        # Tagalog phrases
        # ------------------------------------------------------

        tagalog_prefixes = [
            r"^galing ako sa\s+",
            r"^ako ay mula sa\s+",
            r"^ang bansa ko ay\s+"
        ]

        for pattern in tagalog_prefixes:

            candidate = re.sub(
                pattern,
                "",
                cleaned,
                flags=re.IGNORECASE
            ).strip()

            candidate_key = candidate.lower()

            if candidate_key in self.COUNTRY_VALUES:
                return self.COUNTRY_VALUES[candidate_key]

            if candidate in self.MULTILINGUAL_COUNTRIES:
                return self.MULTILINGUAL_COUNTRIES[candidate]

        # ------------------------------------------------------
        # Country mentioned inside a normal speech transcript
        # ------------------------------------------------------
        # This handles speech such as:
        #
        # "I am calling from India"
        # "I am from Pakistan"
        # "My country is the United States"
        #
        # without using Gemini.

        for country_key, country_value in self.COUNTRY_VALUES.items():

            if len(country_key) < 3:
                continue

            pattern = r"(?<!\w)" + re.escape(country_key) + r"(?!\w)"

            if re.search(
                pattern,
                cleaned_key,
                flags=re.IGNORECASE
            ):
                return country_value

        for country_key, country_value in self.MULTILINGUAL_COUNTRIES.items():

            if len(country_key) < 2:
                continue

            if country_key in value:
                return country_value

        return None

    # ==========================================================
    # GEMINI GENERATION HELPER
    # ==========================================================

    def _generate(self, system_instruction, user_text):

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )

        if not response or not response.text:
            return ""

        return response.text.strip()

    # ==========================================================
    # ENGLISH TRANSLATION
    # ==========================================================

    def to_english(self, text):

        if text is None:
            return ""

        text = str(text).strip()

        if not text:
            return ""

        # ------------------------------------------------------
        # Country
        # ------------------------------------------------------

        country = self.normalize_country(text)

        if country:
            return country

        # ------------------------------------------------------
        # Language
        # ------------------------------------------------------

        language = self.normalize_language(text)

        if language:
            return language

        # ------------------------------------------------------
        # Common exact values
        # ------------------------------------------------------

        english_values = {

            # English
            "yes": "Yes",
            "no": "No",

            # Hindi
            "हाँ": "Yes",
            "हां": "Yes",
            "जी हाँ": "Yes",
            "जी हां": "Yes",
            "नहीं": "No",

            # Malayalam
            "ഉണ്ട്": "Yes",
            "ഇല്ല": "No",

            # Tagalog
            "oo": "Yes",
            "opo": "Yes",
            "hindi": "No",

            # Spanish
            "sí": "Yes",
            "si": "Yes",
            "no": "No",

            # Traveller types
            "solo": "Solo",
            "solo traveller": "Solo",
            "single traveller": "Solo",

            "couple": "Couple",
            "couples": "Couple",

            "family": "Family",
            "families": "Family",

            "group": "Group",
            "groups": "Group"
        }

        if text.lower() in english_values:
            return english_values[text.lower()]

        # ------------------------------------------------------
        # Numeric values
        # ------------------------------------------------------

        numeric = text.replace(",", "").replace(".", "")

        if numeric.isdigit():
            return text

        # ------------------------------------------------------
        # Ask Gemini whether already English
        # ------------------------------------------------------

        detection_instruction = """
You are an English language detector.

Determine whether the customer's text is already written in English.

Return ONLY one word:

YES

or

NO

Rules:

- Do not translate.
- Do not explain.
- Do not rewrite the text.
- If the text is an English date, number, name, place,
  sentence, phrase, traveller answer, budget answer,
  visa answer, or normal English answer, return YES.
- If the text is not English, return NO.
"""

        detection = self._generate(
            detection_instruction,
            text
        )

        detected = detection.strip().upper()

        if detected == "YES":
            return text

        # ------------------------------------------------------
        # Translate
        # ------------------------------------------------------

        translation_instruction = """
You are a strict translation and normalization engine.

Translate the customer's answer into English.

Return ONLY the English customer answer.

Rules:

1. Do not explain.
2. Do not define anything.
3. Do not answer a question.
4. Do not add information.
5. Do not change the meaning.
6. Do not invent information.
7. Keep names unchanged.
8. Keep email addresses unchanged.
9. Keep phone numbers unchanged.
10. Keep dates as dates.
11. Keep numbers as numbers whenever possible.

12. Translate clear yes/no answers to exactly:

Yes

or

No

13. Translate traveller types to the simplest category:

Solo
Couple
Family
Group

14. If the customer gives a phrase meaning two people
travelling as husband and wife, return:

Couple

15. If the customer gives a phrase meaning travelling alone,
return:

Solo

16. If the customer gives a phrase meaning travelling with family,
return:

Family

17. If the customer gives a phrase meaning a group trip,
return:

Group

18. For number of travellers, return the number when it is clear.

Examples:

"दो लोग"
→ 2

"दो"
→ 2

"दो लोग यात्रा करेंगे"
→ 2

"two people"
→ 2

"तीन लोग"
→ 3

19. For children answers:
Return Yes or No only when the meaning is clear.

20. For visa answers:
Return Yes or No only when the meaning is clear.

21. Do not translate or modify a person's name.

22. Do not translate or modify an email address.

23. Do not translate or modify a phone number.

24. Never return:

"There is no text to translate."
"No translation needed."
"There is no translation."
"There is no text to translate"

25. Never provide explanations or commentary.

Return ONLY the English customer answer.
"""

        result = self._generate(
            translation_instruction,
            text
        )

        if not result:
            return text

        # ------------------------------------------------------
        # Remove accidental surrounding quotes
        # ------------------------------------------------------

        result = result.strip("\"'")

        # ------------------------------------------------------
        # Remove accidental markdown code fences
        # ------------------------------------------------------

        result = re.sub(
            r"^```(?:text|plaintext)?\s*",
            "",
            result,
            flags=re.IGNORECASE
        )

        result = re.sub(
            r"\s*```$",
            "",
            result
        ).strip()

        # ------------------------------------------------------
        # Reject known invalid model responses
        # ------------------------------------------------------

        invalid_responses = {

            "there is no text to translate.",
            "there is no translation.",
            "no translation needed.",
            "there is no text to translate",
            "there is no translation",
            "no translation needed"
        }

        if result.lower() in invalid_responses:
            return text

        return result


translation_service = TranslationService()