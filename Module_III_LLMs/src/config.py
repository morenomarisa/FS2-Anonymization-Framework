import os
from dotenv import load_dotenv

load_dotenv()


def get_env_var(var_name: str, default: str = None) -> str:
    """Reads an environment variable and normalizes empty strings or 'none' to None."""
    val = os.getenv(var_name, default)
    if val is not None and (val.strip() == '' or val.strip().lower() == 'none'):
        return None
    return val


# Postgres Database Settings
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)
POSTGRES_DBNAME = os.getenv('POSTGRES_DBNAME')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# Ollama Client Settings
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')

# Folder Settings
PROMPT_FOLDER = os.getenv('PROMPT_FOLDER', 'src/prompts/')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs/')

# Dataset Settings
NAME_DATABASE = get_env_var('NAME_DATABASE')
KEY_COLUMN = get_env_var('KEY_COLUMN')
NAME_COLUMN = get_env_var('NAME_COLUMN')
CPF_CNPJ_COLUMN = get_env_var('CPF_CNPJ_COLUMN')
RG_COLUMN = get_env_var('RG_COLUMN')
TELEPHONES_COLUMN = get_env_var('TELEPHONES_COLUMN')
EMAILS_COLUMN = get_env_var('EMAILS_COLUMN')
BANK_INFORMATION_COLUMN = get_env_var('BANK_INFORMATION_COLUMN')
ADDRESS_COLUMN = get_env_var('ADDRESS_COLUMN')
REPORT_COLUMN = get_env_var('REPORT_COLUMN')

# Experiment Options
MODEL_NAMES = [
    'gemma3:1b',
    'gemma3:4b',
    'qwen3:4b',
]

PROMPT_NAMES = [
    'prompt_1',
    'prompt_2',
    'prompt_3',
]

ENTITY_NAMES = [
    'names',
    'cpf_cnpj',
    'rg',
    'telephone',
    'bank_information',
    'email',
    'address',
]
