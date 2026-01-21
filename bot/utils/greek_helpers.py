"""Greek language utilities."""

# Greek definite articles (singular and plural)
GREEK_ARTICLES = {"ο", "η", "το", "οι", "τα"}


def has_greek_article(text: str) -> bool:
    """Check if Greek text starts with a definite article.

    Args:
        text: Greek text

    Returns:
        True if text starts with a Greek article
    """
    words = text.strip().split()
    if words:
        return words[0].lower() in GREEK_ARTICLES
    return False


def get_article_gender(text: str) -> str | None:
    """Get the grammatical gender based on the article.

    Args:
        text: Greek text starting with article

    Returns:
        Gender string or None if no article found
    """
    words = text.strip().split()
    if not words:
        return None

    first_word = words[0].lower()
    if first_word == "ο":
        return "masculine"
    elif first_word == "η":
        return "feminine"
    elif first_word == "το":
        return "neuter"
    elif first_word == "οι":
        return "masculine_plural"
    elif first_word == "τα":
        return "neuter_plural"
    return None


def get_gender_label_russian(text: str) -> str:
    """Get Russian gender label based on Greek article.

    Args:
        text: Greek text starting with article

    Returns:
        Russian gender abbreviation or empty string
    """
    gender = get_article_gender(text)
    if gender == "masculine":
        return " (м.р.)"
    elif gender == "feminine":
        return " (ж.р.)"
    elif gender == "neuter":
        return " (ср.р.)"
    elif gender == "masculine_plural":
        return " (мн.ч.)"
    elif gender == "neuter_plural":
        return " (мн.ч.)"
    return ""
