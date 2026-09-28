import re
import traceback

from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse

from backend.services.session_manager import session_manager
from backend.services.conversation_engine import conversation_engine
from backend.services.translation_service import translation_service
from backend.services.booking_manager import booking_manager
from backend.services.otp_service import otp_service
from backend.helpers.package_helper import recommend_packages


router = APIRouter()

# ==============================================================
# PACKAGE RECOMMENDATION
# ==============================================================

package_executor = ThreadPoolExecutor(
    max_workers=2
)


LANGUAGE_CODES = {
    "English": "en-US",
    "Spanish": "es-ES",
    "Hindi": "hi-IN",
    "Malayalam": "ml-IN",
    "Tagalog": "fil-PH"
}


MALAYALAM_TTS_VOICE = "Google.ml-IN-Wavenet-A"


def get_language_code(lead):

    language = str(
        lead.preferred_language or ""
    ).strip()

    language = re.sub(
        r"[.!?,;:]+$",
        "",
        language
    ).strip()

    for name, code in LANGUAGE_CODES.items():

        if language.lower() == name.lower():
            return code

    return "en-US"


def say_response(
    response,
    text,
    language_code
):

    if language_code == "ml-IN":

        response.say(
            text,
            language="ml-IN",
            voice=MALAYALAM_TTS_VOICE
        )

        return

    response.say(
        text,
        language=language_code
    )


def clean_simple_speech(text):

    if not text:
        return ""

    text = str(text).strip()

    text = re.sub(
        r"^[.!?,]+|[.!?,]+$",
        "",
        text
    ).strip()

    return text


def clean_otp_input(text):

    return otp_service.extract_digits(
        text,
        keep_plus=False
    )


def prepare_voice_input(
    session_id,
    user_message
):

    session = session_manager.get(
        session_id
    )

    if session is None:
        return user_message

    lead = session["lead"]

    cleaned = clean_simple_speech(
        user_message
    )

    # ----------------------------------------------------------
    # Language selection
    # ----------------------------------------------------------

    if (
        lead.booking_started
        and lead.preferred_language == ""
    ):

        language_text = cleaned.lower()

        if (
            "malayalam" in language_text
            or "malaya. l" in language_text
            or "malaya l" in language_text
            or "malaya" in language_text
        ):
            
            return "Malayalam"

        normalized_language = (
            translation_service.normalize_language(
                cleaned
            )
        )

        if normalized_language:

            return normalized_language

    # ----------------------------------------------------------
    # Country
    #
    # Do not alter it here.
    # booking_flow validates it.
    # ----------------------------------------------------------

    if (
        lead.booking_started
        and lead.preferred_language != ""
        and lead.country == ""
    ):

        return cleaned

    # ----------------------------------------------------------
    # Phone number
    # ----------------------------------------------------------

    if (
        lead.booking_started
        and lead.preferred_language != ""
        and lead.country != ""
        and lead.name != ""
        and lead.phone == ""
    ):

        phone = otp_service.extract_digits(
            user_message,
            keep_plus=True
        )

        if phone:

            print(
                "VOICE NORMALIZED PHONE =",
                phone
            )

            return phone

    # ----------------------------------------------------------
    # OTP
    # ----------------------------------------------------------

    if (
        lead.booking_started
        and lead.preferred_language != ""
        and lead.phone != ""
        and lead.phone_verified is False
        and lead.country != ""
        and lead.name != ""
    ):

        otp = clean_otp_input(
            user_message
        )

        if otp:
            return otp

    return user_message


def add_gather(
    response,
    session_id,
    language_code,
    lead=None
):

    speech_timeout = "auto"
    gather_timeout = 10
    gather_language = language_code
    
    # Detect when the agent is asking for the customer's name
    name_stage = (
        lead is not None
        and lead.booking_started
        and lead.preferred_language != ""
        and lead.country != ""
        and lead.name == ""
    )

    # Detect when the agent is asking for the customer's email
    email_stage = (
        lead is not None
        and lead.booking_started
        and lead.preferred_language != ""
        and lead.country != ""
        and lead.name != ""
        and lead.phone != ""
        and lead.phone_verified is True
        and lead.email == ""
    )   

    # Use English speech recognition only for name and email
    if name_stage or email_stage:
        gather_language = "en-US"
        speech_timeout = 5
        gather_timeout = 15

    phone_stage = (
        lead is not None
        and lead.booking_started
        and lead.preferred_language != ""
        and lead.country != ""
        and lead.name != ""
        and lead.phone == ""
    )

    otp_stage = (
        lead is not None
        and lead.booking_started
        and lead.preferred_language != ""
        and lead.country != ""
        and lead.name != ""
        and lead.phone != ""
        and lead.phone_verified is False
    )
    
    destination_stage = (
        lead is not None
        and lead.booking_started
        and lead.preferred_language != ""
        and lead.country != ""
        and lead.name != ""
        and lead.phone != ""
        and lead.phone_verified is True
        and lead.email != ""
        and lead.destination == ""
    )

    # ----------------------------------------------------------
    # Phone number collection
    # ----------------------------------------------------------

    if phone_stage:

        speech_timeout = 5
        gather_timeout = 15
        
        session = session_manager.get(
            session_id
        )

        # Use English STT only while collecting phone numbers
        # for Malayalam conversations.
        #
        # TTS and the rest of the conversation remain in the
        # customer's selected language.

        if language_code == "ml-IN":
            gather_language = "en-US"
            speech_timeout = 8
            
        # Spanish phone:
        # first allow English number words such as
        # "nine two three..."
        # then native Spanish on retry
        elif language_code == "es-ES":

            phone_language = "en-US"

            if session is not None:

                phone_language = session.get(
                    "spanish_phone_language",
                    "en-US"
                )

            gather_language = phone_language

        # Tagalog phone:
        # first allow English number words such as
        # "nine two three..."
        # then native Tagalog on retry
        elif language_code == "fil-PH":

            phone_language = "en-US"

            if session is not None:

                phone_language = session.get(
                    "tagalog_phone_language",
                    "en-US"
                )

            gather_language = phone_language

    # Use English speech recognition only for destination names.
    # The agent still SPEAKS in the customer's selected language.
    if destination_stage:
        gather_language = "en-US"
    
    gather_kwargs = {
        "input": "speech",
        "action": f"/voice/process?session_id={session_id}",
        "method": "POST",
        "language": gather_language,
        "speechTimeout": speech_timeout,
        "timeout": gather_timeout,
        "actionOnEmptyResult": True
    }
    
    # ----------------------------------------------------------
    # NAME: strongest possible STT, no re-ask
    # ----------------------------------------------------------
    if name_stage:
        gather_kwargs["speechModel"] = "phone_call"
        gather_kwargs["enhanced"] = "true"
        gather_kwargs["speechTimeout"] = 5
        gather_kwargs["timeout"] = 15
        # Letters help if user spells; common name hints help if they don't
        gather_kwargs["hints"] = (
            "a b c d e f g h i j k l m n o p q r s t u v w x y z "
            "mohamed muhammad ahmed ali khan smith john mary "
            "jose maria juan ana carlos"
        )

    # ----------------------------------------------------------
    # EMAIL: strongest STT + full domain/symbol hints
    # ----------------------------------------------------------
    if email_stage:
        gather_kwargs["speechModel"] = "phone_call"
        gather_kwargs["enhanced"] = "true"
        gather_kwargs["speechTimeout"] = 5
        gather_kwargs["timeout"] = 15
        gather_kwargs["hints"] = (
            "at atsign attheRate dot period underscore hyphen dash "
            "gmail gmail.com yahoo yahoo.com outlook outlook.com "
            "hotmail hotmail.com icloud icloud.com protonmail "
            "a b c d e f g h i j k l m n o p q r s t u v w x y z"
        )
    
    # Malayalam phone number recognition
    if phone_stage and language_code == "ml-IN":
        gather_kwargs["speechModel"] = "numbers_and_commands"
        gather_kwargs["hints"] = (
            "zero, oh, one, two, three, four, five, "
            "six, seven, eight, nine, plus"
        )
    
    if (
        phone_stage
        and language_code == "ml-IN"
    ):
        gather_kwargs["input"] = "dtmf speech"

    # ----------------------------------------------------------
    # OTP collection
    # ----------------------------------------------------------

    if otp_stage:

        gather_kwargs["speechTimeout"] = 5
        gather_kwargs["timeout"] = 15

        if language_code == "ml-IN":

            gather_kwargs["input"] = "dtmf speech"
            gather_kwargs["numDigits"] = 6

            session = session_manager.get(
                session_id
            )

            otp_language = "en-US"

            if session is not None:
                otp_language = session.get(
                    "malayalam_otp_language",
                    "en-US"
                )

            gather_kwargs["language"] = otp_language

        elif language_code == "fil-PH":

            gather_kwargs["input"] = "speech"

            session = session_manager.get(
                session_id
            )

            otp_language = "en-US"

            if session is not None:
                otp_language = session.get(
                    "tagalog_otp_language",
                    "en-US"
                )

            gather_kwargs["language"] = otp_language

        else:

            # Keep the existing working behaviour for English,
            # Spanish, Hindi, and Tagalog.
            gather_kwargs["input"] = "dtmf speech"
            gather_kwargs["numDigits"] = 6

    response.gather(
        **gather_kwargs
    )


# ==============================================================
# PACKAGE RECOMMENDATION
# ==============================================================

def generate_package_recommendation(
    session_id
):

    session = session_manager.get(
        session_id
    )

    if session is None:
        return

    lead = session["lead"]

    try:

        print(
            "========== PACKAGE RECOMMENDATION START =========="
        )

        package_reply = recommend_packages(
            lead
        )

        session = session_manager.get(
            session_id
        )

        if session is None:
            return

        session[
            "package_recommendation"
        ] = package_reply or ""

        session[
            "package_recommendation_status"
        ] = "completed"

        print(
            "========== PACKAGE RECOMMENDATION COMPLETE =========="
        )

        print(
            "PACKAGE REPLY =",
            package_reply
        )

    except Exception as exc:

        print(
            "========== PACKAGE RECOMMENDATION ERROR =========="
        )

        print(
            repr(exc)
        )

        traceback.print_exc()

        session = session_manager.get(
            session_id
        )

        if session is None:
            return

        session[
            "package_recommendation"
        ] = ""

        session[
            "package_recommendation_error"
        ] = repr(exc)

        session[
            "package_recommendation_status"
        ] = "failed"


def start_package_recommendation(
    session_id
):

    session = session_manager.get(
        session_id
    )

    if session is None:
        return

    status = session.get(
        "package_recommendation_status",
        "idle"
    )

    if status != "pending":
        return

    # Mark it running before starting the thread.
    # This prevents duplicate Twilio requests
    # from starting the recommendation twice.

    session[
        "package_recommendation_status"
    ] = "running"

    package_executor.submit(
        generate_package_recommendation,
        session_id
    )


def technical_error_response(
    language_code="en-US"
):

    messages = {

        "en-US": (
            "Sorry, we are having a temporary technical problem. "
            "Please call us again in a moment."
        ),

        "es-ES": (
            "Lo sentimos, tenemos un problema técnico temporal. "
            "Por favor, vuelva a llamarnos en un momento."
        ),

        "hi-IN": (
            "क्षमा करें, अभी एक अस्थायी तकनीकी समस्या है। "
            "कृपया थोड़ी देर बाद फिर से कॉल करें।"
        ),

        "ml-IN": (
            "ക്ഷമിക്കണം, ഇപ്പോൾ ഒരു താൽക്കാലിക സാങ്കേതിക പ്രശ്നമുണ്ട്. "
            "ദയവായി കുറച്ച് സമയത്തിന് ശേഷം വീണ്ടും വിളിക്കൂ."
        ),

        "fil-PH": (
            "Paumanhin, may pansamantalang teknikal na problema. "
            "Pakatawag muli pagkalipas ng ilang sandali."
        )
    }

    response = VoiceResponse()

    say_response(
        response,
        messages.get(
            language_code,
            messages["en-US"]
        ),
        language_code
    )

    response.hangup()

    return Response(
        content=str(response),
        media_type="application/xml",
        status_code=200
    )


@router.api_route(
    "/voice",
    methods=["GET", "POST"]
)
async def incoming_call():

    try:

        print(
            "========== INCOMING TWILIO CALL =========="
        )

        session_id = (
            session_manager.create_session()
        )

        reply = conversation_engine.process(
            session_id,
            "hello"
        )

        session = session_manager.get(
            session_id
        )

        lead = session["lead"]

        response = VoiceResponse()

        language_code = get_language_code(
            lead
        )

        say_response(
            response,
            reply,
            language_code
        )

        add_gather(
            response,
            session_id,
            language_code,
            lead
        )

        twiml = str(
            response
        )

        print(
            "========== TWIML RESPONSE =========="
        )

        print(
            twiml
        )

        return Response(
            content=twiml,
            media_type="application/xml"
        )

    except Exception:

        print(
            "========== VOICE START ERROR =========="
        )

        traceback.print_exc()

        return technical_error_response(
            "en-US"
        )


@router.post(
    "/voice/process"
)
async def process_voice(
    request: Request,
    session_id: str
):

    language_code = "en-US"

    try:

        form = await request.form()

        # ------------------------------------------------------
        # NORMAL SPEECH INPUT
        #
        # SpeechResult remains the default for every normal field.
        # This preserves email and every other booking answer.
        # ------------------------------------------------------

        speech_input = form.get(
            "SpeechResult",
            ""
        )

        digits_input = form.get(
            "Digits",
            ""
        )

        user_message = speech_input

        response = VoiceResponse()

        session = session_manager.get(
            session_id
        )

        if session is None:

            say_response(
                response,
                "Sorry, your session has expired. Please call us again.",
                "en-US"
            )

            response.hangup()

            return Response(
                content=str(response),
                media_type="application/xml"
            )

        lead = session["lead"]

        language_code = get_language_code(
            lead
        )
        
        malayalam_phone_stage = (
            lead.booking_started
            and lead.preferred_language == "Malayalam"
            and lead.country != ""
            and lead.name != ""
            and lead.phone == ""
        )

        # ------------------------------------------------------
        # DTMF is allowed ONLY while waiting for OTP.
        #
        # This prevents keypad input from affecting email or
        # any other normal booking field.
        # ------------------------------------------------------

        otp_stage = (
            lead.booking_started
            and lead.preferred_language != ""
            and lead.country != ""
            and lead.name != ""
            and lead.phone != ""
            and lead.phone_verified is False
        )

        if (
            (otp_stage or malayalam_phone_stage)
            and digits_input
        ):

            user_message = digits_input

        if not user_message:

            retry_messages = {

                "en-US": (
                    "Sorry, I did not hear that. "
                    "Please try again."
                ),

                "es-ES": (
                    "Lo siento, no pude escucharle. "
                    "Por favor, inténtelo de nuevo."
                ),

                "hi-IN": (
                    "माफ़ कीजिए, मैं आपकी बात नहीं सुन पाया। "
                    "कृपया फिर से बोलें।"
                ),

                "ml-IN": (
                    "ക്ഷമിക്കണം, എനിക്ക് അത് കേൾക്കാനായില്ല. "
                    "ദയവായി വീണ്ടും പറയൂ."
                ),

                "fil-PH": (
                    "Paumanhin, hindi ko iyon narinig. "
                    "Pakisabi muli."
                )
            }

            say_response(
                response,
                retry_messages.get(
                    language_code,
                    retry_messages["en-US"]
                ),
                language_code
            )

            add_gather(
                response,
                session_id,
                language_code,
                lead
            )

            return Response(
                content=str(response),
                media_type="application/xml"
            )

        original_message = user_message

        user_message = prepare_voice_input(
            session_id,
            user_message
        )

        print(
            "========== VOICE INPUT =========="
        )

        print(
            "SESSION ID =",
            session_id
        )

        print(
            "RAW USER =",
            original_message
        )

        print(
            "PROCESSED USER =",
            user_message
        )

        # ------------------------------------------------------
        # OTP safety check
        # ------------------------------------------------------

        if (
            lead.booking_started
            and lead.preferred_language != ""
            and lead.country != ""
            and lead.name != ""
            and lead.phone != ""
            and lead.phone_verified is False
        ):

            otp_digits = clean_otp_input(
                user_message
            )

            print(
                "VOICE OTP DIGITS =",
                otp_digits
            )

            print(
                "VOICE OTP DIGIT COUNT =",
                len(otp_digits)
            )

            if len(otp_digits) != 6:
                
                # Malayalam OTP only:
                # alternate STT between English and Malayalam
                if lead.preferred_language == "Malayalam":
                    
                    session = session_manager.get(session_id)

                    if session is not None:

                        current_otp_language = session.get(
                            "malayalam_otp_language",
                            "en-US"
                        )

                        if current_otp_language == "en-US":
                            session["malayalam_otp_language"] = "ml-IN"
                            
                        else:
                            session["malayalam_otp_language"] = "en-US"
                            
                # Spanish
                elif lead.preferred_language == "Spanish":

                    current_otp_language = session.get(
                        "spanish_otp_language",
                        "en-US"
                    )

                    if current_otp_language == "en-US":

                        session[
                            "spanish_otp_language"
                        ] = "es-ES"

                    else:

                        session[
                            "spanish_otp_language"
                        ] = "en-US"

                # Tagalog       
                elif lead.preferred_language == "Tagalog":

                    current_otp_language = session.get(
                        "tagalog_otp_language",
                        "en-US"
                    )

                    if current_otp_language == "en-US":

                        session[
                            "tagalog_otp_language"
                        ] = "fil-PH"

                    else:

                        session[
                            "tagalog_otp_language"
                        ] = "en-US"

                otp_retry_messages = {

                    "en-US": (
                        "I did not receive all six digits. "
                        "Please say the six digit verification code again, "
                        "or enter the six digits using your phone keypad."
                    ),

                    "es-ES": (
                        "No recibí los seis dígitos completos. "
                        "Por favor, diga nuevamente el código de seis dígitos "
                        "o introdúzcalo usando el teclado de su teléfono."
                    ),

                    "hi-IN": (
                        "मुझे सभी छह अंक प्राप्त नहीं हुए। "
                        "कृपया छह अंकों का सत्यापन कोड फिर से बोलें, "
                        "या अपने फोन के कीपैड से छह अंक दर्ज करें।"
                    ),

                    "ml-IN": (
                        "ആറ് അക്കങ്ങളും ലഭിച്ചില്ല. "
                        "ദയവായി ആറ് അക്ക സ്ഥിരീകരണ കോഡ് വീണ്ടും പറയുക, "
                        "അല്ലെങ്കിൽ ഫോൺ കീപാഡ് ഉപയോഗിച്ച് ആറ് അക്കങ്ങളും നൽകുക."
                    ),

                    "fil-PH": (
                        "Hindi ko natanggap ang kumpletong anim na digit. "
                        "Pakisabi muli ang anim na digit na verification code "
                        "o ilagay ang anim na digit gamit ang keypad ng iyong telepono."
                    )
                }

                say_response(
                    response,
                    otp_retry_messages.get(
                        language_code,
                        otp_retry_messages["en-US"]
                    ),
                    language_code
                )

                add_gather(
                    response,
                    session_id,
                    language_code,
                    lead
                )

                return Response(
                    content=str(response),
                    media_type="application/xml"
                )

            user_message = otp_digits

        reply = conversation_engine.process(
            session_id,
            user_message
        )

        print(
            "ASSISTANT =",
            reply
        )

        session = session_manager.get(
            session_id
        )

        if session is None:

            say_response(
                response,
                "Sorry, your session has expired. Please call us again.",
                "en-US"
            )

            response.hangup()

            return Response(
                content=str(response),
                media_type="application/xml"
            )

        lead = session["lead"]

        language_code = get_language_code(
            lead
        )

        # ======================================================
        # PACKAGE RECOMMENDATION
        # ======================================================

        package_status = session.get(
            "package_recommendation_status",
            "idle"
        )

        if package_status == "pending":

            start_package_recommendation(
                session_id
            )

            if reply:

                say_response(
                    response,
                    reply,
                    language_code
                )

            response.pause(
                length=2
            )

            response.redirect(
                f"/voice/recommendation-status?session_id={session_id}",
                method="POST"
            )

            return Response(
                content=str(response),
                media_type="application/xml"
            )

        if reply:

            say_response(
                response,
                reply,
                language_code
            )

        if lead.booking_completed:

            response.hangup()

            return Response(
                content=str(response),
                media_type="application/xml"
            )

        add_gather(
            response,
            session_id,
            language_code,
            lead
        )

        return Response(
            content=str(response),
            media_type="application/xml"
        )

    except Exception:

        print(
            "========== VOICE PROCESS ERROR =========="
        )

        print(
            "SESSION ID =",
            session_id
        )

        traceback.print_exc()

        return technical_error_response(
            language_code
        )


# ==============================================================
# PACKAGE RECOMMENDATION STATUS
# ==============================================================

@router.api_route(
    "/voice/recommendation-status",
    methods=["GET", "POST"]
)
async def recommendation_status(
    session_id: str
):

    language_code = "en-US"

    try:

        session = session_manager.get(
            session_id
        )

        response = VoiceResponse()

        if session is None:

            say_response(
                response,
                "Sorry, your session has expired. Please call us again.",
                "en-US"
            )

            response.hangup()

            return Response(
                content=str(response),
                media_type="application/xml"
            )

        lead = session["lead"]

        language_code = get_language_code(
            lead
        )

        status = session.get(
            "package_recommendation_status",
            "idle"
        )

        print(
            "PACKAGE STATUS =",
            status
        )

        # ------------------------------------------------------
        # Recommendation is still being generated
        # ------------------------------------------------------

        if status in (
            "pending",
            "running"
        ):

            response.pause(
                length=2
            )

            response.redirect(
                f"/voice/recommendation-status?session_id={session_id}",
                method="POST"
            )

            return Response(
                content=str(response),
                media_type="application/xml"
            )

        # ------------------------------------------------------
        # Recommendation completed
        # ------------------------------------------------------

        package_reply = session.get(
            "package_recommendation",
            ""
        )

        if (
            status == "completed"
            and package_reply
        ):

            say_response(
                response,
                package_reply,
                language_code
            )

            session_manager.add_message(
                session_id,
                "assistant",
                package_reply
            )

        # ------------------------------------------------------
        # Recommendation failed
        # ------------------------------------------------------

        elif status == "failed":

            fallback_messages = {

                "English": (
                    "I could not load the package recommendation right now. "
                    "A Stanley Tours consultant can still help you choose "
                    "the most suitable package."
                ),

                "Spanish": (
                    "No pude cargar la recomendación del paquete en este momento. "
                    "Un consultor de Stanley Tours puede ayudarle a elegir "
                    "el paquete más adecuado."
                ),

                "Hindi": (
                    "मैं अभी पैकेज की सिफारिश लोड नहीं कर पाया। "
                    "स्टैनली टूर्स का एक कंसल्टेंट आपके लिए "
                    "सबसे उपयुक्त पैकेज चुनने में मदद करेगा।"
                ),

                "Malayalam": (
                    "ഇപ്പോൾ പാക്കേജ് ശുപാർശ ലഭ്യമാക്കാൻ കഴിഞ്ഞില്ല. "
                    "സ്റ്റാൻലി ടൂർസിലെ ഒരു കൺസൾട്ടന്റ് താങ്കൾക്ക് "
                    "ഏറ്റവും അനുയോജ്യമായ പാക്കേജ് തിരഞ്ഞെടുക്കാൻ സഹായിക്കും."
                ),

                "Tagalog": (
                    "Hindi ko ma-load ang package recommendation sa ngayon. "
                    "Matutulungan ka ng isang Stanley Tours consultant "
                    "na pumili ng pinakaangkop na package."
                )
            }

            fallback_reply = fallback_messages.get(
                lead.preferred_language,
                fallback_messages["English"]
            )

            say_response(
                response,
                fallback_reply,
                language_code
            )

            session_manager.add_message(
                session_id,
                "assistant",
                fallback_reply
            )

        # ------------------------------------------------------
        # Mark recommendation as delivered
        # ------------------------------------------------------

        session[
            "package_recommendation_status"
        ] = "delivered"

        # ------------------------------------------------------
        # Continue normal booking flow
        # ------------------------------------------------------

        next_question = booking_manager.next_question(
            lead
        )

        if next_question:

            say_response(
                response,
                next_question,
                language_code
            )

            session_manager.add_message(
                session_id,
                "assistant",
                next_question
            )

        add_gather(
            response,
            session_id,
            language_code,
            lead
        )

        return Response(
            content=str(response),
            media_type="application/xml"
        )

    except Exception:

        print(
            "========== PACKAGE STATUS ERROR =========="
        )

        print(
            "SESSION ID =",
            session_id
        )

        traceback.print_exc()

        return technical_error_response(
            language_code
        )