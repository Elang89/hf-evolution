
COMMAND_LINE_DESCRIPTION = "Evolution CLI Tool"
COMMAND_LINE_OPTIONS = """nn <command> [<args>]

The most commonly used nn commands are:
    mine_datasets Mines dataset repositories for information
    mine_models   Mines model repositries for information 
    mine_products Mines hugging face's github repositories for information
    mine_issues   Mines 3 software repositories, 3 non-hugging face ML repositories and 3 hugging face repositories for issues
    mine_runs     Mines 3 software repositories, 3 non-hugging face ML repositories and 3 hugging face repositories for CI/CD runs
"""

CMD_MINE_REPOSITORIES = "This command will mine all the repositories from Hugging Face"
CMD_MINE_ISSUES = "This command will mine the issues from the main GitHub repositories"
CMD_MINE_RUNS = "This command will mine CI/CD runs from the main GitHub repositories"

COMMON_ARGS_VALIDATION_ERROR_INCORRECT_NUMBER = "Error: option value must be 1, 2 or 3."
COMMON_ARGS_VALIDATION_ERROR_NOT_INT = "Error: option value must be int, cannot be float or double"
COMMON_ARGS_VALIDATION_ERROR_NOT_A_NUMBER = "Error: option value must be a number from 1 to 3"

CONSUMER_KILL_SIG = "STOP" 