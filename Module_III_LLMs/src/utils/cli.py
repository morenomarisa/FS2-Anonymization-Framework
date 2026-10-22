from InquirerPy import inquirer
from InquirerPy.base.control import Choice


def select_option(message: str, choices: list) -> str | int:
    """Displays a single-choice interactive menu using InquirerPy.

    Args:
        message (str): Prompt message shown to the user.
        choices (list): List of strings or Choice objects.

    Returns:
        str | int: The selected choice value.
    """
    return inquirer.select(
        message=message,
        choices=choices,
        instruction="(Setas: navegar | Enter: confirmar)",
    ).execute()


def select_from_list(options: list[str], prompt_message: str) -> list[str]:
    """Displays a multi-select checkbox menu using InquirerPy.

    Args:
        options (list[str]): Available options to choose from.
        prompt_message (str): Header message displayed for the checkbox.

    Returns:
        list[str]: Selected items from the options list.
    """
    choices = [Choice(value="*", name="* (Select all)")] + [
        Choice(value=opt, name=opt) for opt in options
    ]

    selected = inquirer.checkbox(
        message=prompt_message.strip(),
        choices=choices,
        instruction="(Espaço: marcar | Ctrl+R: marcar/desmarcar todos | Enter: confirmar)",
        validate=lambda result: len(result) > 0,
        invalid_message="Selecione pelo menos uma opção.",
    ).execute()

    if "*" in selected:
        return list(options)
    return selected


def ask_confirm(message: str, default: bool = False) -> bool:
    """Displays a yes/no confirmation prompt using InquirerPy."""
    return inquirer.confirm(message=message.strip(), default=default).execute()


def ask_number(message: str, min_allowed: int = 0, default: int = 0) -> int:
    """Displays a numeric input prompt using InquirerPy."""
    result = inquirer.number(
        message=message.strip(),
        min_allowed=min_allowed,
        default=default,
    ).execute()
    return int(result)


def ask_text(message: str, default: str = "") -> str:
    """Displays a text input prompt using InquirerPy."""
    return inquirer.text(message=message.strip(), default=default).execute()
