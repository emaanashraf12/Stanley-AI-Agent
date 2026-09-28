import re
import unicodedata
from unidecode import unidecode


from backend.services.booking_manager import booking_manager
from backend.services.session_manager import session_manager
from backend.flows.general_flow import handle_general
from backend.services.gemini_service import gemini_service
from backend.services.translation_service import translation_service
from backend.services.lead_manager import lead_manager
from backend.database.lead_repository import lead_repository
from backend.services.email_service import email_service


class HandleBooking:

    def normalize_country_name(self, value):

        if not value:
            return value

        cleaned = unicodedata.normalize(
            "NFKD",
            value
        ).encode(
            "ascii",
            "ignore"
        ).decode(
            "ascii"
        ).strip()

        country_aliases = {
            "pakistan": "Pakistan",
            "pakistan.": "Pakistan"
        }

        return country_aliases.get(
            cleaned.lower(),
            value.strip()
        )

    GENERAL_KEYWORDS = [

        "company",
        "business",
        "about",
        "office",
        "services",
        "visa",
        "payment",
        "refund",
        "cancel",
        "location",
        "working hours",
        "price",
        "pricing",
        "cost",
        "package",
        "packages",
        "tour",
        "hotel",
        "flight",
        "transport",
        "passport",
        "who are you",
        "what do you do",
        "tell me about your company",
        "tell me about stanley tours",
        "where is your office",
        "how can i pay",
        "do you provide visa",
        "do you provide flights",
        "do you provide hotels",

        # Hindi
        "कंपनी",
        "व्यवसाय",
        "ऑफिस",
        "सेवाएं",
        "वीजा",
        "भुगतान",
        "रिफंड",
        "रद्द",
        "स्थान",
        "कीमत",
        "पैकेज",
        "टूर",
        "होटल",
        "फ्लाइट",
        "परिवहन",
        "पासपोर्ट",
        "आप कौन हैं",
        "आप क्या करते हैं",
        "कंपनी के बारे में बताओ",
        "स्टेनली टूर्स के बारे में बताओ",
        "ऑफिस कहाँ है",

        # Arabic
        "شركة",
        "مكتب",
        "خدمات",
        "تأشيرة",
        "دفع",
        "استرداد",
        "إلغاء",
        "موقع",
        "سعر",
        "تكلفة",
        "باقة",
        "جولة",
        "فندق",
        "رحلة",
        "نقل",
        "جواز سفر",
        "من أنتم",
        "ماذا تفعلون",
        "أخبرني عن الشركة",
        "أخبرني عن ستانلي تورز",
        "أين مكتبكم",

        # Malayalam
        "കമ്പനി",
        "ഓഫീസ്",
        "സേവനങ്ങൾ",
        "വിസ",
        "പേയ്മെന്റ്",
        "റീഫണ്ട്",
        "റദ്ദാക്കൽ",
        "ലൊക്കേഷൻ",
        "വില",
        "ചെലവ്",
        "പാക്കേജ്",
        "ടൂർ",
        "ഹോട്ടൽ",
        "ഫ്ലൈറ്റ്",
        "ഗതാഗതം",
        "പാസ്‌പോർട്ട്",
        "നിങ്ങൾ ആരാണ്",
        "നിങ്ങൾ എന്താണ് ചെയ്യുന്നത്",
        "കമ്പനിയെക്കുറിച്ച് പറയൂ",
        "സ്റ്റാൻലി ടൂറ്സിനെക്കുറിച്ച് പറയൂ",

        # Tamil
        "நிறுவனம்",
        "அலுவலகம்",
        "சேவைகள்",
        "விசா",
        "கட்டணம்",
        "பணம்",
        "ரீபண்ட்",
        "ரத்து",
        "இடம்",
        "விலை",
        "செலவு",
        "பேக்கேஜ்",
        "சுற்றுலா",
        "ஹோட்டல்",
        "விமானம்",
        "போக்குவரத்து",
        "பாஸ்போர்ட்",
        "நீங்கள் யார்",
        "நீங்கள் என்ன செய்கிறீர்கள்",
        "உங்கள் நிறுவனத்தைப் பற்றி சொல்லுங்கள்",
        "ஸ்டான்லி டூர்ஸ் பற்றி சொல்லுங்கள்",

        # Tagalog
        "kumpanya",
        "opisina",
        "serbisyo",
        "visa",
        "bayad",
        "refund",
        "kanselahin",
        "lokasyon",
        "presyo",
        "gastos",
        "pakete",
        "tour",
        "hotel",
        "lipad",
        "transportasyon",
        "pasaporte",
        "sino kayo",
        "ano ang ginagawa ninyo",
        "sabihin mo ang tungkol sa kumpanya",
        "sabihin mo ang tungkol sa stanley tours"
    ]

    # ==========================================================
    # LANGUAGE
    # ==========================================================

    def can_handle(self, lead):

        return (
            lead.booking_started
            and lead.preferred_language != ""
        )

    # ==========================================================
    # NAME EXTRACTION
    # ==========================================================

    def extract_name(self, user_message, language):

        if not user_message:
            return None

        text = str(
            user_message
        ).strip()

        if not text:
            return None

        text = re.sub(
            r"^[.!?,;:\s]+|[.!?,;:\s]+$",
            "",
            text
        ).strip()

        if not text:
            return None

        # ------------------------------------------------------
        # English
        # ------------------------------------------------------

        english_patterns = [
            r"^my name is\s+",
            r"^my full name is\s+",
            r"^i am\s+",
            r"^i'm\s+",
            r"^this is\s+",
            r"^you can call me\s+"
        ]

        for pattern in english_patterns:

            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            ).strip()

        # ------------------------------------------------------
        # Hindi
        # ------------------------------------------------------

        hindi_patterns = [
            r"^मेरा नाम है\s+",
            r"^मेरा नाम\s+",
            r"^मैं\s+"
        ]

        for pattern in hindi_patterns:

            text = re.sub(
                pattern,
                "",
                text
            ).strip()

        # ------------------------------------------------------
        # Malayalam
        # ------------------------------------------------------

        malayalam_patterns = [
            r"^എന്റെ പേര് ആണ്\s+",
            r"^എന്റെ പേര്\s+",
            r"^ഞാൻ\s+"
        ]

        for pattern in malayalam_patterns:

            text = re.sub(
                pattern,
                "",
                text
            ).strip()

        # ------------------------------------------------------
        # Spanish
        # ------------------------------------------------------

        spanish_patterns = [
            r"^me llamo\s+",
            r"^mi nombre es\s+",
            r"^soy\s+"
        ]

        for pattern in spanish_patterns:

            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            ).strip()

        # ------------------------------------------------------
        # Tagalog
        # ------------------------------------------------------

        tagalog_patterns = [
            r"^ang pangalan ko ay\s+",
            r"^pangalan ko ay\s+",
            r"^ako si\s+"
        ]

        for pattern in tagalog_patterns:

            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            ).strip()

        text = re.sub(
            r"[.!?,;:]+$",
            "",
            text
        ).strip()

        if not text:
            return None

        invalid_values = {

            "yes",
            "no",
            "yeah",
            "yep",
            "okay",
            "ok",
            "sure",
            "hello",
            "hi",
            "hey",

            "हाँ",
            "हां",
            "नहीं",

            "ശരി",
            "ഉണ്ട്",
            "ഇല്ല",

            "oo",
            "opo",
            "hindi",

            "sí",
            "si"
        }

        if text.lower() in invalid_values:
            return None

        if len(
            text.split()
        ) > 5:
            return None

        if language in ["Hindi", "Malayalam", "Tagalog", "Spanish"]:

            try:

                latin_name = unidecode(
                    text
                ).strip()

                if latin_name:
                    return latin_name.title()

            except Exception as exc:

                print(
                    "NAME TRANSLITERATION ERROR:",
                    repr(exc)
                )

        # ------------------------------------------------------
        # Spelled-out name: "S-E-A-N", "s e a n", "S.E.A.N"
        # Only collapse when EVERY token is a single letter.
        # "Mary Jane" is NOT affected.
        # ------------------------------------------------------
        tokens = re.split(r"[\s\-.]+", text.strip())

        if (
            len(tokens) >= 2
            and all(len(t) == 1 and t.isalpha() for t in tokens)
        ):
            return "".join(tokens).title()

        # ------------------------------------------------------
        # Single all-caps token that looks like a spelled name
        # e.g. "SEAN" shouted — leave as Title Case
        # ------------------------------------------------------
        if (
            len(tokens) == 1
            and text.isupper()
            and 2 <= len(text) <= 15
        ):
            return text.title()

        return text.title()

    # ==========================================================
    # EMAIL NORMALIZATION
    # ==========================================================

    def normalize_email(self, user_message):

        if not user_message:
            return None

        original_text = str(
            user_message
        ).strip()

        if not original_text:
            return None

        # ------------------------------------------------------
        # Final email cleaner / validator
        # ------------------------------------------------------

        def clean_and_validate(candidate):

            if not candidate:
                return None

            text = str(
                candidate
            ).strip().lower()

            text = text.replace(
                "`",
                ""
            )

            text = text.replace(
                '"',
                ""
            )

            text = text.replace(
                "'",
                ""
            )

            text = re.sub(
                r"^email\s*:\s*",
                "",
                text,
                flags=re.IGNORECASE
            )

            text = re.sub(
                r"\s*@\s*",
                "@",
                text
            )

            text = re.sub(
                r"\s*\.\s*",
                ".",
                text
            )

            text = re.sub(
                r"\s+",
                "",
                text
            )

            text = re.sub(
                r"[^a-z0-9.!#$%&*+/=?^_{}|~@-]",
                "",
                text
            )

            if text.count("@") != 1:
                return None

            local, domain = text.split(
                "@",
                1
            )

            if not local or not domain:
                return None

            if "." not in domain:
                return None

            if local.startswith("."):
                return None

            if local.endswith("."):
                return None

            if ".." in local:
                return None

            if domain.startswith("."):
                return None

            if domain.endswith("."):
                return None

            if ".." in domain:
                return None

            if not re.match(
                r"^[a-z0-9.!#$%&*+/=?^_{}|~-]+$",
                local
            ):
                return None

            if not re.match(
                r"^[a-z0-9.-]+\.[a-z]{2,}$",
                domain
            ):
                # --------------------------------------------------
                # Soft repair: if domain has no dot but ends with a
                # known TLD-ish word, add it. e.g. "gmailcom" -> "gmail.com"
                # --------------------------------------------------
                soft_repairs = {
                    "gmailcom":  "gmail.com",
                    "yahoocom":  "yahoo.com",
                    "outlookcom":"outlook.com",
                    "hotmailcom":"hotmail.com",
                    "icloudcom": "icloud.com",
                    "gmailc0m":  "gmail.com",
                    "gmai1com":  "gmail.com",
                }
                repaired = soft_repairs.get(domain)
                if repaired:
                    domain = repaired
                else:
                    return None

            return f"{local}@{domain}"

        # ------------------------------------------------------
        # First direct normalization attempt
        # ------------------------------------------------------

        text = original_text.lower().strip()

        # ------------------------------------------------------
        # Collapse letter-by-letter spelling BEFORE any symbol
        # substitution. Runs of 2-31 single letters only.
        #
        # "j o h n at gmail dot com" -> "john at gmail dot com"
        # "j-o-h-n at gmail dot com" -> "john at gmail dot com"
        # ------------------------------------------------------
        text = re.sub(
            r"\b(?:[a-z][\s\-.]?){2,31}\b",
            lambda m: re.sub(r"[\s\-.]", "", m.group(0)),
            text
        )

        # ------------------------------------------------------
        # Spanish STT accent normalization for email addresses
        # ------------------------------------------------------

        spanish_email_characters = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
            "ñ": "n"
        }

        for accented, normal in spanish_email_characters.items():

            text = text.replace(
                accented,
                normal
            )

        replacements = [

            # English
            (
                r"\bat the rate of\b",
                "@"
            ),
            (
                r"\bat the rate\b",
                "@"
            ),
            (
                r"\bat sign\b",
                "@"
            ),
            (
                r"\bat symbol\b",
                "@"
            ),
            (
                r"\bat\b",
                "@"
            ),

            (
                r"\bdot\b",
                "."
            ),
            (
                r"\bperiod\b",
                "."
            ),

            (
                r"\bunderscore\b",
                "_"
            ),
            (
                r"\bhyphen\b",
                "-"
            ),
            (
                r"\bdash\b",
                "-"
            ),

            # Hindi
            (
                r"एट द रेट",
                "@"
            ),
            (
                r"ऐट द रेट",
                "@"
            ),
            (
                r"एट",
                "@"
            ),
            (
                r"ऐट",
                "@"
            ),

            (
                r"डॉट",
                "."
            ),
            (
                r"डाट",
                "."
            ),

            (
                r"अंडरस्कोर",
                "_"
            ),
            (
                r"हाइफन",
                "-"
            ),
            (
                r"डैश",
                "-"
            ),

            # Malayalam
            (
                r"അറ്റ് ദ റേറ്റ്",
                "@"
            ),
            (
                r"അറ്റ്",
                "@"
            ),
            (
                r"ആറ്റ്",
                "@"
            ),

            (
                r"ഡോട്ട്",
                "."
            ),
            (
                r"ഡോട്",
                "."
            ),

            (
                r"അണ്ടർസ്കോർ",
                "_"
            ),
            (
                r"ഹൈഫൻ",
                "-"
            ),
            (
                r"ഡാഷ്",
                "-"
            ),

            # Spanish
            (
                r"\barroba\b",
                "@"
            ),
            (
                r"\bpunto\b",
                "."
            ),

            # Tagalog
            (
                r"\bat\b",
                "@"
            ),
            (
                r"\btuldok\b",
                "."
            )
        ]

        for pattern, replacement in replacements:

            text = re.sub(
                pattern,
                replacement,
                text,
                flags=re.IGNORECASE
            )

        # ------------------------------------------------------
        # Provider names
        # ------------------------------------------------------

        provider_replacements = [

            # English
            (
                r"\bgmail\b",
                "gmail"
            ),

            # Spanish STT may hear "gmail" as "jimmy"
            (
                r"\bjimmy\b",
                "gmail"
            ),
            (
                r"\bjimi\b",
                "gmail"
            ),
            (
                r"\bg\s+mail\b",
                "gmail"
            ),
            (
                r"\byahoo\b",
                "yahoo"
            ),
            (
                r"\boutlook\b",
                "outlook"
            ),
            (
                r"\bhotmail\b",
                "hotmail"
            ),
            (
                r"\bicloud\b",
                "icloud"
            ),

            # Hindi
            (
                r"जीमेल",
                "gmail"
            ),
            (
                r"जिमेल",
                "gmail"
            ),
            (
                r"जी मेल",
                "gmail"
            ),

            (
                r"याहू",
                "yahoo"
            ),

            (
                r"आउटलुक",
                "outlook"
            ),

            (
                r"हॉटमेल",
                "hotmail"
            ),
            (
                r"हाटमेल",
                "hotmail"
            ),

            (
                r"आईक्लाउड",
                "icloud"
            ),
            (
                r"आइक्लाउड",
                "icloud"
            ),

            # Malayalam
            (
                r"ജിമെയിൽ",
                "gmail"
            ),
            (
                r"ജിമെയില്",
                "gmail"
            ),
            (
                r"ജി മെയിൽ",
                "gmail"
            ),
            (
                r"ജി മെയില്",
                "gmail"
            ),

            (
                r"യാഹൂ",
                "yahoo"
            ),

            (
                r"ഔട്ട്ലുക്ക്",
                "outlook"
            ),
            (
                r"ഔട്ട്‌ലുക്ക്",
                "outlook"
            ),

            (
                r"ഹോട്ട്മെയിൽ",
                "hotmail"
            ),
            (
                r"ഹോട്ട്മെയില്",
                "hotmail"
            ),

            (
                r"ഐക്ലൗഡ്",
                "icloud"
            ),

            # Spoken COM
            (
                r"कॉम",
                "com"
            ),
            (
                r"കോം",
                "com"
            )
        ]

        for pattern, replacement in provider_replacements:

            text = re.sub(
                pattern,
                replacement,
                text,
                flags=re.IGNORECASE
            )

        # ------------------------------------------------------
        # Remove introductory speech
        # ------------------------------------------------------

        introductory_patterns = [

            # English
            r"^(my\s+)?email\s+address\s+is\s+",
            r"^(my\s+)?email\s+is\s+",
            r"^(my\s+)?e-mail\s+is\s+",
            r"^(my\s+)?mail\s+is\s+",

            # Hindi
            r"^मेरा\s+ईमेल\s+है\s+",
            r"^मेरा\s+ईमेल\s+पता\s+है\s+",
            r"^मेरी\s+ईमेल\s+है\s+",

            # Malayalam
            r"^എന്റെ\s+ഇമെയിൽ\s+",
            r"^എന്റെ\s+ഇമെയിൽ\s+വിലാസം\s+",
            r"^എന്റെ\s+ഇമെയില്\s+",

            # Spanish
            r"^mi\s+correo\s+es\s+",
            r"^mi\s+correo\s+electrónico\s+es\s+",

            # Tagalog
            r"^ang\s+email\s+ko\s+ay\s+"
        ]

        for pattern in introductory_patterns:

            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE
            ).strip()

        providers = [
            "gmail",
            "yahoo",
            "outlook",
            "hotmail",
            "icloud"
        ]

        for provider in providers:

            text = re.sub(
                rf"\b{provider}\s*(?:dot|\.)?\s*com\b",
                f"{provider}.com",
                text,
                flags=re.IGNORECASE
            )

        text = re.sub(
            r"\s*@\s*",
            "@",
            text
        )

        text = re.sub(
            r"\s*\.\s*",
            ".",
            text
        )

        if "@" not in text:

            text = re.sub(
                r"\s+(gmail\.com|yahoo\.com|outlook\.com|"
                r"hotmail\.com|icloud\.com)\b",
                r"@\1",
                text,
                flags=re.IGNORECASE
            )

        direct_email = clean_and_validate(
            text
        )

        if direct_email:
            return direct_email

        # ------------------------------------------------------
        # Local transliteration fallback
        # ------------------------------------------------------

        try:

            transliterated_text = unidecode(
                text
            )

            transliterated_text = (
                transliterated_text
                .lower()
                .strip()
            )

            local_email = clean_and_validate(
                transliterated_text
            )

            if local_email:

                print(
                    "LOCAL EMAIL NORMALIZED =",
                    local_email
                )

                return local_email

        except Exception as exc:

            print(
                "LOCAL EMAIL TRANSLITERATION ERROR:",
                repr(exc)
            )

        # ------------------------------------------------------
        # AI fallback for non-Latin / difficult STT email
        # ------------------------------------------------------

        try:

            email_prompt = f"""
You are extracting an email address from speech-to-text.

The customer may have spoken the email in English, Hindi,
Malayalam, Spanish, or Tagalog.

Convert the spoken email into a normal ASCII email address.

STRICT RULES:

1. Return ONLY the email address.
2. Do not explain anything.
3. Do not add quotes.
4. Do not add markdown.
5. Transliterate names and usernames by SOUND into Latin letters.
6. Do NOT translate the meaning of a person's name or username.
7. Convert spoken words such as:
   at, at sign, at the rate -> @
   dot, period -> .
8. Convert equivalent Hindi, Malayalam, Spanish and Tagalog
   spoken forms of @ and dot as well.
9. Preserve numbers in the username.
10. If there is clearly no complete email address, return NONE.

Examples:

"emaan ashraf at gmail dot com"
-> emaanashraf@gmail.com

"ईमान अशरफ एट जीमेल डॉट कॉम"
-> emaanashraf@gmail.com

"ഇമാൻ അഷ്റഫ് അറ്റ് ജിമെയിൽ ഡോട്ട് കോം"
-> emaanashraf@gmail.com


Speech transcription:

{original_text}
"""

            ai_result = gemini_service.chat(
                question=email_prompt,
                context="",
                conversation_history="",
                lead_language="English"
            )

        except Exception as exc:

            print(
                "EMAIL EXTRACTION ERROR:",
                repr(exc)
            )

            ai_result = ""

        if not ai_result:
            return None

        ai_result = str(
            ai_result
        ).strip()

        if ai_result.upper() == "NONE":
            return None

        email_match = re.search(
            r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
            r"@"
            r"[A-Za-z0-9.-]+"
            r"\.[A-Za-z]{2,}",
            ai_result
        )

        if email_match:

            ai_result = email_match.group(
                0
            )

        return clean_and_validate(
            ai_result
        )

    # ==========================================================
    # YES / NO NORMALIZATION
    # ==========================================================

    def normalize_yes_no(self, user_message):

        if not user_message:
            return None

        text = str(user_message).strip().lower()

        text = re.sub(
            r"[.!?,;:।،؟]+$",
            "",
            text
        ).strip()

        yes_values = {
            # English
            "yes",
            "yeah",
            "yep",
            "yes please",
            "i do",
            "i have",

            # Hindi
            "हाँ",
            "हां",
            "जी हाँ",
            "जी हां",
            "है",
            "हैं",

            # Malayalam
            "ഉണ്ട്",
            "അതെ",
            "ശരി",
            "വേണം",

            # Spanish
            "sí",
            "si",
            "claro",

            # Tagalog / Filipino
            "oo",
            "opo",
            "meron",
            "mayroon"
        }

        no_values = {
            # English
            "no",
            "nope",
            "i don't",
            "i do not",
            "none",

            # Hindi
            "नहीं",
            "नही",
            "जी नहीं",
            "नहीं है",

            # Malayalam
            "ഇല്ല",
            "വേണ്ട",

            # Spanish
            "no",

            # Tagalog / Filipino
            # IMPORTANT: "hindi" means NO in Tagalog.
            "hindi",
            "wala",
            "hindi po"
        }

        if text in yes_values:
            return "Yes"

        if text in no_values:
            return "No"

        # Translation fallback for longer multilingual answers
        try:

            translated = translation_service.to_english(
                user_message
            )

            if translated:

                translated = (
                    str(translated)
                    .strip()
                    .lower()
                )

                if translated == "yes":
                    return "Yes"

                if translated == "no":
                    return "No"

        except Exception as exc:

            print(
                "YES/NO NORMALIZATION ERROR:",
                repr(exc)
            )

        return None
    
    # ==========================================================
    # TRAVELLER COUNT NORMALIZATION
    # ==========================================================

    def normalize_travellers(self, user_message):

        if not user_message:
            return user_message

        text = str(user_message).lower().strip()

        text = re.sub(
            r"[.!?,;:।]+",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        # ------------------------------------------------------
        # DIGITS
        # ------------------------------------------------------

        digit_match = re.search(
            r"\b([1-9]|[1-9][0-9])\b",
            text
        )

        if digit_match:
            return digit_match.group(1)

        # ------------------------------------------------------
        # NUMBER WORDS
        # English + Hindi + Malayalam + Spanish + Tagalog
        # ------------------------------------------------------

        number_words = {

            # English
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",

            # Hindi
            "एक": "1",
            "दो": "2",
            "तीन": "3",
            "चार": "4",
            "पांच": "5",
            "पाँच": "5",
            "छह": "6",
            "छः": "6",
            "सात": "7",
            "आठ": "8",
            "नौ": "9",
            "दस": "10",

            # Malayalam
            "ഒന്ന്": "1",
            "രണ്ട്": "2",
            "മൂന്ന്": "3",
            "നാല്": "4",
            "നാലു": "4",
            "അഞ്ച്": "5",
            "ആറ്": "6",
            "ഏഴ്": "7",
            "എട്ട്": "8",
            "ഒമ്പത്": "9",
            "പത്ത്": "10",

            # Spanish
            "uno": "1",
            "una": "1",
            "dos": "2",
            "tres": "3",
            "cuatro": "4",
            "cinco": "5",
            "seis": "6",
            "siete": "7",
            "ocho": "8",
            "nueve": "9",
            "diez": "10",

            # Tagalog
            "isa": "1",
            "isang": "1",
            "dalawa": "2",
            "dalawang": "2",
            "tatlo": "3",
            "tatlong": "3",
            "apat": "4",
            "apat na": "4",
            "lima": "5",
            "limang": "5",
            "anim": "6",
            "anim na": "6",
            "pito": "7",
            "pitong": "7",
            "walo": "8",
            "walong": "8",
            "siyam": "9",
            "siyam na": "9",
            "sampu": "10",
            "sampung": "10"
        }

        # Check longer phrases first
        for number_word in sorted(
            number_words,
            key=len,
            reverse=True
        ):

            if re.search(
                rf"(?<!\w){re.escape(number_word)}(?!\w)",
                text
            ):
                return number_words[number_word]

        # Do not store an invalid traveller count.
        return str(user_message).strip()

    # ==========================================================
    # TRAVELLER TYPE NORMALIZATION
    # ==========================================================

    def normalize_traveller_type(self, user_message):

        if not user_message:
            return user_message

        text = str(user_message).lower().strip()

        text = re.sub(
            r"[.!?,;:।]+",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        # ------------------------------------------------------
        # SOLO
        # ------------------------------------------------------

        solo_words = [

            # English
            "solo",
            "alone",
            "single",
            "by myself",

            # Hindi
            "अकेले",
            "अकेला",
            "अकेली",
            "एकल",

            # Malayalam
            "ഒറ്റയ്ക്ക്",
            "ഒറ്റക്ക്",
            "തനിച്ച്",

            # Spanish
            "solo",
            "sola",
            "individual",

            # Tagalog
            "solo",
            "mag-isa",
            "mag isa",
            "nag-iisa"
        ]

        # ------------------------------------------------------
        # COUPLE
        # ------------------------------------------------------

        couple_words = [

            # English
            "couple",
            "pair",

            # Hindi
            "कपल",
            "जोड़ा",
            "दम्पति",
            "दंपति",

            # Malayalam
            "ദമ്പതികൾ",
            "ദമ്പതി",
            "കപ്പിൾ",

            # Spanish
            "pareja",
            "dos personas",

            # Tagalog
            "mag-asawa",
            "mag asawa",
            "couple",
            "dalawa"
        ]

        # ------------------------------------------------------
        # FAMILY
        # ------------------------------------------------------

        family_words = [

            # English
            "family",

            # Hindi
            "परिवार",
            "फैमिली",
            "परिवार के लिए",

            # Malayalam
            "കുടുംബം",
            "കുടുംബത്തിന്",
            "ഫാമിലി",

            # Spanish
            "familia",
            "familiar",

            # Tagalog
            "pamilya",
            "family"
        ]

        # ------------------------------------------------------
        # GROUP
        # ------------------------------------------------------

        group_words = [

            # English
            "group",

            # Hindi
            "समूह",
            "समूह के लिए",
            "ग्रुप",
            "ग्रुप के लिए",

            # Malayalam
            "ഗ്രൂപ്പ്",
            "സംഘം",
            "കൂട്ടം",

            # Spanish
            "grupo",
            "en grupo",

            # Tagalog
            "grupo",
            "group",
            "pangkat"
        ]

        categories = [
            ("Solo", solo_words),
            ("Couple", couple_words),
            ("Family", family_words),
            ("Group", group_words)
        ]

        for normalized_value, phrases in categories:

            for phrase in sorted(
                phrases,
                key=len,
                reverse=True
            ):

                if re.search(
                    rf"(?<!\w){re.escape(phrase)}(?!\w)",
                    text
                ):
                    return normalized_value

        # If not recognized, preserve original answer.
        # NO retry.
        return str(user_message).strip()

    # ==========================================================
    # COUNTRY VALIDATION
    # ==========================================================

    def normalize_country(
        self,
        user_message
    ):

        country = (
            translation_service.normalize_country(
                user_message
            )
        )

        return country

    # ==========================================================
    # SAFE DATABASE TRANSLATION
    #
    # A temporary Gemini error must not destroy a completed
    # booking. If translation fails, preserve the original value.
    # ==========================================================

    def safe_to_english(
        self,
        value
    ):

        if value is None:
            return value

        if str(value).strip() == "":
            return value

        try:

            translated = (
                translation_service.to_english(
                    value
                )
            )

            if translated:

                return translated

        except Exception as exc:

            print(
                "DATABASE TRANSLATION ERROR:",
                repr(exc)
            )

        return value

    # ==========================================================
    # DATABASE NORMALIZATION
    # ==========================================================

    def normalize_for_database(
        self,
        lead
    ):
        
        lead.country = self.safe_to_english(
            lead.country
        )

        lead.destination = self.safe_to_english(
            lead.destination
        )

        lead.travel_date = self.safe_to_english(
            lead.travel_date
        )

        lead.travellers = self.safe_to_english(
            lead.travellers
        )

        lead.traveller_type = self.safe_to_english(
            lead.traveller_type
        )

        lead.children_travelling = self.safe_to_english(
            lead.children_travelling
        )

        lead.budget = self.safe_to_english(
            lead.budget
        )

        lead.visa_required = self.safe_to_english(
            lead.visa_required
        )

        lead.special_requests = self.safe_to_english(
            lead.special_requests
        )

    # ==========================================================
    # PROCESS
    # ==========================================================

    def process(
        self,
        session_id,
        lead,
        user_message
    ):

        user_message = str(
            user_message or ""
        ).strip()

        lower = (
            user_message
            .lower()
            .strip()
        )

        # ------------------------------------------------------
        # General mode
        # ------------------------------------------------------

        if lead.conversation_mode == "general":

            continue_words = [

                "continue",
                "yes",
                "ok",
                "okay",
                "sure",

                "हाँ",
                "हां",
                "ठीक",

                "ശരി",

                "sí",
                "si",

                "oo",
                "opo"
            ]

            if lower in continue_words:

                lead.conversation_mode = "booking"

                reply = booking_manager.next_question(
                    lead
                )

                session_manager.add_message(
                    session_id,
                    "assistant",
                    reply
                )

                return reply

            return handle_general(
                session_id,
                lead,
                user_message
            )

        # ------------------------------------------------------
        # General inquiries
        # ------------------------------------------------------

        current_field_answer_expected = any([

            lead.country == "",

            lead.name == "",

            lead.phone == "",

            lead.phone_verified is False,

            lead.email == "",

            lead.destination == "",

            lead.travel_date == "",

            lead.travellers == "",

            lead.traveller_type == "",

            lead.children_travelling == "",

            lead.budget == "",

            lead.visa_required == "",

            lead.special_requests == ""
        ])

        looks_like_question = (

            "?" in user_message

            or lower.startswith(
                "what "
            )

            or lower.startswith(
                "how "
            )

            or lower.startswith(
                "where "
            )

            or lower.startswith(
                "when "
            )

            or lower.startswith(
                "who "
            )

            or lower.startswith(
                "do you "
            )

            or lower.startswith(
                "can you "
            )

            or lower.startswith(
                "tell me "
            )
        )

        if (
            not current_field_answer_expected
            and looks_like_question
            and any(
                keyword in lower
                for keyword
                in self.GENERAL_KEYWORDS
            )
        ):

            lead.conversation_mode = "general"

            answer = handle_general(
                session_id,
                lead,
                user_message
            )

            answer += (
                "\n\n(You can say 'continue' whenever you want "
                "to continue your booking.)"
            )

            return answer

        # ------------------------------------------------------
        # Country
        # ------------------------------------------------------

        if lead.country == "":

            country_input = self.normalize_country_name(
                user_message
            )

            normalized_country = (
                self.normalize_country(
                    country_input
                )
            )

            if normalized_country:

                lead.country = (
                    normalized_country
                )

            else:

                COUNTRY_QUESTIONS = {

                    "English":
                        "Which country are you contacting us from?",

                    "Spanish":
                        "¿Desde qué país se está poniendo en contacto con nosotros?",

                    "Hindi":
                        "आप किस देश से हमसे संपर्क कर रहे हैं?",

                    "Malayalam":
                        "ഏത് രാജ്യത്തുനിന്നാണ് ഞങ്ങളെ ബന്ധപ്പെടുന്നത്?",

                    "Tagalog":
                        "Saang bansa kayo nakikipag-ugnayan sa amin?"
                }

                reply = (
                    COUNTRY_QUESTIONS.get(
                        lead.preferred_language,
                        COUNTRY_QUESTIONS[
                            "English"
                        ]
                    )
                )

                session_manager.add_message(
                    session_id,
                    "assistant",
                    reply
                )

                return reply

        # ------------------------------------------------------
        # Name
        # ------------------------------------------------------

        elif lead.name == "":

            extracted_name = (
                self.extract_name(
                    user_message,
                    lead.preferred_language
                )
            )

            if extracted_name:

                lead.name = extracted_name

            else:

                name_retry_messages = {

                    "English":
                        "Please say your full name again slowly.",

                    "Spanish":
                        "Por favor, diga nuevamente su nombre completo lentamente.",

                    "Hindi":
                        "कृपया अपना पूरा नाम फिर से धीरे-धीरे बोलें।",

                    "Malayalam":
                        "ദയവായി താങ്കളുടെ മുഴുവൻ പേര് വീണ്ടും പതുക്കെ പറയൂ.",

                    "Tagalog":
                        "Pakisabi muli nang dahan-dahan ang iyong buong pangalan."
                }

                reply = (
                    name_retry_messages.get(
                        lead.preferred_language,
                        name_retry_messages[
                            "English"
                        ]
                    )
                )

                session_manager.add_message(
                    session_id,
                    "assistant",
                    reply
                )

                return reply

        # ------------------------------------------------------
        # Phone
        # ------------------------------------------------------

        elif lead.phone == "":

            lead.phone = user_message

            from backend.services.otp_service import otp_service

            try:

                otp_sent = (
                    otp_service.send_otp(
                        lead
                    )
                )

            except Exception as exc:

                print(
                    "OTP SEND ERROR:",
                    repr(exc)
                )

                otp_sent = False

            if not otp_sent:

                lead.phone = ""

                # --------------------------------------------------
                # Spanish / Tagalog phone STT fallback
                # --------------------------------------------------

                session = session_manager.get(
                    session_id
                )

                if session is not None:

                    if lead.preferred_language == "Malayalam":

                        current_language = session.get(
                            "malayalam_phone_language",
                            "ml-IN"
                        )

                        if current_language == "ml-IN":

                            session[
                                "malayalam_phone_language"
                            ] = "en-US"

                        else:

                            session[
                                "malayalam_phone_language"
                            ] = "ml-IN"

                    elif lead.preferred_language == "Spanish":

                        current_language = session.get(
                            "spanish_phone_language",
                            "en-US"
                        )

                        if current_language == "en-US":

                            session[
                                "spanish_phone_language"
                            ] = "es-ES"

                        else:

                            session[
                                "spanish_phone_language"
                            ] = "en-US"

                    elif lead.preferred_language == "Tagalog":

                        current_language = session.get(
                            "tagalog_phone_language",
                            "en-US"
                        )

                        if current_language == "en-US":

                            session[
                                "tagalog_phone_language"
                            ] = "fil-PH"

                        else:

                            session[
                                "tagalog_phone_language"
                            ] = "en-US"

                phone_retry_messages = {

                    "English": (
                        "I could not verify that phone number. "
                        "Please provide your complete phone number again, "
                        "including the country code."
                    ),

                    "Spanish": (
                        "No pude verificar ese número de teléfono. "
                        "Por favor, indique nuevamente el número completo "
                        "incluido el código de país."
                    ),

                    "Hindi": (
                        "मैं उस फोन नंबर को सत्यापित नहीं कर पाया। "
                        "कृपया देश के कोड सहित अपना पूरा फोन नंबर फिर से बताएं।"
                    ),

                    "Malayalam": (
                        "ആ ഫോൺ നമ്പർ സ്ഥിരീകരിക്കാൻ കഴിഞ്ഞില്ല. "
                        "രാജ്യ കോഡ് ഉൾപ്പെടെ മുഴുവൻ ഫോൺ നമ്പർ വീണ്ടും പറയൂ."
                    ),

                    "Tagalog": (
                        "Hindi ko ma-verify ang numero ng telepono. "
                        "Pakibigay muli ang buong numero kasama ang country code."
                    )
                }

                reply = (
                    phone_retry_messages.get(
                        lead.preferred_language,
                        phone_retry_messages[
                            "English"
                        ]
                    )
                )

                session_manager.add_message(
                    session_id,
                    "assistant",
                    reply
                )

                return reply

            otp_messages = {

                "English": (
                    "We sent a verification code to your phone. "
                    "Please say the verification code."
                ),

                "Spanish": (
                    "Hemos enviado un código de verificación a su teléfono. "
                    "Por favor, diga el código de verificación."
                ),

                "Hindi": (
                    "हमने आपके फोन पर एक सत्यापन कोड भेजा है। "
                    "कृपया सत्यापन कोड बताएं।"
                ),

                "Malayalam": (
                    "താങ്കളുടെ ഫോണിലേക്ക് ഒരു സ്ഥിരീകരണ കോഡ് അയച്ചിട്ടുണ്ട്. "
                    "ദയവായി സ്ഥിരീകരണ കോഡ് പറയൂ."
                ),

                "Tagalog": (
                    "Nagpadala kami ng verification code sa iyong telepono. "
                    "Pakisabi ang verification code."
                )
            }

            reply = (
                otp_messages.get(
                    lead.preferred_language,
                    otp_messages[
                        "English"
                    ]
                )
            )

            session_manager.add_message(
                session_id,
                "assistant",
                reply
            )

            return reply

        # ------------------------------------------------------
        # Phone OTP
        # ------------------------------------------------------

        elif lead.phone_verified is False:

            from backend.services.otp_service import otp_service

            try:

                verified = (
                    otp_service.verify(
                        lead,
                        user_message
                    )
                )

            except Exception as exc:

                print(
                    "OTP VERIFY ERROR:",
                    repr(exc)
                )

                verified = False

            if verified:

                lead.phone_verified = True

                reply = booking_manager.next_question(
                    lead
                )

                session_manager.add_message(
                    session_id,
                    "assistant",
                    reply
                )

                return reply

            otp_retry_messages = {

                "English": (
                    "That verification code was not correct. "
                    "Please say the correct code again."
                ),

                "Spanish": (
                    "Ese código de verificación no es correcto. "
                    "Por favor, diga nuevamente el código correcto."
                ),

                "Hindi": (
                    "वह सत्यापन कोड सही नहीं है। "
                    "कृपया सही कोड फिर से बताएं।"
                ),

                "Malayalam": (
                    "ആ സ്ഥിരീകരണ കോഡ് ശരിയല്ല. "
                    "ദയവായി ശരിയായ കോഡ് വീണ്ടും പറയൂ."
                ),

                "Tagalog": (
                    "Hindi tama ang verification code. "
                    "Pakisabi muli ang tamang code."
                )
            }

            reply = (
                otp_retry_messages.get(
                    lead.preferred_language,
                    otp_retry_messages[
                        "English"
                    ]
                )
            )

            session_manager.add_message(
                session_id,
                "assistant",
                reply
            )

            return reply

        # ------------------------------------------------------
        # Email
        # ------------------------------------------------------

        elif lead.email == "":

            extracted_email = (
                self.normalize_email(
                    user_message,
                )
            )

            if extracted_email:

                lead.email = extracted_email

            else:

                email_retry_messages = {

                    "English": (
                        "I want to make sure I have your email address correct. "
                        "Please say your email address again slowly. "
                        "For example, name at gmail dot com."
                    ),

                    "Hindi": (
                        "मैं आपका ईमेल पता सही तरीके से दर्ज करना चाहता हूँ। "
                        "कृपया अपना ईमेल पता फिर से धीरे-धीरे बोलें।"
                    ),

                    "Malayalam": (
                        "താങ്കളുടെ ഇമെയിൽ വിലാസം ശരിയായി രേഖപ്പെടുത്താൻ "
                        "ദയവായി ഇമെയിൽ വിലാസം വീണ്ടും പതുക്കെ പറയൂ."
                    ),

                    "Spanish": (
                        "Quiero asegurarme de que tengo correctamente "
                        "su correo electrónico. "
                        "Por favor, dígalo de nuevo lentamente."
                    ),

                    "Tagalog": (
                        "Gusto kong tiyaking tama ang iyong email address. "
                        "Pakisabi muli nang dahan-dahan ang iyong email address."
                    )
                }

                reply = (
                    email_retry_messages.get(
                        lead.preferred_language,
                        email_retry_messages[
                            "English"
                        ]
                    )
                )

                session_manager.add_message(
                    session_id,
                    "assistant",
                    reply
                )

                return reply

        # ------------------------------------------------------
        # Destination
        # ------------------------------------------------------

        elif lead.destination == "":

            lead.destination = user_message

        # ------------------------------------------------------
        # Travel date
        # ------------------------------------------------------

        elif lead.travel_date == "":

            lead.travel_date = user_message

        # ------------------------------------------------------
        # Travellers
        # ------------------------------------------------------

        elif lead.travellers == "":

            lead.travellers = (
                self.normalize_travellers(
                    user_message
                )
            )
            
            print(
                "TRAVELLERS NORMALIZED =",
                lead.travellers
            )
            
        # ------------------------------------------------------
        # Traveller type
        # ------------------------------------------------------

        elif lead.traveller_type == "":

            lead.traveller_type = (
                self.normalize_traveller_type(
                    user_message
                )
                
            )
            print(
                "TRAVELLER TYPE NORMALIZED =",
                lead.traveller_type
            )

        # ------------------------------------------------------
        # Children
        # ------------------------------------------------------

        elif lead.children_travelling == "":

            normalized_answer = (
                self.normalize_yes_no(
                    user_message
                )
            )
            
            lead.children_travelling = (
                normalized_answer
                if normalized_answer
                else user_message
            )

        # ------------------------------------------------------
        # Budget
        # ------------------------------------------------------

        elif lead.budget == "":

            lead.budget = user_message

            session = session_manager.get(
                session_id
            )

            if session is not None:

                session[
                    "package_recommendation_status"
                ] = "pending"

                session[
                    "package_recommendation"
                ] = ""

                session[
                    "package_recommendation_error"
                ] = ""

            package_wait_messages = {

                "English": (
                    "One moment while I find the most suitable package for you."
                ),

                "Spanish": (
                    "Un momento mientras encuentro el paquete más adecuado para usted."
                ),

                "Hindi": (
                    "एक क्षण रुकिए, मैं आपके लिए सबसे उपयुक्त पैकेज ढूंढ रहा हूँ।"
                ),

                "Malayalam": (
                    "ഒരു നിമിഷം, താങ്കൾക്ക് ഏറ്റവും അനുയോജ്യമായ പാക്കേജ് ഞാൻ കണ്ടെത്താം."
                ),

                "Tagalog": (
                    "Sandali lamang habang hinahanap ko ang pinakaangkop na package para sa iyo."
                )
            }

            reply = (
                package_wait_messages.get(
                    lead.preferred_language,
                    package_wait_messages[
                        "English"
                    ]
                )
            )

            session_manager.add_message(
                session_id,
                "assistant",
                reply
            )

            return reply

        # ------------------------------------------------------
        # Visa
        # ------------------------------------------------------

        elif lead.visa_required == "":

            normalized_answer = (
                self.normalize_yes_no(
                    user_message
                )
            )

            lead.visa_required = (
                normalized_answer
                if normalized_answer
                else user_message
            )

        # ------------------------------------------------------
        # Special requests
        # ------------------------------------------------------

        elif lead.special_requests == "":

            lead.special_requests = (
                user_message
            )

            # --------------------------------------------------
            # Normalize database fields.
            #
            # Translation failures are handled inside
            # safe_to_english(), so the booking can still finish.
            # --------------------------------------------------

            try:

                self.normalize_for_database(
                    lead
                )

            except Exception as exc:

                print(
                    "DATABASE NORMALIZATION ERROR:",
                    repr(exc)
                )

            lead_manager.complete_booking(
                lead
            )

            try:

                saved_lead_id = lead_repository.save(
                    lead
                )

                print(
                    "BOOKING SAVED SUCCESSFULLY:",
                    saved_lead_id
                )

            except Exception as exc:

                print(
                    "BOOKING DATABASE SAVE ERROR:",
                    repr(exc)
                )

                raise

            # --------------------------------------------------
            # Send company notification email.
            #
            # Failure here must not destroy the saved booking.
            # --------------------------------------------------

            try:

                email_sent = email_service.send_lead(
                    lead
                )

                if email_sent:

                    print(
                        "LEAD EMAIL SENT SUCCESSFULLY"
                    )

                else:

                    print(
                        "LEAD EMAIL NOT SENT"
                    )

            except Exception as exc:

                print(
                    "LEAD EMAIL ERROR:",
                    type(exc).__name__,
                    repr(exc)
                )

            # --------------------------------------------------
            # Final response
            # --------------------------------------------------

            try:

                final_reply = (
                    booking_manager.final_message(
                        lead
                    )
                )

            except Exception as exc:

                print(
                    "FINAL MESSAGE ERROR:",
                    repr(exc)
                )

                final_messages = {

                    "English": (
                        "Thank you. Your enquiry has been submitted successfully. "
                        "A Stanley Tours consultant will contact you shortly. "
                        "Thank you for choosing Stanley Tours."
                    ),

                    "Spanish": (
                        "Gracias. Su consulta ha sido enviada correctamente. "
                        "Un consultor de Stanley Tours se pondrá en contacto "
                        "con usted pronto. Gracias por elegir Stanley Tours."
                    ),

                    "Hindi": (
                        "धन्यवाद। आपकी जानकारी सफलतापूर्वक जमा हो गई है। "
                        "स्टैनली टूर्स का एक ट्रैवल कंसल्टेंट आपसे जल्द संपर्क करेगा। "
                        "स्टैनली टूर्स को चुनने के लिए धन्यवाद।"
                    ),

                    "Malayalam": (
                        "നന്ദി. താങ്കളുടെ അന്വേഷണം വിജയകരമായി സമർപ്പിച്ചു. "
                        "സ്റ്റാൻലി ടൂർസിലെ ഒരു ട്രാവൽ കൺസൾട്ടന്റ് "
                        "ഉടൻ താങ്കളെ ബന്ധപ്പെടും. നന്ദി."
                    ),

                    "Tagalog": (
                        "Salamat. Matagumpay na naisumite ang iyong inquiry. "
                        "Makikipag-ugnayan sa iyo ang isang Stanley Tours "
                        "consultant sa lalong madaling panahon. Salamat."
                    )
                }

                final_reply = (
                    final_messages.get(
                        lead.preferred_language,
                        final_messages[
                            "English"
                        ]
                    )
                )

            session_manager.add_message(
                session_id,
                "assistant",
                final_reply
            )

            return final_reply

        # ------------------------------------------------------
        # NEXT QUESTION
        #
        # This is critical.
        #
        # After country, name, email, destination, travel date,
        # travellers, traveller type, children, and visa are
        # successfully stored, execution reaches here and asks
        # the NEXT booking question.
        # ------------------------------------------------------

        reply = booking_manager.next_question(
            lead
        )

        if not reply:

            fallback_messages = {

                "English":
                    "Please continue with your booking details.",

                "Spanish":
                    "Por favor, continúe con los detalles de su reserva.",

                "Hindi":
                    "कृपया अपनी बुकिंग की जानकारी जारी रखें।",

                "Malayalam":
                    "ദയവായി ബുക്കിംഗ് വിവരങ്ങൾ തുടരൂ.",

                "Tagalog":
                    "Pakipagpatuloy ang mga detalye ng iyong booking."
            }

            reply = fallback_messages.get(
                lead.preferred_language,
                fallback_messages[
                    "English"
                ]
            )

        session_manager.add_message(
            session_id,
            "assistant",
            reply
        )

        return reply


handle_booking = HandleBooking()