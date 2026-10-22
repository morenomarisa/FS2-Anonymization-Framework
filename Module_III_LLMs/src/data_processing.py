import ast
from glob import glob
import os
from pathlib import Path

import pandas as pd

from config import ENTITY_NAMES, KEY_COLUMN, MODEL_NAMES, OUTPUT_FOLDER, PROMPT_NAMES
from data import entities
from prompts import prompts
from utils.cli import ask_confirm, select_from_list
from utils.extractor import get_entities, get_entities_json, get_entities_tag
from utils.sanitizer import sanitize, sanitize_all
from utils.tokenizer import tokenize, tokenize_all

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 250)


def calculate_metrics(file_name: str):
    """Calculate the metrics for the results of the tests and save the resulting DataFrame with the metrics in a new csv file.

    Args:
        file_name (str): The name of the file with the results of the tests, including the .csv extension. The file must be in the folder outputs/tests/model_name/prompt_name/entity/.
        entity (str): The type of entity to analyze. The entity type must be the same as the name of the folder where the results of the tests are stored, which is outputs/tests/model_name/prompt_name/entity/.

    Returns:
        pd.DataFrame: A DataFrame with the metrics for each test, including the true positives, false positives, false negatives, true negatives, precision, recall and F1 score for each entity type in the responses.
    """
    # get the model name, prompt name and entity type from the file name, which is in the format outputs/tests/model_name/prompt_name/entity/tests_result_model_name_prompt_name_entity_iteration_with_metrics.csv

    file_name_parts = Path(file_name).parts

    model_name = file_name_parts[0]
    prompt_name = file_name_parts[1]
    entity = file_name_parts[2]

    prompt_text = prompts.load_prompt(prompt_name + '_' + entity).split('---')
    return_type = prompt_text[0].strip().lower()

    if not KEY_COLUMN:
        error_msg = "Erro: KEY_COLUMN não está configurada no .env (valor é None)."
        print(error_msg)
        raise ValueError(error_msg)

    reports_df = pd.DataFrame(entities.get_reports(), columns=[KEY_COLUMN, 'report'])
    reports_df[KEY_COLUMN] = reports_df[KEY_COLUMN].apply(str)

    test_df = pd.read_csv(os.path.join(OUTPUT_FOLDER, 'tests', file_name)) # load the results of the tests from the csv file
    test_df['report_id'] = test_df['report_id'].apply(str)
    test_df['report'] = test_df['report_id'].apply(lambda x: reports_df.loc[reports_df[KEY_COLUMN] == x, 'report'].values[0][0]) # add the report text to the test DataFrame by matching the report_id with the reports DataFrame
    test_df['response'] = test_df['response'].fillna('')
    test_df['report_tokens'] = test_df['report'].apply(lambda x: set(tokenize(sanitize(x)))) # create a new column with the unique tokens in the reports
    test_df['response_tokens'] = test_df['response'].apply(lambda x: set(tokenize(sanitize(x)))) # create a new column with the unique tokens in the responses

    # Load entities dynamically for the entity being evaluated
    entities_in_test = set(test_df['entity'].dropna().unique()) if 'entity' in test_df.columns else {entity}
    if not entities_in_test:
        entities_in_test = {entity}

    entities_data = {}
    for ent in entities_in_test:
        if ent in entities.ENTITY_LOADERS:
            entities_data[ent] = dict(entities.ENTITY_LOADERS[ent]())
        else:
            raise ValueError(f"Entidade desconhecida: {ent}")
    
    test_df['observed_total'] = test_df.apply(lambda row: set(tokenize_all(sanitize_all(entities_data.get(row['entity'], {}).get(row['report_id'], [])))), axis=1) # create a new column with the unique tokens in the observed entities of each type in the responses, using the report_id to get the correct entities for each report
    test_df['observed'] = test_df.apply(lambda row: row['observed_total'] & row['report_tokens'], axis=1) # create a new column with the unique tokens in the observed entities of each type in the responses that are also in the report tokens, which should be the correct observed entities for each report
    test_df['error_tokens'] = test_df.apply(lambda row: row['observed_total'] - row['report_tokens'], axis=1) # calculate the number of error tokens for each entity type in the responses
    test_df['predicted_total'] = test_df['response'].apply(lambda x: set(tokenize_all(sanitize_all(get_entities(str(x), return_type)))))  # create a new column with the unique entities of each type in the responses based on prompt return_type
    test_df['predicted'] = test_df.apply(lambda row: row['predicted_total'] & row['report_tokens'], axis=1) # create a new column with the unique entities of each type in the responses that are also in the report tokens, which should be the correct predicted entities for each report
    test_df['predicted_made_up'] = test_df.apply(lambda row: row['predicted_total'] - row['report_tokens'], axis=1) # create a new column with the unique entities of each type in the responses that are not in the report tokens, which should be the made up predicted entities for each report
    
    test_df['fp_tokens'] = test_df.apply(lambda row: row['predicted'] - row['observed'], axis=1) # calculate the number of false positives for each entity type in the responses
    test_df['fn_tokens'] = test_df.apply(lambda row: row['observed'] - row['predicted'], axis=1) # calculate the number of false negatives for each entity type in the responses
    
    test_df['tp'] = test_df.apply(lambda row: len(row['observed'] & row['predicted']), axis=1) # calculate the number of true positives for each entity type in the responses
    test_df['fp'] = test_df['fp_tokens'].apply(lambda x: len(x))
    test_df['fn'] = test_df['fn_tokens'].apply(lambda x: len(x))
    test_df['tn'] = test_df.apply(lambda row: len(row['report_tokens'] - row['observed'] - row['predicted']), axis=1) # calculate the number of true negatives for each entity type in the responses
    test_df['precision'] = test_df.apply(lambda row: row['tp'] / (row['tp'] + row['fp']) if (row['tp'] + row['fp']) > 0 else 0, axis=1) # calculate the precision for each entity type in the responses
    test_df['recall'] = test_df.apply(lambda row: row['tp'] / (row['tp'] + row['fn']) if (row['tp'] + row['fn']) > 0 else 0, axis=1) # calculate the recall for each entity type in the responses
    test_df['f1'] = test_df.apply(lambda row: 2 * (row['precision'] * row['recall']) / (row['precision'] + row['recall']) if (row['precision'] + row['recall']) > 0 else 0, axis=1) # calculate the F1 score for each entity type in the responses
    
    os.makedirs(os.path.join(f'{OUTPUT_FOLDER}/metrics/{model_name}/{prompt_name}/{entity}'), exist_ok=True)
    test_df.to_csv(os.path.join(f'{OUTPUT_FOLDER}/metrics/{model_name}/{prompt_name}/{entity}', f'{Path(file_name).stem}_with_metrics.csv'), index=False) # save the results of the tests with the calculated metrics in a new csv file
    
    return test_df

def calculate_all_metrics(file_name: str):
    """Calculate the metrics for all the test results in a folder and save the resulting DataFrame with the metrics in a new csv file.

    Args:
        file_name (str): The name of the folder with the results of the tests, including the model name, prompt name and entity type. The folder must be in the path outputs/metrics/model_name/prompt_name/entity/.

    Returns:
        pd.DataFrame: A DataFrame with the aggregated metrics for all tests in the folder.
    """
    path = os.path.join(OUTPUT_FOLDER, 'metrics', file_name)
    all_files = glob(os.path.join(path, "*.csv"))

    df = pd.concat((pd.read_csv(file) for file in all_files), ignore_index=True) # read all csv files in the folder and concatenate them into a single DataFrame

    df_analysis = df[['report_tokens', 'observed', 'response_tokens', 'error_tokens', 'execution_time (s)']].copy()
    df_analysis['report_tokens_count'] = df_analysis['report_tokens'].map(lambda s: len(ast.literal_eval(s)))
    df_analysis['entity_tokens_count'] = df_analysis['observed'].map(lambda s: len(ast.literal_eval(s)))
    df_analysis['response_tokens_count'] = df_analysis['response_tokens'].apply(lambda s: len(ast.literal_eval(s)))
    df_analysis['error_tokens_count'] = df_analysis['error_tokens'].apply(lambda s: len(ast.literal_eval(s)))
    df_analysis['execution_time (s)'] = df_analysis['execution_time (s)'].astype(float)

    df_output = pd.DataFrame()
    df_output['report_tokens (sum)'] = [df_analysis['report_tokens_count'].sum()]
    df_output['report_tokens (avg)'] = [df_analysis['report_tokens_count'].mean()]
    df_output['entity_tokens (sum)'] = [df_analysis['entity_tokens_count'].sum()]
    df_output['entity_tokens (avg)'] = [df_analysis['entity_tokens_count'].mean()]
    df_output['response_tokens (sum)'] = [df_analysis['response_tokens_count'].sum()]
    df_output['response_tokens (avg)'] = [df_analysis['response_tokens_count'].mean()]
    df_output['error_tokens (sum)'] = [df_analysis['error_tokens_count'].sum()]
    df_output['execution_time (s) (sum)'] = [df_analysis['execution_time (s)'].sum()]
    df_output['execution_time (s) (avg)'] = [df_analysis['execution_time (s)'].mean()]

    df = df[['tp', 'fp', 'fn', 'tn', 'precision', 'recall', 'f1']]  
    df = df.sum().to_frame().T
    df_output['tp'] = df['tp'].astype(int) 
    df_output['fp'] = df['fp'].astype(int) 
    df_output['fn'] = df['fn'].astype(int) 
    df_output['tn'] = df['tn'].astype(int)
    df_output['accuracy'] = df_output.apply(lambda row: (row['tp'] + row['tn']) / (row['tp'] + row['tn'] + row['fp'] + row['fn']) if (row['tp'] + row['tn'] + row['fp'] + row['fn']) > 0 else 0, axis=1)
    df_output['precision'] = df_output.apply(lambda row: row['tp'] / (row['tp'] + row['fp']) if (row['tp'] + row['fp']) > 0 else 0, axis=1) # calculate the precision for each entity type in the responses
    df_output['recall'] = df_output.apply(lambda row: row['tp'] / (row['tp'] + row['fn']) if (row['tp'] + row['fn']) > 0 else 0, axis=1) # calculate the recall for each entity type in the responses
    df_output['f1'] = df_output.apply(lambda row: 2 * (row['precision'] * row['recall']) / (row['precision'] + row['recall']) if (row['precision'] + row['recall']) > 0 else 0, axis=1) # calculate the F1 score for each entity type in the responses

    os.makedirs(os.path.join(f'{OUTPUT_FOLDER}/all_metrics/{file_name}'), exist_ok=True)
    df_output.to_csv(os.path.join(f'{OUTPUT_FOLDER}/all_metrics/{file_name}', f'{Path(file_name).stem}_all_metrics.csv'), index=False) # save the results of the tests with the calculated metrics in a new csv file
    return df_output

def calculate_intervals_metrics(file_name: str): 
    """Calculate the metrics for each time interval of the tests and save the resulting DataFrame with the metrics in a new csv file.

    Args:
        file_name (str): The name of the folder with the results of the tests, including the model name, prompt name and entity type. The folder must be in the path outputs/metrics/model_name/prompt_name/entity/.

    Returns:
        pd.DataFrame: A DataFrame with the metrics for each time interval of the tests, including the true positives, false positives, false negatives, true negatives, precision, recall and F1 score for each entity type in the responses.
    """
    path = os.path.join(OUTPUT_FOLDER, 'metrics', file_name)
    path_save = f'/{file_name.split("/")[0]}/{file_name.split("/")[1]}/{file_name.split("/")[2]}'
    
    intervals_df = pd.read_csv(path) # read the csv file with the metrics for each time interval into a DataFrame
    
    intervals_df = intervals_df[['model', 'prompt', 'entity', 'tp', 'fp', 'fn', 'tn', 'precision', 'recall', 'f1']]  
    
    intervals_df = intervals_df.sum().to_frame().T
    
    intervals_df['model'] = file_name.split('/')[0] 
    intervals_df['prompt'] = file_name.split('/')[1] 
    intervals_df['entity'] = file_name.split('/')[2]
    intervals_df['tp'] = intervals_df['tp'].astype(int)
    intervals_df['fp'] = intervals_df['fp'].astype(int)
    intervals_df['fn'] = intervals_df['fn'].astype(int)
    intervals_df['tn'] = intervals_df['tn'].astype(int)
    intervals_df['precision'] = intervals_df.apply(lambda row: row['tp'] / (row['tp'] + row['fp']) if (row['tp'] + row['fp']) > 0 else 0, axis=1) # calculate the precision for each entity type in the responses
    intervals_df['recall'] = intervals_df.apply(lambda row: row['tp'] / (row['tp'] + row['fn']) if (row['tp'] + row['fn']) > 0 else 0, axis=1) # calculate the recall for each entity type in the responses
    intervals_df['f1'] = intervals_df.apply(lambda row: 2 * (row['precision'] * row['recall']) / (row['precision'] + row['recall']) if (row['precision'] + row['recall']) > 0 else 0, axis=1) # calculate the F1 score for each entity type in the responses    

    os.makedirs(os.path.join(f'{OUTPUT_FOLDER}/intervals_metrics/{path_save}'), exist_ok=True)
    intervals_df.to_csv(os.path.join(f'{OUTPUT_FOLDER}/intervals_metrics/{path_save}', f'{Path(file_name).stem}_intervals_metrics.csv'), index=False) # 
    return intervals_df

def main(): 
    selected_models = select_from_list(MODEL_NAMES, "Select the models to be tested:")
    selected_prompts = select_from_list(PROMPT_NAMES, "Select the prompts to be tested:")
    selected_entities = select_from_list(ENTITY_NAMES, "Select the entities to be tested:")
    calculate_metrics_option = ask_confirm('Do you want to calculate the metrics interval of the tests?')
    calculate_all_metrics_option = ask_confirm('Do you want to calculate the aggregated metrics for all tests in a folder?')
    calculate_intervals_metrics_option = ask_confirm('Do you want to calculate all metrics of one interval tests?')


    if calculate_all_metrics_option:
        for folder in glob(os.path.join(f'{OUTPUT_FOLDER}/metrics/{",".join(selected_models)}/{",".join(selected_prompts)}/{",".join(selected_entities)}/'.replace(':', '_'))): # iterate over all folders in the metrics folder
            calculate_all_metrics(file_name=folder.replace(f'{OUTPUT_FOLDER}/metrics/', '')) # calculate the aggregated metrics for all tests in each folder and save the resulting DataFrame with the metrics in a new csv file
    elif calculate_intervals_metrics_option:
        for file in glob(os.path.join(f'{OUTPUT_FOLDER}/metrics/{",".join(selected_models)}/{",".join(selected_prompts)}/{",".join(selected_entities)}/*.csv'.replace(':', '_'))): # iterate over all csv files in the metrics folder
            calculate_intervals_metrics(str(file).replace(f'{OUTPUT_FOLDER}/metrics/', '')) # calculate the metrics for each time interval of the tests and save the resulting DataFrame with the metrics in a new csv file
    elif calculate_metrics_option:
        for file in glob(os.path.join(f'{OUTPUT_FOLDER}/tests/{",".join(selected_models)}/{",".join(selected_prompts)}/{",".join(selected_entities)}/*.csv'.replace(':', '_'))): # iterate over all csv files in the metrics folder
            calculate_metrics(str(file).replace(f'{OUTPUT_FOLDER}/tests/', '')) # calculate the metrics for each time interval of the tests and save the resulting DataFrame with the metrics in a new csv file
    else:
        print('No metrics will be calculated. Exiting...')
