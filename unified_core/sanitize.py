import re

# Remueve surrogate pairs ilegales (UTF-16 huérfanos)
BAD_CHARS = re.compile(r'[\ud800-\udfff]')

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    return BAD_CHARS.sub("", text)


def sanitize(obj):
    """
    Recorrido recursivo: limpia strings dentro de dicts, lists, tuples.
    """
    if isinstance(obj, dict):
        return {sanitize(k): sanitize(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [sanitize(x) for x in obj]

    if isinstance(obj, tuple):
        return tuple(sanitize(list(obj)))

    if isinstance(obj, str):
        return clean_text(obj)

    return obj
