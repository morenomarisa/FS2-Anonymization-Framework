from psycopg2 import sql

from config import (
    ADDRESS_COLUMN,
    BANK_INFORMATION_COLUMN,
    CPF_CNPJ_COLUMN,
    EMAILS_COLUMN,
    KEY_COLUMN,
    NAME_COLUMN,
    NAME_DATABASE,
    REPORT_COLUMN,
    RG_COLUMN,
    TELEPHONES_COLUMN,
)
from database.postgres import query
from utils.sanitizer import sanitize_all

def load_entity(column: str, quantity: int = 'ALL', offset: int = 0, separator: str = ',', sql_to_list: bool = False) -> list:
    """Load, split and sanitize entities from column of database.

    Args:
        column (str): Name of column
        quantity (int, optional): Number of rows that will be loaded from database. Defaults to ALL (all rows).
        offset (int, optional): Number of rows that are skipped from the start. Defaults to 0.
        separator (str, optional): Separator to split the column data. Defaults to ','.

    Raises:
        ValueError: If column name is None or empty.
        ValueError: If KEY_COLUMN or NAME_DATABASE is None.
        ValueError: If the number of quantity is smaller or equal 0. 
        ValueError: If the number of offset is smaller than 0. 

    Returns:
        list: returns a entity list. 
    """

    if column is None:
        error_msg = "Erro: O valor da coluna no banco de dados é None. Verifique as configurações no .env."
        print(error_msg)
        raise ValueError(error_msg)

    if KEY_COLUMN is None:
        error_msg = "Erro: KEY_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)

    if NAME_DATABASE is None:
        error_msg = "Erro: NAME_DATABASE não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)

    if quantity != 'ALL' and quantity <= 0: 
        raise ValueError(f'Error number of {column} must be greater than 0')
    
    if offset < 0:
        raise ValueError(f'Error number of offset must be greater or equals to 0')
    
    sql_query = sql.SQL(
        'SELECT {key_column}, string_to_array({column}, %s) FROM public.{name_database} WHERE {column} is not null LIMIT {quantity} OFFSET %s'
    ).format(
        key_column = sql.Identifier(KEY_COLUMN),
        name_database = sql.Identifier(NAME_DATABASE),
        column = sql.Identifier(column),
        quantity = sql.SQL(str(quantity))
    )
    
    result = query(sql_query, separator, offset)

    result_sanitized = [(record_key, sanitize_all(entities)) for record_key, entities in result]
    
    if sql_to_list: 

        entities_list = []
        
        for _, entities in result_sanitized: 
            entities_list += entities
        
        return entities_list
        
    return result_sanitized 

def get_reports(quantity: int = 'ALL', offset: int = 0, sql_to_list: bool = False) -> list:
    """Load reports from database

    Args:
        quantity (int, optional): Number of rows that will be loaded from database. Defaults to ALL. (All rows).
        offset (int, optional):   Number of rows that are skipped from the start. Defaults to 0.
        sql_to_list (bool, optional): If True, returns a list of entities instead of a list of tuples. Defaults to False.

    Returns:
        list: returns a reports list. 
    """
    if REPORT_COLUMN is None:
        error_msg = "Erro: REPORT_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)
    return load_entity(REPORT_COLUMN, quantity, offset, separator='', sql_to_list=sql_to_list)

def get_names(quantity: int = 'ALL', offset: int = 0, sql_to_list: bool = False) -> list:
    """Get names from database

    Args:
        quantity (int, optional): Number of rows that will be loaded from database. Defaults to ALL. (All rows). 
        offset (int, optional):  Number of rows that are skipped from the start. Defaults to 0.
        sql_to_list (bool, optional): If True, returns a list of entities instead of a list of tuples. Defaults to False.

    Returns:
        list: returns a name list. 
    """
    if NAME_COLUMN is None:
        error_msg = "Erro: NAME_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)
    return load_entity(NAME_COLUMN, quantity, offset, sql_to_list=sql_to_list)


def get_cpfs_cnpjs(quantity: int = 'ALL', offset: int = 0, sql_to_list: bool = False) -> list: 
    """Get cpfs_cnpjs from database

    Args:
        quantity (int, optional): Number of rows that will be loaded from database. Defaults to ALL. (All rows). 
        offset (int, optional): Number of rows that are skipped from the start. Defaults to 0.
        sql_to_list (bool, optional): If True, returns a list of entities instead of a list of tuples. Defaults to False.

    Returns:
        list: returns a cpf_cpnj list. 
    """
    if CPF_CNPJ_COLUMN is None:
        error_msg = "Erro: CPF_CNPJ_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)
    return load_entity(CPF_CNPJ_COLUMN, quantity, offset, sql_to_list=sql_to_list)

def get_rg(quantity: int = 'ALL', offset: int = 0, sql_to_list: bool = False) -> list: 
    """Get rg from database

    Args:
        quantity (int, optional): Number of rows that will be loaded from database. Defaults to ALL. (All rows). 
        offset (int, optional): Number of rows that are skipped from the start. Defaults to 0.
        sql_to_list (bool, optional): If True, returns a list of entities instead of a list of tuples. Defaults to False.

    Returns:
        list: returns a rg list. 
    """
    if RG_COLUMN is None:
        error_msg = "Erro: RG_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)
    return load_entity(RG_COLUMN, quantity, offset, sql_to_list=sql_to_list)
    
def get_telephones(quantity: int = 'ALL', offset: int = 0, sql_to_list: bool = False) -> list:     
    """Get telephones from database

    Args:
        quantity (int, optional): Number of rows that will be loaded from database. Defaults to ALL. (All rows).
        offset (int, optional): Number of rows that are skipped from the start. Defaults to 0.
        sql_to_list (bool, optional): If True, returns a list of entities instead of a list of tuples. Defaults to False.

    Returns:
        list: returns a telephone list. 
    """
    if TELEPHONES_COLUMN is None:
        error_msg = "Erro: TELEPHONES_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)
    return load_entity(TELEPHONES_COLUMN, quantity, offset, sql_to_list=sql_to_list)

def get_emails(quantity: int = 'ALL', offset: int = 0, sql_to_list: bool = False) -> list:
    """Get emails from database 

    Args:
        quantity (int, optional): Number of rows that will be loaded from database. Defaults to ALL. (All rows).
        offset (int, optional): Number of rows that are skipped from the start. Defaults to 0.
        sql_to_list (bool, optional): If True, returns a list of entities instead of a list of tuples. Defaults to False.

    Returns:
        list: returns a email list.
    """
    if EMAILS_COLUMN is None:
        error_msg = "Erro: EMAILS_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)
    return load_entity(EMAILS_COLUMN, quantity, offset, sql_to_list=sql_to_list)

def get_bank_information(quantity: int = 'ALL', offset: int = 0, sql_to_list: bool = False) -> list:
    """Get bank information from database

    Args:
        quantity (int, optional): Number of rows that will be loaded from database. Defaults to ALL. (All rows).
        offset (int, optional): Number of rows that are skipped from the start. Defaults to 0.
        sql_to_list (bool, optional): If True, returns a list of entities instead of a list of tuples. Defaults to False.

    Returns:
        list: returns a bank information list.
    """
    if BANK_INFORMATION_COLUMN is None:
        error_msg = "Erro: BANK_INFORMATION_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)
    return load_entity(BANK_INFORMATION_COLUMN, quantity, offset, separator='//', sql_to_list=sql_to_list)

def get_addresses(quantity: int = 'ALL', offset: int = 0, sql_to_list: bool = False) -> list: 
    """Get adress information from database

    Args:
        quantity (int, optional): Number of rows that will be loaded from database. Defaults to 'ALL'.
        offset (int, optional): Number of rows that are skipped from the start. Defaults to 0.
        sql_to_list (bool, optional): If True, returns a list of entities instead of a list of tuples. Defaults to False.

    Returns:
        list: returns a adress list.
    """
    if ADDRESS_COLUMN is None:
        error_msg = "Erro: ADDRESS_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)
    return load_entity(ADDRESS_COLUMN, quantity, offset, separator='', sql_to_list=sql_to_list)


ENTITY_LOADERS = {
    'names': get_names,
    'cpf_cnpj': get_cpfs_cnpjs,
    'rg': get_rg,
    'telephone': get_telephones,
    'bank_information': get_bank_information,
    'email': get_emails,
    'address': get_addresses,
}

ENTITY_COLUMNS = {
    'names': NAME_COLUMN,
    'cpf_cnpj': CPF_CNPJ_COLUMN,
    'rg': RG_COLUMN,
    'telephone': TELEPHONES_COLUMN,
    'bank_information': BANK_INFORMATION_COLUMN,
    'email': EMAILS_COLUMN,
    'address': ADDRESS_COLUMN,
}


def get_configured_entities() -> list[str]:
    """Returns the list of entity names whose database columns are configured in .env."""
    return [name for name, col in ENTITY_COLUMNS.items() if col is not None]