import re

import phonenumbers
from phonenumbers import NumberParseException
from twilio.rest import Client

from backend.apps.config import settings


class OTPService:

    def __init__(self):

        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

    # ==========================================================
    # SPOKEN NUMBER NORMALIZATION
    # ==========================================================

    NUMBER_WORDS = {

        # English
        "zero": "0",
        "oh": "0",
        "o": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",

        # Common Hindi number words
        "शून्य": "0",
        "जीरो": "0",
        "ज़ीरो": "0",

        "एक": "1",
        "वन": "1",

        "दो": "2",
        "टू": "2",

        "तीन": "3",
        "थ्री": "3",

        "चार": "4",
        "फोर": "4",

        "पांच": "5",
        "पाँच": "5",
        "फाइव": "5",

        "छह": "6",
        "छः": "6",
        "सिक्स": "6",

        "सात": "7",
        "सेवन": "7",

        "आठ": "8",
        "एट": "8",

        "नौ": "9",
        "नाइन": "9",

        # Malayalam number words
        "പൂജ്യം": "0",
        "സീറോ": "0",

        "ഒന്ന്": "1",
        "ഒന്നു": "1",
        "വൺ": "1",
        "വണ്": "1",

        "രണ്ട്": "2",
        "രണ്ടു": "2",
        "ടൂ": "2",
        "ടു": "2",

        "മൂന്ന്": "3",
        "മൂന്നു": "3",
        "ത്രീ": "3",
        "ത്രി": "3",

        "നാല്": "4",
        "നാലു": "4",
        "ഫോർ": "4",
        "ഫോര്": "4",

        "അഞ്ച്": "5",
        "അഞ്ചു": "5",
        "ഫൈവ്": "5",

        "ആറ്": "6",
        "ആറു": "6",
        "സിക്സ്": "6",
        "സെക്സ്": "6",

        "ഏഴ്": "7",
        "ഏഴു": "7",
        "സെവൻ": "7",
        "സെവന്": "7",

        "എട്ട്": "8",
        "എട്ടു": "8",
        "എയ്റ്റ്": "8",
        "എയിറ്റ്": "8",

        "ഒൻപത്": "9",
        "ഒമ്പത്": "9",
        "നൈൻ": "9",
        "നൈന്": "9",
        "നയൻ": "9",
        "നയന്": "9",

        # Spanish number words
        "cero": "0",
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

        # Tagalog number words
        "sero": "0",
        "siro": "0",
        "isa": "1",
        "dalawa": "2",
        "tatlo": "3",
        "apat": "4",
        "lima": "5",
        "anim": "6",
        "pito": "7",
        "walo": "8",
        "siyam": "9"
    }

    def normalize_spoken_digits(self, text):

        if not text:
            return ""

        text = str(text).strip().lower()

        text = text.translate(
            str.maketrans({

                # Hindi / Devanagari digits
                "०": "0",
                "१": "1",
                "२": "2",
                "३": "3",
                "४": "4",
                "५": "5",
                "६": "6",
                "७": "7",
                "८": "8",
                "९": "9",

                # Malayalam digits
                "൦": "0",
                "൧": "1",
                "൨": "2",
                "൩": "3",
                "൪": "4",
                "൫": "5",
                "൬": "6",
                "൭": "7",
                "൮": "8",
                "൯": "9",

                # Arabic-Indic digits
                "٠": "0",
                "١": "1",
                "٢": "2",
                "٣": "3",
                "٤": "4",
                "٥": "5",
                "٦": "6",
                "٧": "7",
                "٨": "8",
                "٩": "9"
            })
        )

        plus_words = [

            # English
            "positive",
            "plus",

            # Hindi
            "पॉजिटिव",
            "पोजिटिव",
            "प्लस",

            # Malayalam
            "പ്ലസ്",
            "പോസിറ്റീവ്",

            # Spanish
            "más",
            "mas",
            "positivo",
            "positiva",

            # Tagalog
            "positibo"
        ]

        for word in sorted(
            plus_words,
            key=len,
            reverse=True
        ):

            text = re.sub(
                rf"(?<!\w){re.escape(word)}(?!\w)",
                "plus",
                text,
                flags=re.IGNORECASE
            )

        for word in sorted(
            self.NUMBER_WORDS,
            key=len,
            reverse=True
        ):

            replacement = self.NUMBER_WORDS[word]

            text = re.sub(
                rf"(?<!\w){re.escape(word)}(?!\w)",
                replacement,
                text,
                flags=re.IGNORECASE
            )

        return text

    def extract_digits(
        self,
        text,
        keep_plus=False
    ):

        if not text:
            return ""

        normalized = self.normalize_spoken_digits(
            text
        )

        normalized = str(
            normalized
        ).strip()

        plus_found = (
            normalized.startswith("+")
            or
            normalized.startswith("plus")
        )

        digits = re.sub(
            r"\D",
            "",
            normalized
        )

        if not digits:
            return ""

        if (
            keep_plus
            and plus_found
        ):

            return "+" + digits

        return digits

    # ==========================================================
    # PHONE NORMALIZATION
    # ==========================================================

    def normalize_phone(self, phone, country):

        if not phone:
            return None

        phone = self.extract_digits(
            phone,
            keep_plus=True
        )

        if not phone:
            return None

        try:

            # --------------------------------------------------
            # Already international number with +
            # --------------------------------------------------

            if phone.startswith("+"):

                parsed = phonenumbers.parse(
                    phone,
                    None
                )

                if (
                    phonenumbers.is_possible_number(parsed)
                    and phonenumbers.is_valid_number(parsed)
                ):

                    return phonenumbers.format_number(
                        parsed,
                        phonenumbers.PhoneNumberFormat.E164
                    )

                return None

            # --------------------------------------------------
            # Number without +.
            #
            # First try it as an international number.
            # --------------------------------------------------

            international_candidate = "+" + phone

            try:

                parsed_international = phonenumbers.parse(
                    international_candidate,
                    None
                )

                if (
                    phonenumbers.is_possible_number(
                        parsed_international
                    )
                    and
                    phonenumbers.is_valid_number(
                        parsed_international
                    )
                ):

                    return phonenumbers.format_number(
                        parsed_international,
                        phonenumbers.PhoneNumberFormat.E164
                    )

            except NumberParseException:
                pass

            # --------------------------------------------------
            # If that failed, treat it as a local number using
            # the customer's country.
            # --------------------------------------------------

            region = self.country_to_region(
                country
            )

            if not region:

                print(
                    "OTP ERROR: Could not determine country region:",
                    country
                )

                return None

            parsed_local = phonenumbers.parse(
                phone,
                region
            )

            if not phonenumbers.is_possible_number(
                parsed_local
            ):

                print(
                    "OTP ERROR: Phone number is not possible:",
                    phone
                )

                return None

            if not phonenumbers.is_valid_number(
                parsed_local
            ):

                print(
                    "OTP ERROR: Phone number is not valid:",
                    phone
                )

                return None

            return phonenumbers.format_number(
                parsed_local,
                phonenumbers.PhoneNumberFormat.E164
            )

        except NumberParseException as e:

            print(
                "OTP ERROR: Could not parse phone number:",
                phone,
                "Error:",
                e
            )

            return None

    # ==========================================================
    # COUNTRY -> REGION
    # ==========================================================

    def country_to_region(self, country):

        if not country:
            return None

        country = str(
            country
        ).strip().lower()

        country = re.sub(
            r"[.!?,;:]+$",
            "",
            country
        ).strip()

        country_map = {

            "pakistan": "PK",
            "pk": "PK",

            "india": "IN",
            "in": "IN",

            "bangladesh": "BD",
            "bd": "BD",

            "sri lanka": "LK",
            "srilanka": "LK",
            "lk": "LK",

            "nepal": "NP",
            "np": "NP",

            "united states": "US",
            "united states of america": "US",
            "usa": "US",
            "u.s.a": "US",
            "u.s.a.": "US",
            "us": "US",
            "u.s": "US",
            "u.s.": "US",
            "america": "US",

            "canada": "CA",
            "ca": "CA",

            "mexico": "MX",

            "united kingdom": "GB",
            "uk": "GB",
            "u.k": "GB",
            "u.k.": "GB",
            "england": "GB",
            "scotland": "GB",
            "wales": "GB",

            "ireland": "IE",

            "france": "FR",
            "germany": "DE",
            "spain": "ES",
            "italy": "IT",
            "portugal": "PT",
            "netherlands": "NL",
            "holland": "NL",
            "belgium": "BE",
            "switzerland": "CH",
            "austria": "AT",
            "sweden": "SE",
            "norway": "NO",
            "denmark": "DK",
            "finland": "FI",
            "iceland": "IS",
            "poland": "PL",
            "greece": "GR",
            "romania": "RO",
            "ukraine": "UA",
            "turkey": "TR",

            "united arab emirates": "AE",
            "uae": "AE",

            "saudi arabia": "SA",
            "saudi": "SA",

            "qatar": "QA",
            "kuwait": "KW",
            "bahrain": "BH",
            "oman": "OM",
            "jordan": "JO",
            "israel": "IL",
            "egypt": "EG",

            "philippines": "PH",
            "the philippines": "PH",

            "singapore": "SG",
            "malaysia": "MY",
            "indonesia": "ID",
            "thailand": "TH",
            "vietnam": "VN",
            "japan": "JP",
            "south korea": "KR",
            "korea": "KR",
            "china": "CN",
            "hong kong": "HK",
            "taiwan": "TW",

            "australia": "AU",
            "new zealand": "NZ",
            "fiji": "FJ",

            "south africa": "ZA",
            "kenya": "KE",
            "nigeria": "NG",
            "morocco": "MA",
            "ghana": "GH",
            "tanzania": "TZ",

            "brazil": "BR",
            "argentina": "AR",
            "chile": "CL",
            "colombia": "CO",
            "peru": "PE",
            "cuba": "CU",
            "jamaica": "JM",
            "dominican republic": "DO",
            "costa rica": "CR"
        }

        return country_map.get(
            country
        )

    # ==========================================================
    # SEND OTP
    # ==========================================================

    def send_otp(self, lead):

        normalized_phone = self.normalize_phone(
            lead.phone,
            lead.country
        )

        if not normalized_phone:

            print(
                "OTP ERROR: Invalid phone number:",
                lead.phone,
                "Country:",
                lead.country
            )

            return False

        lead.phone = normalized_phone

        print(
            "NORMALIZED PHONE =",
            lead.phone
        )

        try:

            verification = (
                self.client
                .verify
                .v2
                .services(
                    settings.TWILIO_VERIFY_SERVICE_SID
                )
                .verifications
                .create(
                    to=lead.phone,
                    channel="sms"
                )
            )

            print(
                "OTP sent to:",
                lead.phone,
                "Status:",
                verification.status
            )

            return (
                verification.status
                == "pending"
            )

        except Exception as e:

            print(
                "OTP Error:",
                e
            )

            return False

    # ==========================================================
    # VERIFY OTP
    # ==========================================================

    def verify(
        self,
        lead,
        otp
    ):

        if not lead.phone:

            print(
                "OTP Verification Error: No phone number stored."
            )

            return False

        otp_digits = self.extract_digits(
            otp,
            keep_plus=False
        )

        print(
            "NORMALIZED OTP =",
            otp_digits
        )

        print(
            "OTP DIGIT COUNT =",
            len(otp_digits)
        )

        if len(otp_digits) != 6:

            print(
                "OTP Verification Error: Expected 6 digits but received:",
                len(otp_digits)
            )

            return False

        try:

            verification = (
                self.client
                .verify
                .v2
                .services(
                    settings.TWILIO_VERIFY_SERVICE_SID
                )
                .verification_checks
                .create(
                    to=lead.phone,
                    code=otp_digits
                )
            )

            print(
                "TWILIO OTP STATUS =",
                verification.status
            )

            return (
                verification.status
                == "approved"
            )

        except Exception as e:

            print(
                "OTP Verification Error:",
                e
            )

            return False


otp_service = OTPService()