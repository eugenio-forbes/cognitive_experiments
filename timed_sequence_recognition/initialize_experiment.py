"""
Initialization of Timed Sequence Recognition Experiment

This code will generate up to 45 trials consisting of two pairs of sequences. 
Sequences in each pair share the same images of two celebrities, but differ 
in the time interval of a blank image separating their display. Each of the
four sequences is associated to a unique emoji image. The sequences are randomized
during the study phase. For the test phase, a random sequence is selected and
displayed without corresponding emoji. User must select the emoji associated
to this sequence. Positions for selection between emojis are randomized.

"""
import pandas as pd
import random
import json
import os
import time

from configuration import *
from experiment_utils import *

########################################################################################################################################################################

def initialize_experiment_func(subject, session, session_directory, n_experiment_blocks):

    ### Define session files
    checkpoint_file = session_directory + 'checkpoint.csv'
    pulses_file = session_directory + 'pulses.csv'
    events_file = session_directory + 'events.csv'
    timing_file = session_directory + 'timing.csv'
    delays_file = session_directory + 'delays.csv'
    experiment_block_list_file = session_directory + 'experiment_block_list.json'
    configurations_file = session_directory + 'configurations.json'

    ### Item emojis presented are randomly sampled
    with open(emoji_list_file, 'r') as file_handle:
        emojis = file_handle.read().split()
    random.shuffle(emojis)
    
    ### Celebrity faces presented are randomly sampled
    with open(celebrity_list_file, 'r') as file_handle:
        faces = file_handle.read().split()
    random.shuffle(faces)

    ### Organize images into a list of experiment blocks consisting of study and test phases
    
    experiment_block_list = []

    for trial_index in range(n_experiment_blocks):

        # Four emojis and four faces per trial. 
        # One emoji for each sequence, two faces for each pair of sequences differing in blank interval duration
        
        block_number = str(trial_index)

        study_phase = []
    
        trial_emojis = emojis[trial_index * 4:(trial_index + 1) * 4]
        trial_faces = faces[trial_index * 4:(trial_index + 1) * 4]

        sequence_A_long = {
            'subject': subject,
            'session': session,
            'experiment_block': block_number,
            'experiment_phase': 'ENCODING',
            'sequence_index': -1,
            'sequence_group': 'A',
            'interval_type': 'long',
            'emoji': trial_emojis[0],
            'face1': trial_faces[0],
            'interval': long_blank_duration,
            'face2': trial_faces[1]
            }
    
        sequence_A_short = {
            'subject': subject,
            'session': session,
            'experiment_block': block_number,
            'experiment_phase': 'ENCODING',
            'sequence_index': -1,
            'sequence_group':'A',
            'interval_type': 'short',
            'emoji': trial_emojis[1],
            'face1': trial_faces[0],
            'interval': short_blank_duration,
            'face2': trial_faces[1]
            }
    
        sequence_B_long = {
            'subject': subject,
            'session': session,
            'experiment_block': block_number,
            'experiment_phase': 'ENCODING',
            'sequence_index': -1,
            'sequence_group': 'B',
            'interval_type': 'long',
            'emoji': trial_emojis[2],
            'face1': trial_faces[2],
            'interval': long_blank_duration,
            'face2': trial_faces[3]
            }
    
        sequence_B_short = {
            'subject': subject,
            'session': session,
            'experiment_block': block_number,
            'experiment_phase': 'ENCODING',
            'sequence_index': -1,
            'sequence_group':'B',
            'interval_type': 'short',
            'emoji': trial_emojis[3],
            'face1': trial_faces[2],
            'interval': short_blank_duration,
            'face2': trial_faces[3]
            }
    
        ### Study phase as list of dictionaries defining the sequences
        study_phase.append(sequence_A_long)
        study_phase.append(sequence_A_short)
        study_phase.append(sequence_B_long)
        study_phase.append(sequence_B_short)

        ### Shuffle study phase and randomly pick test sequence 
        random.shuffle(study_phase)
        for index, sequence in enumerate(study_phase):
            sequence['sequence_index'] = index
        sequence_selected = random.randint(0, 3)
        test_sequence = study_phase[sequence_selected]

        ### Shuffle trial emojis to randomize their position for selection of test phase response
        test_phase_emojis = trial_emojis.copy()
        random.shuffle(test_phase_emojis)

        if test_sequence['emoji'] == test_phase_emojis[0]:
            correct_response = 'top_left'
        elif test_sequence['emoji'] == test_phase_emojis[1]:
            correct_response = 'top_right'
        elif test_sequence['emoji'] == test_phase_emojis[2]:
            correct_response = 'bottom_left'
        elif test_sequence['emoji'] == test_phase_emojis[3]:
            correct_response = 'bottom_right'
        
        ### Test phase as nested dictionary
        test_phase = {
            'subject': subject,
            'session': session,
            'experiment_block': block_number,
            'experiment_phase': 'RETRIEVAL',
            'sequence': test_sequence,
            'emojis': test_phase_emojis,
            'correct_response': correct_response}

        ### Trial as nested dictionary
        experiment_block = {
            'subject': subject,
            'session': session,
            'experiment_block': block_number,
            'study_phase': study_phase,
            'test_phase': test_phase}

        ### Append trial to experiment block list
        experiment_block_list.append(experiment_block)
    
    ### Save trial list to be used for the experiment session
    with open(experiment_block_list_file, 'w') as file_handle:
        json.dump(experiment_block_list, file_handle)

    ### Save configurations used for the experiment session
    with open(configurations_file, 'w') as file_handle:
        json.dump(configuration_dictionary, file_handle)
    
    ### Initialize .csv files to which data on trials will be added after execution of the experiment
    ### Initialize .csv's to store experiment data after the execution of the experiment

    if not os.path.isfile(checkpoint_file):
        pd.DataFrame(columns=checkpoint_fieldnames).to_csv(checkpoint_file, index=False, header=True)
    
    if not os.path.isfile(pulses_file):
        pd.DataFrame(columns=pulses_fieldnames).to_csv(pulses_file, index=False, header=True)

    if not os.path.isfile(events_file):
        pd.DataFrame(columns=events_fieldnames).to_csv(events_file, index=False, header=True)

    if not os.path.isfile(timing_file):
        pd.DataFrame(columns=timing_fieldnames).to_csv(timing_file, index=False, header=True)

    if not os.path.isfile(delays_file):
        pd.DataFrame(columns=delays_fieldnames).to_csv(delays_file, index=False, header=True)
    
    ### Allow some time for writing of files before accessing them
    time.sleep(0.5)

########################################################################################################################################################################

### Function can be executed independently from experiment prior to start to review files and experiment block list
if __name__ == '__main__':
    
    ### Prompt subject and session information from user for easier file management
    ### and to enable starting a session from a completed checkpoint.

    ### Gather a valid subject code:
    subject = prompt_subject_code()
        
    ### Gather a valid session number:
    session = prompt_session_number()
        
    session_directory = data_directory + subject + '/session_'+ session + '/'
    session_logs = session_directory + 'session_logs/'

    ### Create list of trials if the experimental session had never been initialized
    if not os.path.isdir(session_directory):
        os.makedirs(session_directory)
        os.makedirs(session_logs)
        ### Gather a valid number of experiment blocks (1-45) to be performed in this session
        n_experiment_blocks = prompt_n_experiment_blocks()
        initialize_experiment_func(subject, session, session_directory, n_experiment_blocks)
    else:
        print(f"Session {session} for subject {subject} had already been initialized. Verify and try again.")