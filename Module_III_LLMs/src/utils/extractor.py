import json
import re


def get_entities_tag(text: str) -> list[str]:
    """Process entities from text using > and < tags.

    Args:
        text (str): Text that contains the entity. The entity must be between > and <.

    Returns:
        list[str]: Extracted entities.
    """
    return re.findall(r'>(.*?)<', text)


def get_entities_json(text: str) -> list[str]:
    """Process entities from JSON text.

    Args:
        text (str): JSON string containing the 'resultados' key.

    Returns:
        list[str]: Extracted entities.
    """
    try:
        dados_dict = json.loads(text)
        return dados_dict['resultados']
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def get_entities(text: str, return_type: str) -> list[str]:
    """Process entities from text according to the prompt's return_type ('tag' or 'json').

    Args:
        text (str): Response text containing extracted entities.
        return_type (str): Expected output format ('tag' or 'json').

    Returns:
        list[str]: Extracted entities.
    """
    return_type = return_type.strip().lower()
    if return_type == 'tag':
        return get_entities_tag(text)
    elif return_type == 'json':
        return get_entities_json(text)
    else:
        raise ValueError(f"Tipo de retorno desconhecido no prompt: '{return_type}'. Esperado 'tag' ou 'json'.")

