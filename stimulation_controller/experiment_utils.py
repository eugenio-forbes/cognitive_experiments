"""
Experiment Utils

This code contains utilities like gathering valid user inputs.

"""
import sys
from configuration import *

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

### Function to gather whether stimulation will be delivered
def prompt_stimulation_enabled():
    valid_input = False
    while not valid_input:
        valid_input = True
        user_input = input("Will stimulation be delivered in this session? ([y]es/[n]o):")
        valid_responses = ['y','n']
        if user_input != '':
            if not user_input in valid_responses:
                valid_input = False
                print("Type 'y' or 'n'. Try again.")
            else:
                global stimulation_enabled
                if user_input == 'y':
                    stimulation_enabled = True
                else:
                    stimulation_enabled = False   
        else:
            valid_input = False
            print("Type 'y' or 'n'. Try again.")
    return stimulation_enabled

### Function to gather whether server connection is to be established
def prompt_server_connection_enabled():
    valid_input = False
    while not valid_input:
        valid_input = True
        user_input = input("Connect to server? ([y]es/[n]o):")
        valid_responses = ['y','n']
        if user_input != '':
            if not user_input in valid_responses:
                valid_input = False
                print("Type 'y' or 'n'. Try again.")
            else:
                if user_input == 'y':
                    server_connection_enabled = True
                else:
                    server_connection_enabled = False   
        else:
            valid_input = False
            print("Type 'y' or 'n'. Try again.")
    return server_connection_enabled

### Function for getting depth electrode labels of channels available for stimulation
def get_stimulation_labels(subject_configurations_folder):
    
    if not os.path.isdir(subject_configurations_folder):
        print(f"Error: Subject configurations folder '{subject_configurations_folder}' does not exist.")
        sys.exit(1)  # If the configurations are not in the correct folder then will exit task.
    
    subject_configurations_files = [file for file in os.listdir(subject_configurations_folder) if file.endswith('.csv')]
    stimulation_labels = [file_name[-6:-4] for file_name in subject_configurations_files]
    
    n_stimulation_labels = len(stimulation_labels)
    
    if n_stimulation_labels < 1:
        print(f"Error: Subject configurations folder'{subject_configurations_folder}' does not contain files.")
        sys.exit(1)  # If the configurations are not in the correct folder then will exit task.        
    
    return stimulation_labels

### Function to gather stimulation channel label
def prompt_stimulation_channel_label(subject):
    subject_configurations_folder = configurations_directory + subject + '/'
    potential_stimulation_sites = get_stimulation_labels(subject_configurations_folder)
    valid_input = False
    while not valid_input:
        valid_input = True
        print("Available stimulation sites:")
        print(potential_stimulation_sites)
        stimulation_label = input("Select and enter one of the above stimulation sites:")
        if stimulation_label != '':
            if not stimulation_label in potential_stimulation_sites:
                valid_input = False
                print("Input label is not part of available stimulation sites.")                
            else:
                valid_input = False
                print("Must enter one of available stimulation sites.")
    return stimulation_label