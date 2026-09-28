GENERAL_KEYWORDS = [

    "company",

    "about",

    "office",

    "business",

    "services",

    "visa",

    "payment",

    "refund",

    "cancel",

    "location",

    "head office",

    "working hours"
]


def is_general_question(message):

    message = message.lower()

    return any(

        keyword in message

        for keyword in GENERAL_KEYWORDS

    )