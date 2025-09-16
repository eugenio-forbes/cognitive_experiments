"""
Initialization of Stimulation Parameter Search Experiment

This code will take configurations for locations, amplitudes, frequencies, 
pulse widths, and number of trials per combination, to generate a randomized 
list of trials with combinations for these stimulation parameters. 
A fraction of sham trials is controlled troughout experiment runtime.

"""

import pandas as pd
import itertools
import random
import json
import os
import sys
import time
from datetime import datetime
from csv import DictReader

### Import configuration and message dictionary
from configuration import *
from message_dictionary import*

########################################################################################################################################################################

def initialize_experiment_func(subject, session, session_directory, stimulation_label):
    
    ### Define session files
    checkpoint_file = session_directory + 'checkpoint.csv'
    pulses_file = session_directory + 'pulses.csv'
    events_file = session_directory + 'events.csv'
    ratings_file = session_directory + 'psych_ratings.csv'
    scores_file = session_directory + 'psych_scores.csv'
    communications_file = session_directory + 'communications.csv'
    configurations_file = session_directory + 'configurations.json'
    message_dictionary_file = session_directory + 'message_dictionary.json'
    stimulus_list_file = session_directory + 'stimulus_list.json'
    stimulation_locations_file = configurations_directory + subject + '/' + subject + '_stimulation_locations_' + stimulation_label + '.csv'


    ### Only saving configurations and stimuli list if stimulation was enabled in session
    if stimulation_label != 'none':
        
        ### Retrieve stimulation locations from file selected by user to produce stimulus list
        with open(stimulation_locations_file, 'r') as file_handle:
            csv_reader = DictReader(file_handle, fieldnames=location_fieldnames)
            stimulation_locations = list(csv_reader)
    
        ### Single set of parameters added to a dictionary that will be used to send messages to Blackrock computer
        stimulation_parameters = {
            'location': stimulation_locations[0],
            'amplitude': amplitudes[0],
            'frequency': frequencies[0],
            'pulse_width': pulse_widths[0],
            'duration': stimulation_duration
        }

        ### Save a shuffled list of combinations of stimulation parameters with enough trials per combination
        parameter_combinations = itertools.product(stimulation_locations, amplitudes, frequencies, pulse_widths)
        stimulus_list = [dict(zip(parameter_fieldnames, combination)) for combination in parameter_combinations]
        stimulus_list = stimulus_list * trials_per_combination
        max_trial_index = len(stimulus_list)
        random.shuffle(stimulus_list)

        with open(stimulus_list_file, 'w') as file_handle:
            json.dump(stimulus_list, file_handle)

        ### Save current configurations from configuration.py
        with open(configurations_file, 'w') as file_handle:
            json.dump(configuration_dictionary, file_handle)
    
    ### Initialize files that will store experiment data as it is being executed
    if not os.path.isfile(checkpoint_file):
        pd.DataFrame(columns=checkpoint_fieldnames).to_csv(checkpoint_file, index=False, header=True)
    
    if not os.path.isfile(pulses_file):
        pd.DataFrame(columns=pulses_fieldnames).to_csv(pulses_file, index=False, header=True)
    
    if not os.path.isfile(events_file):
        pd.DataFrame(columns=events_fieldnames).to_csv(events_file, index=False, header=True)
    
    if not os.path.isfile(ratings_file):
        pd.DataFrame(columns=ratings_fieldnames).to_csv(ratings_file, index=False, header=True)
    
    if not os.path.isfile(scores_file):
        pd.DataFrame(columns=scores_fieldnames).to_csv(scores_file, index=False, header=True)
    
    if not os.path.isfile(communications_file):
        pd.DataFrame(columns=communications_fieldnames).to_csv(communications_file, index=False, header=True)
    
    ### Initialize and save message dictionary used in server-client communications
    if stimulation_label != 'none':
        message_dictionary = get_message_dictionary(subject, session, stimulation_parameters)
    else:
        message_dictionary = get_message_dictionary(subject, session)
    
    with open(message_dictionary_file, 'w') as file_handle:
        json.dump(message_dictionary, file_handle)

    ### Allow some time for files to be written before accessing
    time.sleep(0.5)

### Function can be executed independently to test initialization (each session has a unique date as folder name).
if __name__ == '__main__':
    
    ### Prompt valid subject code
    subject_code = prompt_subject_code()

    ### Prompt whether stimulation is enabled
    stimulation_enabled = prompt_stimulation_enabled()

    ### If stimulation is to be delivered, prompt for picking depth electrode label
    if stimulation_enabled:
        stimulation_label = prompt_stimulation_channel_label(subject)
    else:
        stimulation_label = 'none'

    ### Create new folder for saving trial list, configurations, and events files using date and time as name of folder
    current_time = datetime.now().strftime(datetime_format)
    session = current_time
    session_directory = data_directory + subject + '/'+ session + '/'

    ### Generate stimulation trial list and dictionary with messages and events
    if not os.path.exists(session_directory):
        os.makedirs(session_directory)
    initialize_experiment_func(subject, session, session_directory, stimulation_label)