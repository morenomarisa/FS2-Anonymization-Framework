import json
import os
from pathlib import Path
import time

from config import ENTITY_NAMES, MODEL_NAMES, OUTPUT_FOLDER, PROMPT_NAMES
from data import entities
from llms import ollama
from prompts import prompts
from utils.cli import ask_number, ask_text, select_from_list

JSON_FORMAT = {
    "type": "object",
    "properties": {
        "resultados": {
            "type": "array",
            "items": {
                "type": "string",
                # Blocks strings that start with '{' (common in JSON/Dict)
                "pattern": "^[^{].*$",
                # ensures the string is not empty or just whitespace
                "minLength": 1
            }
        }
    },
    "required": ["resultados"],
    "additionalProperties": False
}

def test_prompt_execution(model_name: str, prompt_name: str, entity_name: str, quantity: str = 'ALL', offset: int = 0):
    """Tests the execution of a prompt with a given model and saves the results in a csv file.

    Args:
        model_name (str): Name of the model to be tested. The model must be available in the Ollama platform and compatible with the prompt being tested.
        prompt_name (str): Name of the prompt to be tested. The prompt must be available in the prompts module and compatible with the model being tested.
        entity_name (str): Name of the entity to be tested. The entity must be available in the entities module and compatible with the prompt being tested.
    """

    reports = entities.get_reports(quantity=quantity, offset=offset, sql_to_list=False) # get reports from database as a list of strings

    if len(reports) == 0:
        raise ValueError('No reports found in the database. Please check the database connection and the quantity and offset parameters.')

    prompt_text = prompts.load_prompt(prompt_name + '_' + entity_name).split('---') # load the prompt for the entity
    
    return_type = prompt_text[0].strip().lower() # the first part of the prompt is the return type, that is TAG or JSON

    system_prompt = prompt_text[1] # the second part of the prompt is the system prompt
    user_prompt = prompt_text[2] if len(prompt_text) > 2 else '{report}' # the third part of the prompt is the user prompt, if it exists, otherwise it is just the report

    with ollama.initialize(model_name, keep_alive=-1, temperature=0, top_k=40, top_p=0.9, seed=2306, repeat_penalty=1.2, num_ctx=4096, num_predict=9000, format=JSON_FORMAT if return_type == 'json' else None) as model: # initialize the model with the desired parameters

        folder_path = Path(f'{OUTPUT_FOLDER}/tests/{model_name.replace(":", "_")}/{prompt_name}/{entity_name}')
        folder_path.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILENAME = os.path.join(folder_path, f'tests_result_{model_name.replace(":", "_")}_{prompt_name}_{entity_name}_{offset}.csv')
        
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write("\"model\",\"prompt\",\"entity\",\"report_id\",\"response\",\"execution_time (s)\"\n")
        
        for i, (report_id, report) in enumerate(reports): # iterate over the reports to be used in the tests, report_id is the id of the report and report is the text of the report
            start_time = time.perf_counter()
            
            try: 
                response = ollama.execute(model, user_prompt, system_prompt, {'report': report[0]}) # execute the prompt with the report as input and get the response from the model
                
                response_content = response.content.replace('\n', '')
            except Exception as e:    
                print('O teste excedeu o limite de tokens processados!', e)
                response_content = json.dumps({'resultados':[]}) 
            
            finally:
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                 
                

            results = [model_name, prompt_name, entity_name, report_id, response_content, execution_time] # add the results of the test to the DataFrame
            print(f'finished {i+1} of {len(reports)} in {execution_time:.2f} seconds') # print the progress of the tests
            
            with open(OUTPUT_FILENAME, 'a', encoding='utf-8') as f:
                f.write(",".join([f"\"{str(result).replace('\"', '\"\"')}\"" for result in results]) + "\n") 


def main() -> None:   
    """Displays a menu to select the models, prompts, quantity of reports and intervals of reports to be used in the tests and calls the test_prompt_execution function with the selected options.
    """
    selected_models = select_from_list(MODEL_NAMES, "Select the models to be tested:")
    selected_prompts = select_from_list(PROMPT_NAMES, "Select the prompts to be tested:")
    selected_entities = select_from_list(ENTITY_NAMES, "Select the entities to be tested:")
    start = ask_number("Inform the starting point of the reports to be used in the tests:", min_allowed=0, default=0)
    quantity = ask_text("Inform the quantity of reports to be used in the tests (type ALL to use all reports):", default="ALL").strip()
    intervals = ask_number("Inform the number of tests to be executed:", min_allowed=1, default=1)

    for model in selected_models:
        for prompt in selected_prompts:
            for entity in selected_entities:
                    i = 0
                    while quantity == 'ALL' or i < intervals:
                        try:
                            print(f'\nExecuting tests for model: {model}, prompt: {prompt}, entity: {entity}\n')
                            test_prompt_execution(model, prompt, entity, quantity=quantity if quantity == 'ALL' else int(quantity), offset=start +i*int(quantity) if quantity != 'ALL' else 0)
                        #except ValueError: 
                        #    break
                        except Exception as e:
                            print(f'Error occurred while executing tests for model: {model}, prompt: {prompt}, entity: {entity}, error: {e.with_traceback(None)}\n')
                            break
                        i += 1

if __name__ == '__main__':
    main()