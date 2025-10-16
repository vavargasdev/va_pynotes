import re
import unicodedata


def sanitize_text(text):
    """
    Sanitizes a string to be used in a filename.
    Removes accents, non-alphanumeric characters, and limits length.
    """
    texto_sem_acento = (
        unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    )

    # Remover caracteres que não são letras, números, ou underscores
    texto_limpo = re.sub(r"[^a-zA-Z0-9]", "_", texto_sem_acento)

    # Limitar a 15 caracteres
    texto_limpo = texto_limpo[:15]

    return texto_limpo