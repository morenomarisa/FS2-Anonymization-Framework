import re

EXCLUSION_PATTERN = r'D(E|(A|O)S?)'

def tokenize(text: str):
    """Tokenizes a text by splitting it into words and converting them to uppercase.

    Args:
        text (str): Text to be tokenized.

    Returns:
        _type_: A list of tokens extracted from the text.
    """

    text = text.split()
    return [text for text in text if len(text) > 1 and not re.search(EXCLUSION_PATTERN, text)]

def tokenize_all(texts: list):
    """Tokenizes a list of texts by splitting each text into words and converting them to uppercase.

    Args:
        texts (list): List of texts to be tokenized.
    Returns:
        list : A list of lists of tokens extracted from each text in the input list.
    """
    result = []

    for text in texts:
        result.extend(tokenize(text))
    
    return result