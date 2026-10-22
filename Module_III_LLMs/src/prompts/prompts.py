import os

from config import PROMPT_FOLDER

def load_prompt(name: str):
    """Load prompt with a specifc name

    Args:
        name (str): name of prompt

    Returns:
        str: Returns prompt
    """
    try:
        with open(os.path.join(PROMPT_FOLDER, f'{name}.txt'), 'r', encoding='utf-8') as f: 
            return f.read()
        
    except FileNotFoundError: 
        print(f'Error: file {str(os.path.join(PROMPT_FOLDER, f'{name}.txt'))} not found! Check your enviroment variables.')

    return '' 