from glob import glob
import os
from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay

from config import ENTITY_NAMES, MODEL_NAMES, OUTPUT_FOLDER, PROMPT_NAMES
from utils.cli import ask_confirm, ask_text, select_from_list

def plot_confusion_matrix(results: list, title: str, file_name: str): 
  """The function plots the confusion matrix for the given results, title, and file name

  Args:
      results (list): Confusion matrix results as a list of lists
      title (str): Title for the confusion matrix plot
      file_name (str): File name to save the confusion matrix plot
  """

  labels = ["0", "1"] 
  
  data = np.array(results) # recebe os dados calculados
  
  display = ConfusionMatrixDisplay(confusion_matrix=data, display_labels=labels)
  display.plot(cmap="binary", values_format='.0f')
  plt.title(title)

  plt.xlabel("Predicted label")
  plt.ylabel("True label")

  plt.savefig(file_name) 
  plt.close()

def calculate_results(df: pd.DataFrame):
  """ calculates the sum of the metrics for each column of a dataset

  Args:
      df (pd.DataFrame): Metrics calculated on the data of the passed model

  Returns:
      list: Confusion matrix results as a list of lists
  """
  table = [
    [df['tn'].sum(), df['fp'].sum()],
    [df['fn'].sum(), df['tp'].sum()] 
  ] # sum of columns

  token_sum = table[0][0] + table[0][1] + table[1][1]
  print(df.head()) 
  print(f'Token sum: {token_sum}')

  return table

  
def calculate_model_result(file_name: str): 
  """Plots the confusion matrices based on the metrics obtained by anonymization for each model and entity type.

  Args:
      file_name (str): Name of the file containing the metrics
  """

  file_name_parts = Path(file_name).parts
  
  model_name = file_name_parts[0]
  prompt_name = file_name_parts[1]
  entity = file_name_parts[2]
  offset = re.findall(r'\d+', file_name_parts[-1])[-1] 

  df = pd.read_csv(os.path.join(f'{OUTPUT_FOLDER}/metrics', file_name)) 
  entities = df['entity'].unique() 
  
  os.makedirs(f'{OUTPUT_FOLDER}/confusionmatrix/{model_name.replace(":", "_")}/{prompt_name}/{entity}', exist_ok=True) # creates a folder with the name of the model if it does not exist, replacing ':' with '_' to avoid issues with folder names

  # plot_confusion_matrix(calculate_results(df), f' Total Confusion Matrix - {model_name}', f'{OUTPUT_FOLDER}/confusionmatrix/{model_name.replace(":", "-")}/confusionmatrix-{model_name.replace(":", "-")}.png')

  for entity in entities: 
    plot_confusion_matrix(calculate_results(df[df['entity'] == entity]), f'Confusion Matrix {entity} - {model_name}_{offset}_{prompt_name}', f'{OUTPUT_FOLDER}/confusionmatrix/{model_name.replace(":", "_")}/{prompt_name}/{entity}/confusionmatrix-{model_name.replace(":", "-")}-{prompt_name}-{entity}-{offset}.png')



def main():
  selected_models = select_from_list(MODEL_NAMES, "Select the models to be tested:")
  selected_prompts = select_from_list(PROMPT_NAMES, "Select the prompts to be tested:")
  selected_entities = select_from_list(ENTITY_NAMES, "Select the entities to be tested:")
  calculate_results_intervals_option = ask_confirm('Do you want to calculate the metrics for each time interval?')
  calculate_total_results = ask_confirm('Do you want to calculate the total metrics for each model?')

  if calculate_results_intervals_option:
    for file in glob(f'{OUTPUT_FOLDER}/metrics/{",".join(selected_models)}/{",".join(selected_prompts)}/{",".join(selected_entities)}/*.csv'.replace(':', '_')): 
      calculate_model_result(file.replace(f'{OUTPUT_FOLDER}/metrics/', '')) 
  
  if calculate_total_results:

    for model in selected_models:
      for prompt in selected_prompts:
        for entity in selected_entities:
          files = glob(f'{OUTPUT_FOLDER}/metrics/{model}/{prompt}/{entity}/*.csv'.replace(':', '_'))
          total_table = [[0, 0], [0, 0]] 
          for file in files: 
            df = pd.read_csv(file) 
            total_table[0][0] += df['tn'].sum() 
            total_table[0][1] += df['fp'].sum() 
            total_table[1][0] += df['fn'].sum() 
            total_table[1][1] += df['tp'].sum()
                      
          
          os.makedirs(f'{OUTPUT_FOLDER}/confusionmatrix/{model.replace(":", "_")}/{prompt.replace(":", "_")}/{entity}', exist_ok=True)

          # MUDE AQUI PARA ALTERAR O NOME DO ARQUIVO DE SAÍDA, SE NECESSÁRIO
          title = ask_text(f'Enter the title for the total confusion matrix file for model: {model}, prompt: {prompt}, entity: {entity} (without extension):')
          # f'Total Confusion Matrix {entity} - {model}_{prompt}'
          plot_confusion_matrix(total_table, title, f'{OUTPUT_FOLDER}/confusionmatrix/{model.replace(":", "_")}/{prompt.replace(":", "_")}/{entity}/confusionmatrix-{model.replace(":", "-")}-{prompt.replace(":", "-")}-{entity}-total.png')

  else:
    print('No confusion matrix will be plotted. Exiting...')