SUPPORTED_LANGUAGES = [

    "english",

    "hindi",

    "malayalam",

    "tamil",

    "arabic",

    "spanish",

    "tagalog"
]


def is_language(message):

    return message.lower().strip() in SUPPORTED_LANGUAGES