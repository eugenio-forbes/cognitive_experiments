"""
Initialization of Time Associative Recognition Experiment
This code will generate a randomized and balanced list of
experimental stimuli (celebrity faces, time intervals) to
be executed during the study and test phases of the
experiment
"""

import pandas as pd
import random
import json
import os
import time
from configuration import *

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
    session_keys_file = session_directory + 'session_keys_dictionary.json'

    ### Organize a randomized list of stimuli (images) to be presented during the experiment
    
    ### Test conditions in which a face or intervening time between emoji and face in a sequence (or both) changes
    face_changes = ['face', 'both']
    time_changes = ['time', 'both']
    
    ### Item emojis presented are randomly sampled and balanced based on whether they are organic or inorganic
    organic_emojis = open(list_directory + 'organic_emojis.txt').read().split()
    random.shuffle(organic_emojis)
    inorganic_emojis = open(list_directory + 'inorganic_emojis.txt').read().split()
    random.shuffle(inorganic_emojis)
    
    ### Celebrity faces presented are randomly sampled and balanced based on whether they are male or female
    male_faces = open(list_directory + 'male_celebrities.txt').read().split()
    random.shuffle(male_faces)
    female_faces = open(list_directory + 'female_celebrities.txt').read().split()
    random.shuffle(female_faces)
    
    ### Distribute items, celebrities, test conditions (intervals and changes) into up to 7 blocks of 24 trials each:
    experiment_blocks = list(range(0, 7)) * 24
    items = organic_emojis[0:84] + inorganic_emojis[0:84]
    item_categories = ['organic'] * 84 + ['inorganic'] * 84
    celebrity_faces = male_faces[0:42] + female_faces[0:42] + male_faces[42:84] + female_faces[42:84]
    celebrity_genders = ['male'] * 42 + ['female'] * 42 + ['male'] * 42 + ['female'] * 42
    interval_types = ['short', 'long'] * 84
    test_conditions = (['none'] * 21 + ['time'] * 7 + ['face'] * 7 + ['both'] * 7) * 4
    
    sequence_columns = ['experiment_block', 'item', 'item_category', 'celebrity_face', 'celebrity_gender', 'interval_type', 'test_condition']

    ### Zip distributed items into dataframe to create table of study phase trials indicating their corresponding
    ### block, stimuli (item, face, interval) and their corresponding experimental test condition
    sequences = list(zip(experiment_blocks, items, item_categories, celebrity_faces, celebrity_genders, interval_types, test_conditions))
    sequences = pd.DataFrame(sequences, columns=sequence_columns)
    
    ### Loop through each study block to generate their corresponding test block based on the
    ### experimental condition of each trial, randomizing again their order for the test phase
    
    experiment_block_list = []
    for block_number in range(n_experiment_blocks + 1):
        
        block_sequences = sequences[sequences['experiment_block'] == block_number]

        study_sequences = block_sequences.copy()
        
        ### Randomize the order of the sequences presented during study
        study_sequences = study_sequences.sample(frac=1).reset_index(drop=True)
        
        ### For trials with test condition of changing celebrity face associated to an item,
        ### randomly swap faces between these
        with_face_change = block_sequences[block_sequences['test_condition'].isin(face_changes)]
        without_face_change = block_sequences[~block_sequences['test_condition'].isin(face_changes)]
        changed_faces = rearrange_faces(with_face_change, male_faces, sequence_columns)
        halfway_there = pd.concat([changed_faces, without_face_change], ignore_index=True)
        
        ### Change time interval between item and celebrity for trials with this experimental condition
        changing_times = halfway_there[halfway_there['test_condition'].isin(time_changes)]
        same_times = halfway_there[~halfway_there['test_condition'].isin(time_changes)]
        new_times = switch_time(changing_times, sequence_columns)
        test_sequences = pd.concat([new_times, same_times], ignore_index=True)
        
        ### Now that experimental conditions have been applied, randomize order of test trials
        test_sequences = test_sequences.sample(frac=1).reset_index(drop=True)
        shuffled_study_sequences = study_sequences.itertuples(index=False)
        shuffled_test_sequences = test_sequences.itertuples(index=False)
        
        ### Set shuffled study and test trials with corresponding trial index into a nested dictionary
        ### corresponding to an experimental block and append it to experiment block list
        trial_index = 0
        study_phase = []
        for _, item, item_category, celebrity_face, celebrity_gender, interval_type, test_condition in shuffled_study_sequences:
            
            if interval_type == 'long':
                interval = long_blank_duration
            else:
                interval = short_blank_duration

            trial = {
                'subject': subject,
                'session': session,
                'experiment_block': str(block_number),
                'experiment_phase': 'ENCODING',
                'trial_index': trial_index,
                'item': item,
                'item_category': item_category,
                'celebrity_face': celebrity_face,
                'celebrity_gender': celebrity_gender,
                'interval': interval,
                'interval_type': interval_type,
                'test_condition': test_condition
            }

            study_phase.append(trial)
            trial_index += 1
        
        trial_index = 0
        test_phase = []
        for _, item, item_category, celebrity_face, celebrity_gender, interval_type, test_condition in shuffled_test_sequences:
            
            if interval_type == 'long':
                interval = long_blank_duration
            else:
                interval = short_blank_duration

            trial = {
                'subject': subject,
                'session': session,
                'experiment_block': str(block_number),
                'experiment_phase': 'RETRIEVAL',
                'trial_index': trial_index,
                'item': item,
                'item_category': item_category,
                'celebrity_face': celebrity_face,
                'celebrity_gender': celebrity_gender,
                'interval': interval,
                'interval_type': interval_type,
                'test_condition': test_condition
            }

            test_phase.append(trial)
            trial_index += 1
        
        experiment_block = {
            'subject': subject,
            'session': session,
            'experiment_block': str(block_number),
            'study_phase': study_phase,
            'test_phase': test_phase
        }

        experiment_block_list.append(experiment_block)
    
    ### Randomization of study and test phase responses associated to left or right keys
    if random.randint(0,1) == 0:
        organic_key = left_key
        inorganic_key = right_key
        study_left_label = 'ORGANIC'
        study_right_label = 'INORGANIC'
    else:
        organic_key = right_key
        inorganic_key = left_key
        study_right_label = 'ORGANIC'
        study_left_label = 'INORGANIC'

    if random.randint(0,1) == 0:
        same_key = left_key
        different_key = right_key
        test_left_label = 'SAME'
        test_right_label = 'DIFFERENT'
    else:
        same_key = right_key
        different_key = left_key
        test_right_label = 'SAME'
        test_left_label = 'DIFFERENT'

    session_keys_dictionary = {
        'organic_key': organic_key,
        'inorganic_key': inorganic_key,
        'study_left_label': study_left_label,
        'study_right_label': study_right_label,
        'same_key': same_key,
        'different_key': different_key,
        'test_left_label': test_left_label,
        'test_right_label': test_right_label
    }

    ### Save experiment block list to be used for the experiment session
    with open(experiment_block_list_file, 'w') as file_handle:
        json.dump(experiment_block_list, file_handle)

    ### Save configurations used for the experiment session
    with open(configurations_file, 'w') as file_handle:
        json.dump(configuration_dictionary, file_handle)
    
    ### Save key assignment for this session
    with open(session_keys_file, 'w') as file_handle:
        json.dump(session_keys_dictionary, file_handle)
    
    ### Initialize .csv files to which data on trials will be added after execution of the experiment
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


### Function to produce random derangement of celebrity faces
def rearrange_faces(faces_to_change, male_faces, sequence_columns):
    ftc = faces_to_change.to_records(index=False)
    tup_list = list(ftc)
    block, item, category, faces_in_question, gender, interval, change = zip(*tup_list)
    rearranged_faces = list(faces_in_question)
    random.shuffle(rearranged_faces)
    all_shuffled = False
    while not all_shuffled: ### Probability of successful derangement ~ 1/e ~ 0.37, so keeping like this
        all_shuffled = True
        random.shuffle(rearranged_faces)
        for x in range(len(rearranged_faces)):
            if rearranged_faces[x] == faces_in_question[x]:
                all_shuffled = False
    new_gender = switch_gender(rearranged_faces, male_faces)
    new_tup = list(zip(block, item, category, list(rearranged_faces), list(new_gender), interval, change))
    changed_faces = pd.DataFrame(new_tup, columns=sequence_columns)
    return changed_faces

### Function to determine gender of shuffled faces to change information of corresponding trial
def switch_gender(question_mark, male_faces):
    new_gender = []
    for this_face in question_mark:
        if this_face in male_faces:
            new_gender.append('male')
        else:
            new_gender.append('female')
    return new_gender

### Function to change time interval of trials with corresponding experimental condition
def switch_time(changing_times, sequence_columns):
    tup_list = list(changing_times.to_records(index=False))
    block, item, category, face, gender, intervals_in_question, change = zip(*tup_list)
    changed_times = []
    for interval in intervals_in_question:
        if interval == 'long':
            changed_times.append('short')
        elif interval == 'short':
            changed_times.append('long')
    new_tup = list(zip(block, item, category, face, gender, changed_times, change))
    new_times = pd.DataFrame(new_tup, columns=sequence_columns)
    return new_times

########################################################################################################################################################################

### Function can be executed independently from experiment prior to start to review files and stimuli

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