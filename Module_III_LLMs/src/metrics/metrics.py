import os
from pathlib import Path

import pandas as pd

from config import ENTITY_NAMES, OUTPUT_FOLDER
from data import entities
from utils.sanitizer import sanitize, sanitize_all
from utils.tokenizer import tokenize, tokenize_all

ENTITIES_NAMES = ENTITY_NAMES

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 150)

def load_reports_df() -> pd.DataFrame:
    """Loads the reports and their associated entities into a DataFrame.
    
    Returns:
        pd.DataFrame: A DataFrame containing the reports and their associated entities.
    """

    reports_df = pd.DataFrame(entities.get_reports(), columns=['report_id', 'report']) 

    for entity_name in entities.get_configured_entities():
        entity_data = entities.ENTITY_LOADERS[entity_name]()
        entity_df = pd.DataFrame(entity_data, columns=['report_id', entity_name]) # create a DataFrame for the entity with the report_id and the entity values
        reports_df = reports_df.merge(entity_df, on='report_id', how='left') # merge the entity DataFrame with the reports DataFrame using the report_id as key, keeping all the reports and adding the entity values where they exist
        reports_df[entity_name] = reports_df[entity_name].apply(lambda x: x if isinstance(x, list) else []) # ensure that the entity column contains lists, if there are any missing values (NaN) they will be replaced with empty lists
    
    return reports_df

def load_tokens_df() -> pd.DataFrame:
    """Loads the tokens from the reports and their associated entities into a DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the tokens from the reports and their associated entities, with the columns: report_id, report_tokens, report_unique_tokens and for each entity: entity_tokens and entity_unique_tokens.
    """
    reports_df = load_reports_df()

    tokens_df = pd.DataFrame(columns=['report_id', 'report_tokens', 'report_unique_tokens']) 
    tokens_df['report_id'] = reports_df['report_id']
    tokens_df['report_tokens'] = reports_df['report'].apply(lambda x: tokenize(x[0])) 
    tokens_df['report_unique_tokens'] = tokens_df['report_tokens'].apply(lambda x: set(x))
    
    for entity_name in entities.get_configured_entities():
        tokens_df[f'{entity_name}_tokens'] = reports_df[entity_name].apply(tokenize_all)
        tokens_df[f'{entity_name}_unique_tokens'] = tokens_df[f'{entity_name}_tokens'].apply(lambda x: set(x))
        
    return tokens_df

def load_metrics_df() -> pd.DataFrame:
    """Calculates the metrics from the tokens DataFrame, including total tokens, total unique tokens, total repeated tokens, average tokens, standard deviation of tokens and percentage of entity tokens in the report.

    Returns:
        pd.DataFrame: A DataFrame containing the metrics, with the columns: report_id, report_tokens_count, report_unique_tokens_count, report_repeated_tokens_count and for each entity: entity_tokens_count, entity_unique_tokens_count, entity_repeated_tokens_count and entity_tokens_percentage.
    """
    tokens_df = load_tokens_df()

    metrics_df = pd.DataFrame(columns=['report_id', 'report_tokens_count', 'report_unique_tokens_count'])
    metrics_df['report_id'] = tokens_df['report_id']
    metrics_df['report_tokens_count'] = tokens_df['report_tokens'].apply(lambda x: len(x))
    metrics_df['report_unique_tokens_count'] = tokens_df['report_unique_tokens'].apply(lambda x: len(x))
    metrics_df['report_repeated_tokens_count'] = metrics_df['report_tokens_count'] - metrics_df['report_unique_tokens_count']

    for entity_name in entities.get_configured_entities():
        metrics_df[f'{entity_name}_tokens_count'] = tokens_df[f'{entity_name}_tokens'].apply(lambda x: len(x))
        metrics_df[f'{entity_name}_unique_tokens_count'] = tokens_df[f'{entity_name}_unique_tokens'].apply(lambda x: len(x))
        metrics_df[f'{entity_name}_repeated_tokens_count'] = metrics_df[f'{entity_name}_tokens_count'] - metrics_df[f'{entity_name}_unique_tokens_count']
        metrics_df[f'{entity_name}_tokens_percentage'] = metrics_df[f'{entity_name}_tokens_count'] / metrics_df['report_tokens_count'] * 100
    
    return metrics_df


def report_metrics() -> pd.DataFrame:
    """Calculates the report metrics from the tokens DataFrame, including total reports, total tokens, total unique tokens, total repeated tokens, average tokens, standard deviation of tokens, minimum and maximum tokens in a report and the corresponding report ids.

    Returns:
        pd.DataFrame: A DataFrame containing the report metrics, with the columns: total_reports, total_tokens, total_unique_tokens, total_repetition_tokens, average_tokens, std_tokens, min_tokens_report_id, max_tokens_report_id, min_tokens and max_tokens.
    """
    metrics_df = load_metrics_df()
    
    max_report_token = metrics_df['report_tokens_count'].idxmax()
    min_report_token = metrics_df['report_tokens_count'].idxmin()

    token_metrics_reports = pd.DataFrame({
        'total_reports': len(metrics_df),
        'total_tokens': metrics_df['report_tokens_count'].sum(),
        'total_unique_tokens': metrics_df['report_unique_tokens_count'].sum(),
        'total_repetition_tokens': metrics_df['report_repeated_tokens_count'].sum(),
        'average_tokens': metrics_df['report_tokens_count'].mean(),
        'std_tokens': metrics_df['report_tokens_count'].std(),
        'min_tokens_report_id': metrics_df['report_id'].iloc[min_report_token],
        'max_tokens_report_id': metrics_df['report_id'].iloc[max_report_token],
        'min_tokens': metrics_df['report_tokens_count'].iloc[min_report_token],
        'max_tokens': metrics_df['report_tokens_count'].iloc[max_report_token]
    }, index=[0])

    return token_metrics_reports

def entity_metrics() -> pd.DataFrame:
    """Calculates the entity metrics from the tokens DataFrame, including total entity tokens, total unique entity tokens, total repeated entity tokens, average entity tokens, standard deviation of entity tokens and percentage of entity tokens in the report.

    Returns:
        pd.DataFrame: A DataFrame containing the entity metrics, with the columns: entity_name, total_entity_tokens, total_unique_entity_tokens, total_repetition_entity_tokens, average_entity_tokens, std_entity_tokens and entity_tokens_percentage.
    """
    metrics_df = load_metrics_df()
    entities_metrics_reports = pd.DataFrame()

    for entity_name in entities.get_configured_entities():
        min_idx = metrics_df[f'{entity_name}_tokens_count'].idxmin()
        max_idx = metrics_df[f'{entity_name}_tokens_count'].idxmax()

        entity_metrics_reports = pd.DataFrame({
            'entity_name': entity_name,
            'total_entity_tokens': metrics_df[f'{entity_name}_tokens_count'].sum(),
            'total_unique_entity_tokens': metrics_df[f'{entity_name}_unique_tokens_count'].sum(),
            'total_repetition_entity_tokens': metrics_df[f'{entity_name}_repeated_tokens_count'].sum(),
            'average_entity_tokens': metrics_df[f'{entity_name}_tokens_count'].mean(),
            'std_entity_tokens': metrics_df[f'{entity_name}_tokens_count'].std(),
            'entity_tokens_percentage': metrics_df[f'{entity_name}_tokens_percentage'].mean(),
            'min_entity_tokens_report_id': metrics_df['report_id'].iloc[min_idx],
            'max_entity_tokens_report_id': metrics_df['report_id'].iloc[max_idx],
            'min_entity_tokens': metrics_df[f'{entity_name}_tokens_count'].iloc[min_idx],
            'max_entity_tokens': metrics_df[f'{entity_name}_tokens_count'].iloc[max_idx]
        }, index=[0])

        entities_metrics_reports = pd.concat([entities_metrics_reports, entity_metrics_reports], ignore_index=True)

    return entities_metrics_reports

def load_reponse_df(file_name: str) -> pd.DataFrame:
    """Loads the response DataFrame from a csv file in the outputs/tables folder.

    Args:
        file_name (str): The name of the file containing the response data. The file must be in the outputs/tables folder and must be a csv file.

    Returns:
        pd.DataFrame: A DataFrame containing the response data, with the columns: report_id, response and execution_time (s).
    """
    response_df = pd.read_csv(os.path.join(OUTPUT_FOLDER, 'tests', file_name)) # load the results of the tests from the csv file
    
    return response_df

def load_reponse_tokens(file_name: str) -> pd.DataFrame:
    """Loads the response tokens DataFrame from the response DataFrame, which contains the report_id, response_tokens and response_unique_tokens columns.

    Args:
        file_name (str): The name of the file containing the response data. The file must be in the outputs/tables folder and must be a csv file.

    Returns:
        pd.DataFrame:  A DataFrame containing the response tokens, with the columns: report_id, response_tokens and response_unique_tokens.
    """
    response_df = load_reponse_df(file_name)
    response_df['response'] = response_df['response'].fillna('') # fill any missing values in the response column with empty strings to avoid errors when tokenizing

    response_tokens_df = pd.DataFrame(columns=['report_id', 'response_tokens', 'response_unique_tokens']) 
    response_tokens_df['report_id'] = response_df['report_id']
    response_tokens_df['response_tokens'] = response_df['response'].apply(lambda x: sanitize_all(tokenize(x))) 
    response_tokens_df['response_unique_tokens'] = response_tokens_df['response_tokens'].apply(lambda x: set(x))

    return response_tokens_df

def load_response_metrics(file_name: str) -> pd.DataFrame:
    """Calculates the response metrics from the response tokens DataFrame, including total responses, total response tokens, total unique response tokens, total repeated response tokens, average response tokens and standard deviation of response tokens.

    Args:
        file_name (str): The name of the file containing the response data. The file must be in the outputs/tables folder and must be a csv file.

    Returns:
        pd.DataFrame: A DataFrame containing the response metrics, with the columns: total_responses, total_response_tokens, total_unique_response_tokens, total_repetition_response_tokens, average_response_tokens and std_response_tokens.
    """
    response_tokens_df = load_reponse_tokens(file_name)

    response_metrics_df = pd.DataFrame(columns=['report_id', 'response_tokens_count', 'response_unique_tokens_count'])
    response_metrics_df['report_id'] = response_tokens_df['report_id']
    response_metrics_df['response_tokens_count'] = response_tokens_df['response_tokens'].apply(lambda x: len(x))
    response_metrics_df['response_unique_tokens_count'] = response_tokens_df['response_unique_tokens'].apply(lambda x: len(x))
    response_metrics_df['response_repeated_tokens_count'] = response_metrics_df['response_tokens_count'] - response_metrics_df['response_unique_tokens_count']

    return response_metrics_df

def response_metrics(file_name: str) -> pd.DataFrame:
    """Calculates the response metrics from the response tokens DataFrame, including total responses, total response tokens, total unique response tokens, total repeated response tokens, average response tokens and standard deviation of response tokens.

    Args:
        file_name (str): The name of the file containing the response data. The file must be in the outputs/tables folder and must be a csv file.

    Returns:
        pd.DataFrame: A DataFrame containing the response metrics, with the columns: total_responses, total_response_tokens, total_unique_response_tokens, total_repetition_response_tokens, average_response_tokens and std_response_tokens.
    """
    response_metrics_df = load_response_metrics(file_name)
    
    response_token_metrics_reports = pd.DataFrame({
        'total_responses': len(response_metrics_df),
        'total_response_tokens': response_metrics_df['response_tokens_count'].sum(),
        'total_unique_response_tokens': response_metrics_df['response_unique_tokens_count'].sum(),
        'total_repetition_response_tokens': response_metrics_df['response_repeated_tokens_count'].sum(),
        'average_response_tokens': response_metrics_df['response_tokens_count'].mean(),
        'std_response_tokens': response_metrics_df['response_tokens_count'].std(),
    }, index=[0])

    return response_token_metrics_reports

def tokens_report_test(quantity: str = 'ALL', offset: int = 0) -> int: 
    """Calculates the total number of tokens in a list of reports.
    Args:
        reports (list): List of reports, where each report is a tuple containing the report id and the report text.
    Returns:
        int: Total number of tokens in the reports.
    """
    reports = entities.get_reports(quantity=quantity, offset=offset, sql_to_list=False) 

    total_tokens = 0
    
    for report in reports:
        total_tokens += len(set(tokenize(sanitize(report[1][0]))))
    
    return total_tokens

def token_report_metrics(quantity: int | str = 10, iterations: int = 5) -> None:
    """Calculates the total number of tokens in a list of reports in intervals of 10 iterations and saves the results in a csv file in the outputs/tables folder.

    Args:
        quantity (int | str, optional): The number of reports to include in each interval. Defaults to 10.
        iterations (int, optional): The number of intervals to calculate. Defaults to 5.
    """
    offset = 0
    i = 0 

    token_report_df = pd.DataFrame(columns=['start', 'end', 'total_tokens'])

    total_sum = 0
    while i < iterations:
        total_tokens = tokens_report_test(quantity=quantity, offset=offset)
        
        if total_tokens == 0:
            break
        
        token_report_df.loc[len(token_report_df)] = [offset+1, offset + quantity, total_tokens]
        print(f'Offset: [{offset+1} - {offset + quantity}], Total Tokens: {total_tokens}')
        total_sum += total_tokens

        if quantity == 'ALL':
            break

        offset += quantity
        i += 1

    print(f'Total sum of tokens: {total_sum}')
    Path(f'{OUTPUT_FOLDER}/token_report').mkdir(parents=True, exist_ok=True)
    token_report_df.to_csv(f'{OUTPUT_FOLDER}/token_report/token_report_metrics.csv', index=False)