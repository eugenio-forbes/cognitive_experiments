"""
Experiment Utils

This code contains utilities like gathering valid user inputs and returning experiment trial list from checkpoint.

"""
from configuration import *
from csv import DictReader

#########################################################################################################################################################################

### Function to prevent execution of session once all trials have been completed
def lock_session(session_lock_file):
    lock_file = open(session_lock_file, 'w')
    lock_file.close()

### Function to gather a valid subject code based on configurations
def prompt_subject_code():
    valid_input = False    
    while not valid_input:   
        valid_input = True
        subject = input(f"Enter subject code ({valid_subject_code_prefix}###):")
        if subject != '':
            invalid_condition1 = subject[0:prefix_length] != valid_subject_code_prefix
            invalid_condition2 = len(subject) != valid_subject_code_length
            invalid_condition3 = not subject[prefix_length:valid_subject_code_length].isnumeric()
            invalid_subject_code = invalid_condition1 or invalid_condition2 or invalid_condition3
            if  invalid_subject_code:
                valid_input = False
                print(f"Subject code must be entered as {valid_subject_code_prefix}###. Try again.")
        else:
            valid_input = False
            print("Must enter a subject code. Try again.")
    return subject

### Function to gather valid session number        
def prompt_session_number():
    valid_input = False
    while not valid_input:
        valid_input = True
        session = input("Enter session number:")
        if session != '':
            if not session.isnumeric():
                valid_input = False
                print("Must enter an integer number. Try again.")
        else:
            valid_input = False
            print("Must enter session number. Try again.")
    return session

### Function to prompt valid number of experiment blocks
def prompt_n_experiment_blocks():
    valid_input = False
    while not valid_input:
        valid_input = True
        n_experiment_blocks = input("Enter number of experiment blocks in addition to practice for this session (0-6):")
        if n_experiment_blocks != '':
            if not n_experiment_blocks.isnumeric() or int(n_experiment_blocks) < 0 or int(n_experiment_blocks) > 6:
                valid_input = False
                print("Must enter an integer between 0 and 6. Try again.")
        else:
            valid_input = False
            print("Must enter number of experiment_blocks for this session. Try again.")
    return int(n_experiment_blocks)
    
### Function to determine whether user input valid datetime format
def is_valid_datetime(date_string):
    datetime_format='%Y%m%d_%H%M%S'
    try:
        datetime.strptime(date_string, datetime_format)
        return True
    except ValueError:
        return False

### Function to gather correctly formatted SMILE log folder datetime name
def prompt_datetime_folder_name():
    valid_input = False
    while not valid_input:
        valid_input = True
        date = input("Enter datetime (YYYYMMDD_HHMMSS) of SMILE log folder for session:")
        if date != '':
            if not is_valid_datetime(date):
                valid_input = False
                print("Datetime was not entered in valid format. Try again.")
        else:
            valid_input = False
            print("Must enter SMILE log folder datetime. Try again.") 
    return date

### Function to prompt whether to create new folder
def prompt_new_folder_creation():
    valid_input = False
    valid_responses = ['y', 'n']
    while not valid_input:
        valid_input = True
        response = input("Create folder for specified session? (y/n)")
        if response != '':
            if not response in valid_responses:
                valid_input = False
                print("Invalid response. Must be 'y' or 'n'. Try again.")
            elif response == 'n':
                return False
        else:
            valid_input = False
            print("Invalid response. Must be 'y' or 'n'. Try again.")
    return True

### Function to return experiment block list from appropriate starting point based on saved checkpoint
def update_list_from_checkpoint(experiment_block_list, checkpoint_file, session_lock_file):
    skip_study_phase = False
    last_experiment_block = None
    last_experiment_phase = None
    last_trial_index = None

    ### Iterate over each line as an ordered dictionary
    with open(checkpoint_file, 'r') as file_handle:
        csv_dict_reader = DictReader(file_handle)
        for row in csv_dict_reader:
            last_experiment_block = int(row['experiment_block'])
            last_experiment_phase = row['experiment_phase']
            last_trial_index = int(row['trial_index'])
   
    ### Use gathered checkpoint information to remove previous items from trial list
    if last_experiment_block is not None:
        if last_experiment_phase == 'ENCODING':
            if last_trial_index + 1 < len(experiment_block_list[0]['study_phase']):
                new_study_phase = experiment_block_list[last_experiment_block]['study_phase'][last_trial_index + 1:]
                experiment_block_list[last_experiment_block]['study_phase'] = new_study_phase
                experiment_block_list = experiment_block_list[last_experiment_block:]
            else:
                skip_study_phase = True
                experiment_block_list = experiment_block_list[last_experiment_block:]
        else:
            if last_trial_index + 1 < len(experiment_block_list[0]['test_phase']):
                skip_study_phase = True
                new_test_phase = experiment_block_list[last_experiment_block]['test_phase'][last_trial_index + 1:]
                experiment_block_list[last_experiment_block]['test_phase'] = new_test_phase
                experiment_block_list = experiment_block_list[last_experiment_block:]
            else:
                if last_experiment_block + 1 < len(experiment_block_list):
                    experiment_block_list = experiment_block_list[last_experiment_block + 1:]
                else:
                    lock_session(session_lock_file)
                    print("Subject had already completed session.")
                    print("Locking session.")
                    quit()
    
    return experiment_block_list, skip_study_phase