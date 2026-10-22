import re

def sanitize(text: str) -> str:
    """Sanitizes a text by removing leading and trailing whitespace and converting it to uppercase.

    Args:
        text (str): Text to be sanitized.

    Returns:
        str: The sanitized text.
    """

    text = re.sub(r'(?<=\D)[.(),_](?=\D)', ' ', text) # replace dots that are not between digits with spaces
    text = re.sub(r'[.,:;@!?\-+\'"()\/]', '', text)

    text = text.strip().upper() # remove leading and trailing whitespace and convert to uppercase

    text = re.sub(r'[ÁÂÀÃ]', 'A', text) # replace accented characters with their non-accented counterparts
    text = re.sub(r'[ÉÊ]', 'E', text) 
    text = re.sub(r'[Í]', 'I', text) 
    text = re.sub(r'[ÓÔÕ]', 'O', text)
    text = re.sub(r'[Ú]', 'U', text)
    text = re.sub(r'[Ç]', 'C', text)

    return text

def sanitize_all(texts: list) -> list:
    """Sanitizes a list of texts by applying the sanitize function to each text.

    Args:
        texts (list): List of texts to be sanitized.

    Returns:
        list: A list of sanitized texts.
    """
    sanitized_texts = [sanitize(text) for text in texts] # apply the sanitize function to each text in the list
    return list(filter(lambda x: x != '', sanitized_texts)) # filter out empty strings from the list of sanitized texts