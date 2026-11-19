import glob
import os
from pathlib import Path

import pandas as pd

from config import OUTPUT_FOLDER
from metrics.metrics import (
    entity_metrics,
    load_metrics_df,
    load_reponse_df,
    load_reponse_tokens,
    load_reports_df,
    load_response_metrics,
    load_tokens_df,
    report_metrics,
    response_metrics,
)


def _ensure_tables_dir() -> None:
    Path(f'{OUTPUT_FOLDER}/tables').mkdir(parents=True, exist_ok=True)


def save_reports_df() -> None:
    """Saves the reports DataFrame to a csv file in the outputs/tables folder and prints the first 5 rows of the DataFrame.
     The reports DataFrame contains the reports used in the tests, with the columns: report_id and report.
    """
    _ensure_tables_dir()
    reports_df = load_reports_df()
    reports_df.to_csv(f'{OUTPUT_FOLDER}/tables/reports.csv', index=False)
    print(reports_df.head())

def save_tokens_df() -> None:
    """Saves the tokens DataFrame to a csv file in the outputs/tables folder and prints the first 5 rows of the DataFrame.
     The tokens DataFrame contains the tokens extracted from the reports and responses, with the columns: report_id, entity, tokens, unique_tokens, names_unique_tokens, cpfs_cnpjs_unique_tokens, rgs_unique_tokens, telephones_unique_tokens, bank_information_unique_tokens, emails_unique_tokens and addresses_unique_tokens.
    """
    _ensure_tables_dir()
    tokens_df = load_tokens_df()
    tokens_df.to_csv(f'{OUTPUT_FOLDER}/tables/tokens.csv', index=False)
    print(tokens_df.head())
    
def save_metrics_df() -> None:
    """Saves the metrics DataFrame to a csv file in the outputs/tables folder and prints the first 5 rows of the DataFrame.
     The metrics DataFrame contains the metrics calculated from the reports and responses, with the columns: report_id, entity, precision, recall, f1_score, true_positives, false_positives, false_negatives.
    """
    _ensure_tables_dir()
    metrics_df = load_metrics_df()
    metrics_df.to_csv(f'{OUTPUT_FOLDER}/tables/metrics.csv', index=False)
    print(metrics_df.head())

def save_reports_metrics_df() -> None:
    """Saves the reports metrics DataFrame to a csv file in the outputs/tables folder and prints the first 5 rows of the DataFrame.
     The reports metrics DataFrame contains the metrics calculated from the reports and responses, grouped by report, with the columns: report_id, precision, recall, f1_score, true_positives
    """
    _ensure_tables_dir()
    metrics_df = report_metrics()
    metrics_df.to_csv(f'{OUTPUT_FOLDER}/tables/reports_metrics.csv', index=False)
    print(metrics_df.head())    

def save_entities_metrics_df() -> None:
    """Saves the entities metrics DataFrame to a csv file in the outputs/tables folder and prints the first 5 rows of the DataFrame.
    The entities metrics DataFrame contains the metrics calculated from the reports and responses, grouped by entity, with the columns: entity, precision, recall, f1_score, true_positives
    """
    _ensure_tables_dir()
    tokens_df = entity_metrics()
    tokens_df.to_csv(f'{OUTPUT_FOLDER}/tables/entities_metrics.csv', index=False)
    print(tokens_df.head())


def save_reponse_df(file_name: str) -> None:
    """Saves the response DataFrame to a csv file in the outputs/tables folder and prints the first 5 rows of the DataFrame.

    Args:
        file_name (str): The name of the file to save. The file must be in the outputs/tables folder and must be a csv file.
    """
    _ensure_tables_dir()
    response_df = load_reponse_df(file_name)
    response_df.to_csv(f'{OUTPUT_FOLDER}/tables/{file_name}', index=False)
    print(response_df.head())

def save_reponse_tokens_df(file_name: str) -> None:
    """Saves the response tokens DataFrame to a csv file in the outputs/tables folder and prints the first 5 rows of the DataFrame.

    Args:
        file_name (str): The name of the file to save. The file must be in the outputs/tables folder and must be a csv file.
    """
    _ensure_tables_dir()
    response_df = load_reponse_tokens(file_name)
    response_df.to_csv(f'{OUTPUT_FOLDER}/tables/{file_name}', index=False)
    print(response_df.head())

def save_response_metrics_df(file_name: str) -> None:
    """Saves the response metrics DataFrame to a csv file in the outputs/tables folder and prints the first 5 rows of the DataFrame.

    Args:
        file_name (str): The name of the file to save. The file must be in the outputs/tables folder and must be a csv file.
    """
    _ensure_tables_dir()
    response_metrics_df = load_response_metrics(file_name)
    response_metrics_df.to_csv(f'{OUTPUT_FOLDER}/tables/{file_name}', index=False)
    print(response_metrics_df.head())

def save_response_metrics(file_name: str) -> None:
    """Saves the response metrics DataFrame to a csv file in the outputs/tables folder and prints the first 5 rows of the DataFrame.

    Args:
        file_name (str): The name of the file to save. The file must be in the outputs/tables folder and must be a csv file.
    """
    _ensure_tables_dir()
    response_metrics_report = response_metrics(file_name)
    response_metrics_report.to_csv(f'{OUTPUT_FOLDER}/tables/{file_name}', index=False)
    print(response_metrics_report.head())

def plot_total_time(file_name: str) -> None:
    """Saves the total execution time of the tests model to a csv file in the outputs/tables folder and prints the total execution time in minutes.

    Args:
        file_name (str): The name of the file to save. The file must be in the outputs/tables folder and must be a csv file.
    """
    path = os.path.join(OUTPUT_FOLDER, 'tests', file_name)
    all_files = glob.glob(os.path.join(path, "*.csv"))

    list_dataframes = []
    
    for file in all_files: # iterate over all csv files in the folder and read the execution time column to a dataframe and append to a list of dataframes
        df = pd.read_csv(file, usecols=['execution_time (s)'])
        list_dataframes.append(df)

    df_final = pd.concat(list_dataframes, ignore_index=True)
    
    df_final.rename(columns={'execution_time (s)': 'execution_time (min)'}, inplace=True)

    df_sum = df_final.sum().to_frame().T / 60

    _ensure_tables_dir()
    df_sum.to_csv(f'{OUTPUT_FOLDER}/tables/execution_time_total_{file_name.replace("/", "_")}.csv', index=False)

def plot_time_intervals(file_name: str) -> None:
    """Saves the execution time of the tests model in intervals of 10 iterations to a csv file in the outputs/tables folder and prints the execution time in minutes for each interval.

    Args:
        file_name (str): The name of the file to save. The file must be in the outputs/tables folder and must be a csv file.
    """
    path = os.path.join(OUTPUT_FOLDER, 'tests', file_name)
    all_files = glob.glob(os.path.join(path, "*.csv"))

    list_dataframes = []

    offset = 0

    for file in all_files: # iterate over all csv files in the folder and read the execution time column to a dataframe and append to a list of dataframes
        df = pd.read_csv(file, usecols=['execution_time (s)'])

        df_process = df[['execution_time (s)']].copy()
        df_process.columns = [f'execution_time (min) offset:{offset}']
        
        list_dataframes.append(df_process)

        offset += 10 
    
    df_final = pd.concat(list_dataframes, ignore_index=True)
    df_sum = df_final.sum().to_frame().T / 60

    _ensure_tables_dir()
    df_sum.to_csv(f'{OUTPUT_FOLDER}/tables/execution_time_intervals_{file_name.replace("/", "_")}.csv', index=False)