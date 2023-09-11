config = {
    "API_URL": "https://talnet.instructure.com",
    "API_KEY": "17601~V6FUc7Xvc07XkCMxJtDVJlpN7RiugCbaodIJ6pUzfnxTZ7S44eRs7yGW7jKc0hOO",
    "default_feedback_pos": [
        "Top gedaan!",
        "Nice One!",
        "Netjes",
        "Goed gedaan",
        "Top!",
        "Top!",
        "Goed zo!",
        "Gaat goed zo!",
        "Top!",
    ],
    "default_feedback_neg": ["Niet helemaal goed"],
    "defaults": [
        {
            "short": "Aantal bijlagen",
            "value": "Het aantal bijlage klopt niet.",
        },
        {"short": "Naam bijlagen", "value": "De naamgeving van de bijlage klopt niet."},
        {
            "short": "Verkeerde bijlage",
            "value": "De bijlage hoort niet bij de opdracht",
        },
        {
            "short": "Feedback niet verwerkt",
            "value": "De vorige feedback is niet verwerkt",
        },
        {
            "short": "Incomplete browser",
            "value": "Screenshot is niet van complete browser; URL mist bijvoorbeeld.",
        },
    ],
    "TEST": False,
}


def testdata():
    print("OK")
