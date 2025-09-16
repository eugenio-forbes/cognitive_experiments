"""
Get Experiment Session Data

SMILE creates new folder each time experiment is run, and pickles a dictionary before writing to .slog file.
This code will use SMILE's log2dl function to retrieve data from .slog files and append it to .csv files for a session.
This will allow for multiple experiment runs for a single session (in case there is a break or an interruption).
Code can also be run independently in the case were there is an error impeding file transfer.

"""
from smile.log import log2dl
import time
import os
import pandas as pd
from configuration import *
from experiment_utils import *

########################################################################################################################################################################

### Matching smile log and .csv file names, this function will loop through all SMILE log instances
### and append their data to corresponding .csv files

def append_log_to_csv(new_session_log, file_key, csv_file_info):
    csv_file, fieldnames = csv_file_info
    smile_log_index = 0
    file_exists = True
    data = pd.DataFrame(columns=fieldnames)
    while file_exists:
        smile_log_file = new_session_log + f'log_{file_key}_{smile_log_index}.slog'
        file_exists = os.path.isfile(smile_log_file)
        if file_exists:
            data_block = pd.DataFrame(log2dl(smile_log_file))
            data = pd.concat([data, data_block.reindex(columns=fieldnames)], ignore_index=True)
        smile_log_index += 1
    if not data.empty:
        data = data.sort_values(by='log_time')
        data.to_csv(csv_file, mode='a', index=False, header=False)

def get_experiment_data_func(new_session_log, smile_log_directory, file_dictionary):
    
    smile_log_files = os.listdir(smile_log_directory)

    ### Transfer all SMILE log files to session directory for better management
    if not os.path.exists(new_session_log):
        os.makedirs(new_session_log)
    for file in smile_log_files:        
        os.rename(smile_log_directory + file, new_session_log + file)
    print(f"Success! Log files transferred to {new_session_log}.")
    time.sleep(1)

    for file_key, csv_file_info in file_dictionary.items():
        append_log_to_csv(new_session_log, file_key, csv_file_info)

########################################################################################################################################################################

### Function can be executed independently from experiment after session runs in case files were not transferred
if __name__ == '__main__':

    ### Gather a valid subject code:
    subject = prompt_subject_code()
        
    ### Gather a valid session number:
    session = prompt_session_number()

    ### Gather valid SMILE log folder datetime name:
    date = prompt_datetime_folder_name()

    ### Definition of session directories and files        
    session_directory = data_directory + subject + '/session_'+ session + '/'
    session_logs = session_directory + 'session_logs/'
    checkpoint_file = session_directory + 'checkpoint.csv'
    pulses_file = session_directory + 'pulses.csv'
    events_file = session_directory + 'events.csv'
    timing_file = session_directory + 'timing.csv'
    delays_file = session_directory + 'delays.csv'
    smile_log_directory = test_directory + date + '/'
    new_session_log = session_logs + date + '/'

    file_dictionary = {
        'pulse': (pulses_file, pulses_fieldnames),
        'event': (events_file, events_fieldnames),
        'timing': (timing_file, timing_fieldnames),
        'checkpoint': (checkpoint_file, checkpoint_fieldnames),
        'delay': (delays_file, delays_fieldnames)
    }

    ### If there is no smile log for specified date, ask user to try again
    if not os.path.isdir(smile_log_directory):
        print(f"Specified SMILE log folder {smile_log_directory} does not exist. Try again.")
        quit()

    ### If specified session directory does not exist, ask user whether to create new folder
    if not os.path.isdir(session_directory):
        create_new_folder = prompt_new_folder_creation()
        if not create_new_folder:
            print("Data transfer cancelled.")
            quit()

    ### If files already exist, verify from user whether to append to existing
    checkpoint_exist = os.path.isfile(checkpoint_file)
    pulses_exist = os.path.isfile(pulses_file)
    events_exist = os.path.isfile(events_file)
    timing_exist = os.path.isfile(timing_file)
    delays_exist = os.path.isfile(delays_file)
    files_exist = checkpoint_exist or pulses_exist or events_exist or timing_exist or delays_exist

    if files_exist:
        append_to_files = prompt_append_to_files()
        if not append_to_files:
            print("Data transfer cancelled.")
            quit()
    
    ### Initiate transfer of data files 
    if not os.path.isdir(session_directory):
        os.makedirs(session_directory)
    if not os.path.isdir(session_logs):    
        os.makedirs(session_logs)
    if not checkpoint_exist:
        pd.DataFrame(columns=checkpoint_fieldnames).to_csv(checkpoint_file, index=False, header=True)
    if not pulses_exist:
        pd.DataFrame(columns=pulses_fieldnames).to_csv(pulses_file, index=False, header=True)
    if not events_exist:
        pd.DataFrame(columns=events_fieldnames).to_csv(events_file, index=False, header=True)
    if not timing_exist:
        pd.DataFrame(columns=timing_fieldnames).to_csv(timing_file, index=False, header=True)
    if not delays_exist:
        pd.DataFrame(columns=delays_fieldnames).to_csv(delays_file, index=False, header=True)
    
    get_experiment_data_func(new_session_log, smile_log_directory, file_dictionary)