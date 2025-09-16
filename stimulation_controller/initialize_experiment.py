"""
Initialization of Stimulation Controller GUI

This code will take configurations for locations, amplitudes, frequencies, 
pulse widths to enable their selection in GUI.

"""
import pandas as pd
import itertools
import random
import json
import os
import time
from csv import DictReader
from datetime import datetime
from configuration import *
from experiment_utils import *
from message_dictionary import *
from re import search

########################################################################################################################################################################

def initialize_experiment_func(subject, session, session_directory):
    
    ### Define session files
    pulses_file = session_directory + 'pulses.csv'
    events_file = session_directory + 'events.csv'
    notes_file = session_directory + 'notes.csv'
    communications_file = session_directory + 'communications.csv'
    configurations_file = session_directory + 'configurations.json'
    message_dictionary_file = session_directory + 'message_dictionary.json'
    parameters_file = session_directory + 'possible_stimulation_parameters.json'
    stimulation_locations_file = configurations_directory + subject + '/' + subject + '_stimulation_locations.csv'
    
    ### Read subjects list of locations to define parameter lists
    with open(stimulation_locations_file, 'r') as file_handle:
        csv_reader = DictReader(file_handle, fieldnames=location_fieldnames)
        locations = list(csv_reader)
    
    labels = [location['label'] for location in locations]

    ### All possible parameter values added to dictionary
    possible_stimulation_parameters = {
        'label': labels,
        'location': locations,
        'amplitude': amplitudes,
        'frequency': frequencies,
        'pulse_width': pulse_widths,
        'duration': durations
    }

    ### Single set of parameters added to a dictionary that will be used to send messages to Blackrock
    stimulation_parameters = {
        'location': locations[0],
        'amplitude': amplitudes[0],
        'frequency': frequencies[0],
        'pulse_width': pulse_widths[0],
        'duration': durations[0]
    }
    
    ### Save lists of possible parameters
    with open(parameters_file, 'w') as file_handle:
            json.dump(possible_stimulation_parameters, file_handle)

    ### Save current configurations from configuration.py
    with open(configurations_file, 'w') as file_handle:
        json.dump(configuration_dictionary, file_handle)

    ### Initialize files that will store experiment data as it is being executed
    if not os.path.isfile(pulses_file):
        pd.DataFrame(columns=pulses_fieldnames).to_csv(pulses_file, index=False, header=True)
    
    if not os.path.isfile(events_file):
        pd.DataFrame(columns=events_fieldnames).to_csv(events_file, index=False, header=True)
    
    if not os.path.isfile(notes_file):
        pd.DataFrame(columns=notes_fieldnames).to_csv(notes_file, index=False, header=True)
    
    if not os.path.isfile(communications_file):
        pd.DataFrame(columns=communications_fieldnames).to_csv(communications_file, index=False, header=True)

    ### Initialize and save message dictionary used in server-client communications
    message_dictionary = get_message_dictionary(subject, session, stimulation_parameters)
    with open(message_dictionary_file, 'w') as file_handle:
        json.dump(message_dictionary, file_handle)

    ### Allow some time for files to be written before accessing
    time.sleep(0.5)

### Function can be executed independently to test initialization (each session has a unique date as folder name).
if __name__ == '__main__':
    
    ### Prompt valid subject code
    subject_code = prompt_subject_code()

    ### Create new folder for saving parameter lists, configurations, and events files using date and time as name of folder
    current_time = datetime.now().strftime(datetime_format)
    session = current_time
    session_directory = data_directory + subject + '/'+ session + '/'

    ### Generate list of possible stimuli parameters and dictionary with messages and events
    if not os.path.exists(session_directory):
        os.makedirs(session_directory)
    initialize_experiment_func(subject, session, session_directory)