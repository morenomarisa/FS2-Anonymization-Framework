import os
from pathlib import Path

from InquirerPy.base.control import Choice
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from config import OUTPUT_FOLDER
from data import entities
from metrics import charts
from utils.cli import select_option
from utils.tokenizer import tokenize

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 150)


def _ensure_output_dir() -> None:
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)


def tokens_per_entity():
    """Calculates and displays token counts for each entity type.
    
    Returns:
        entity_df (pd.DataFrame): DataFrame with the token counts for each entity type.
        token_metrics_entity (pd.DataFrame): DataFrame with the token metrics for the entities.

    """
    _ensure_output_dir()

    entity_rows = [
        (ent_name, entities.ENTITY_LOADERS[ent_name](sql_to_list=True))
        for ent_name in entities.get_configured_entities()
    ]
    entity_df = pd.DataFrame(entity_rows, columns=['entity', 'data'])
    
    entity_df['unique'] = entity_df['data'].apply(lambda x: set(x)) # create a new column with the unique entities of each type
    entity_df['token_count']  = entity_df['data'].apply(lambda x: len(x)) # create a new column with the total number of tokens that the entities of each type represent
    entity_df['token_unique_count'] = entity_df['unique'].apply(lambda x: len(x)) # create a new column with the total number of tokens that the unique entities of each type represent
    entity_df['token_repetition_count'] = entity_df['token_count'] - entity_df['token_unique_count'] # create a new column with the total number of tokens that the repeated entities of each type represent, calculated as the difference between the total token count and the unique token count for each entity type

    token_metrics_entity = pd.DataFrame({
        'total_tokens': entity_df['token_count'].sum(),
        'total_unique_tokens': entity_df['token_unique_count'].sum(),
        'total_repetition_tokens': entity_df['token_repetition_count'].sum(),
        'average_tokens': entity_df['token_count'].mean(),
        'std_tokens': entity_df['token_count'].std(),
        'min_tokens': entity_df['token_count'].min(),
        'max_tokens': entity_df['token_count'].max()
    }, index=[0])

    entity_df.to_csv(os.path.join(OUTPUT_FOLDER, 'tokens_per_entity.csv'), index=False) # save the results of the token counts for each entity type in a csv file
    entity_df.to_excel(os.path.join(OUTPUT_FOLDER, 'tokens_per_entity.xlsx'), index=False)
    token_metrics_entity.to_csv(os.path.join(OUTPUT_FOLDER, 'entity_token_metrics.csv'), index=False) # save the results of the token metrics for the entities in a csv file
    return entity_df, token_metrics_entity


def tokens_per_report():
    """Calculates and displays token counts for each report and the proportion of tokens that each entity type represents in the report.

    Returns:
        reports_df (pd.DataFrame): DataFrame with the token counts and proportions for each report.
        token_names_metrics (pd.DataFrame): DataFrame with the token metrics for the entities of type 'names'.
        token_metrics_reports (pd.DataFrame): DataFrame with the token metrics for the reports. 

    """
    _ensure_output_dir()
    # count the number of tokens in each report
    reports_df = pd.DataFrame(entities.get_reports(), columns=['report_id', 'report']) # load reports from database
    reports_df['report'] = reports_df['report'].apply(lambda x: tokenize(x[0])) # extract the report text from the tuple
    reports_df['token_count'] = reports_df['report'].apply(lambda x: len(x)) # calculate the number of tokens in each report
    reports_df['unique_token_count'] = reports_df['report'].apply(lambda x: len(set(x))) # calculate the number of unique tokens in each report
    reports_df['repetition_token_count'] = reports_df['token_count'] - reports_df['unique_token_count']
    reports_df['total_reports'] = len(reports_df)

    for entity_name in entities.get_configured_entities():
        entity_data = entities.ENTITY_LOADERS[entity_name]()
        entity_df = pd.DataFrame(entity_data, columns=['report_id', entity_name])
        reports_df = reports_df.merge(entity_df, on='report_id', how='left') # relation entity with report
        reports_df[f'{entity_name}_token_count'] = reports_df[entity_name].dropna().apply(lambda x: len(x) if isinstance(x, list) else 0) # count the number of tokens that the entity represents in the report
        reports_df[f'{entity_name}_token_count_unique'] = reports_df[entity_name].dropna().apply(lambda x: len(set(x)) if isinstance(x, list) else 0)
        reports_df[f'{entity_name}_token_percent'] = reports_df.dropna().apply(lambda row: row[f'{entity_name}_token_count'] / row['token_count'] * 100 if row['token_count'] > 0 else 0, axis=1) # proportion of tokens that the entity represents in the report


    token_metrics_reports = pd.DataFrame({
        'total_reports': reports_df['total_reports'].iloc[0],
        'total_tokens': reports_df['token_count'].sum(),
        'total_unique_tokens': reports_df['unique_token_count'].sum(),
        'total_repetition_tokens': reports_df['repetition_token_count'].sum(),
        'average_tokens': reports_df['token_count'].mean(),
        'std_tokens': reports_df['token_count'].std(),
        'min_tokens': reports_df['token_count'].min(),
        'max_tokens': reports_df['token_count'].max()
    }, index=[0])

    token_names_metrics = pd.DataFrame({
        'total_tokens': reports_df['names_token_count'].sum(),
        'total_unique_tokens': reports_df['names_token_count_unique'].sum(),
        'total_repetition_tokens': reports_df['names_token_count'].sum() - reports_df['names_token_count_unique'].sum(),
        'average_tokens': reports_df['names_token_count'].mean(),
        'std_tokens': reports_df['names_token_count'].std(),
        'min_tokens': reports_df['names_token_count'].min(),
        'max_tokens': reports_df['names_token_count'].max(), 
        'total_percent': reports_df['names_token_count'].sum() / reports_df['token_count'].sum() * 100
    }, index=[0])

    reports_df.to_csv(os.path.join(OUTPUT_FOLDER, 'tokens_per_report.csv'), index=False) # save the results of the token counts and proportions for each report in a csv file
    token_metrics_reports.to_csv(os.path.join(OUTPUT_FOLDER, 'report_token_metrics.csv'), index=False) # save the results of the token metrics for the reports in a csv file
    token_names_metrics.to_csv(os.path.join(OUTPUT_FOLDER, 'names_token_metrics.csv'), index=False) # save the results of the token metrics for the entities of type 'names' in a csv file
    reports_df.to_excel(os.path.join(OUTPUT_FOLDER, 'tokens_per_report.xlsx'), index=False)
    
    return reports_df, token_names_metrics, token_metrics_reports

def plot_tokens_per_report(reports_df: pd.DataFrame):
    """Plots the distribution of token counts per report.

    Args:
        reports_df (pd.DataFrame): DataFrame with the token counts for each report.

    """
    _ensure_output_dir()
    plt.figure(figsize=(10, 6))
    sns.histplot(reports_df['token_count'], bins=30, kde=True)
    plt.title('Distribution of Token Counts per Report')
    plt.xlabel('Token Count')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/tokens_per_report.png')
    plt.close()

def plot_tokens_per_names(reports_df: pd.DataFrame):
    """Plots the distribution of token counts for the 'names' entity type.

    Args:
        tokens_per_entity_df (pd.DataFrame): DataFrame with the token counts for each entity type.

    """
    _ensure_output_dir()
    plt.figure(figsize=(10, 6))
    sns.histplot(reports_df['names_token_count'].dropna(), bins=30, kde=True)
    plt.title('Distribution of Token Counts for Names Entity')
    plt.xlabel('Token Count')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_FOLDER}/tokens_per_names.png')
    plt.close()

def menu(): 
    """ Displays a menu for exploratory analysis of token counts and proportions for entities in reports.
        The user can choose to view metrics for entities, reports, or specific entity types, as well as visualizations of token distributions. The results are saved in CSV and Excel files in the specified output folder.
        
        returns:
            None
    """
    options = select_option(
        message="Exploratory Analysis & Charts - Select an option:",
        choices=[
            Choice(value=1, name="1 - Entities Metrics"),
            Choice(value=2, name="2 - Report Metrics"),
            Choice(value=3, name="3 - Reports Distribution Graphic"),
            Choice(value=4, name="4 - Names Distribution Graphic"),
            Choice(value=5, name="5 - Token Entities Metrics"),
            Choice(value=6, name="6 - Token Names Metrics"),
            Choice(value=7, name="7 - Token Reports Metrics"),
            Choice(value=8, name="8 - All Frequency Charts (Reports & Entities with IC 95%)"),
            Choice(value=9, name="9 - Exit"),
        ],
    )

    if options == 9:
        return print("Exiting the program.")

    if options == 8:
        charts.token_frequency_per_report()
        charts.token_frequency_per_report_mean()
        charts.token_frequency_per_entity()
        charts.token_frequency_per_entity_mean()
        print(f"Charts saved in '{OUTPUT_FOLDER}/charts/'.")
        return

    if options in (1, 5):
        entity_df, token_metrics_entity = tokens_per_entity()
        if options == 1:
            print(entity_df)
        else:
            print(token_metrics_entity)
        return

    reports_df, token_names_metrics, token_metrics_reports = tokens_per_report()

    match options: 
        case 2:
            print(reports_df)
        
        case 3:
            plot_tokens_per_report(reports_df)
            print(f"Chart saved in '{OUTPUT_FOLDER}/tokens_per_report.png'.")
        
        case 4: 
            plot_tokens_per_names(reports_df)
            print(f"Chart saved in '{OUTPUT_FOLDER}/tokens_per_names.png'.")
        
        case 6:
            print(token_names_metrics)

        case 7: 
            print(token_metrics_reports)


if __name__ == '__main__': 
    menu()
    # print(f'Minimum tokens in a report: {reports_token_min}')
    # print(f'Maximum tokens in a report: {reports_token_max}')
    # reports_df, _, _, _, _, _ = tokens_per_report()
    # plot_tokens_per_report(reports_df)
    # print(reports_df)   