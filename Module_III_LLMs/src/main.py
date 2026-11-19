from InquirerPy.base.control import Choice

import confusion_matrix
import data_processing
import exploratory_analysis
from metrics.metrics import token_report_metrics
from metrics.tables import plot_time_intervals, plot_total_time
import test
from utils.cli import select_option


def main():
    option = select_option(
        message="What do you want to do?",
        choices=[
            Choice(value="1", name="1. Run tests"),
            Choice(value="2", name="2. Calculate metrics"),
            Choice(value="3", name="3. Generate charts"),
            Choice(value="4", name="4. Generate confusion matrices"),
            Choice(value="5", name="5. Exit"),
        ],
    )

    match option:
        case '1':
            test.main()
        case '2':
            data_processing.main()
        case '3':
            exploratory_analysis.menu()
        case '4':
            confusion_matrix.main()
        case '5':
            print('Exiting...')
        case _:
            print('Invalid option. Please select a valid option (1, 2, 3, 4 or 5).')


if __name__ == '__main__':
    # plot_total_time('qwen3_4b/prompt_2/names')
    # plot_time_intervals('luana_2b/prompt_9/names')
    # token_report_metrics(iterations=20)
    main()