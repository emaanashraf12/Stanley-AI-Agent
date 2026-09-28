class IntentDetector:

    BOOKING_KEYWORDS = [
        "book",
        "booking",
        "reserve",
        "reservation",
        "trip",
        "tour",
        "holiday",
        "vacation",
        "travel package",
        "book a trip",
        "book tour",
        "i want to travel",
        "i want to book",
        "i would like to travel",
        "plan my trip",
        "travel to",
        "visit"
    ]

    VISA_KEYWORDS = [
        "visa",
        "immigration",
        "passport",
        "embassy",
        "entry permit"
    ]

    GREETING_KEYWORDS = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    def detect(self, message):

        message = message.lower().strip()

        # Greeting
        if any(word in message for word in self.GREETING_KEYWORDS):
            return "greeting"

        # Visa
        if any(word in message for word in self.VISA_KEYWORDS):
            return "visa"

        # Booking
        if any(word in message for word in self.BOOKING_KEYWORDS):
            return "booking"

        return "general"


intent_detector = IntentDetector()