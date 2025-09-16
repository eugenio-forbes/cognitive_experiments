"""
Initialization of Associative Recognition Experiment (Elemem compatible)

Experiment consists of several blocks with study and test phases. In each study phase 45 pairs of  
nouns are sequentially presented, with one noun positioned on top and the other on the bottom.     
Subject must select which of the two nouns fits inside the other in an imagined interaction        
between the two.                                                                                   

The test phase begins after a delay of some minutes. From the 45 pairs of nouns in the study phase,
15 pairs will have words swapped between them (rearranged pairs), while conseving the words'       
original position (top or bottom), and 30 will remain the same as they were. 15 new pairs of nouns 
are added to the test phase. The 60 word pairs are presented sequentially in the same manner as    
the study phase. Subject must select whether the pair of words displayed is a new pair, a pair     
that remained the same as it was during the study phase, or a rearranged pair.                     

This code extracts nouns from two different lists that roughly separate them into nouns that would 
be subdominant in an interaction (INSIDE.txt) and nouns that would dominate the interaction        
(OUTSIDE.txt). It then arranges them into a specified number of experiment blocks, randomizing     
selection of experimental condition and trial order, balancing the correct study response.    

This code defines message dictionaries sent to Elemem server with experiment parameters.

"""
import random
import json
import os
import time
import pandas as pd

from configuration import *
from experiment_utils import *
from elemem_message_dictionary import *

########################################################################################################################################################################

def initialize_experiment_func(subject, session, session_directory, n_experiment_blocks):
    
    ### Define session files
    experiment_block_list_file = session_directory + 'experiment_block_list.json'
    configurations_file = session_directory + 'configurations.json'
    message_dictionary_file = session_directory + 'message_dictionary.json'
    checkpoint_file = session_directory + 'checkpoint.csv'
    pulses_file = session_directory + 'pulses.csv'
    events_file = session_directory + 'events.csv'
    timing_file = session_directory + 'timing.csv'
    communications_file = session_directory + 'communications.csv'

    ### Randomize nouns from each category
    with open(inside_nouns_list, 'r') as file_handle:
        inside_nouns = [line.strip() for line in file_handle]
    random.shuffle(inside_nouns)
    
    with open(outside_nouns_list, 'r') as file_handle:
        outside_nouns = [line.strip() for line in file_handle]
    random.shuffle(outside_nouns)
    
    ### Divide each noun category into two lists
    ### For balancing correct study response (top, bottom)
    top_inside_nouns = inside_nouns[0:210]
    bottom_inside_nouns = inside_nouns[210:420]
    top_outside_nouns = outside_nouns[0:210]
    bottom_outside_nouns = outside_nouns[210:420]

    ### Create lists for the study answer that match above lists
    study_answer_top = ['top'] * 210
    study_answer_bottom = ['bottom'] * 210
    
    ### Combine opposite categories and study answer corresponding to position of inside nouns
    ### Randomize order of word pairs
    top_response_word_pairs = list(zip(top_inside_nouns, bottom_outside_nouns, study_answer_top))
    bottom_response_word_pairs = list(zip(top_outside_nouns, bottom_inside_nouns, study_answer_bottom))
    word_pairs = top_response_word_pairs + bottom_response_word_pairs
    random.shuffle(word_pairs)

    ### Arrange word pairs into experiment blocks, select experimental conditions and prepare
    ### study and test phases for final experiment block list used in experiment

    experiment_block_list = []

    for block_number in range(n_experiment_blocks + 1):
        
        start_index = 60 * block_number
        end_index = 60 * (block_number + 1)
        
        block_word_pairs = word_pairs[start_index:end_index]
        
        study_phase, test_phase = arrange_experiment_phases(block_word_pairs)
        
        study_phase_trials = []
        trial_index = 0
        for top_word, bottom_word, study_answer, test_condition in study_phase:
            trial = {
                'subject': subject,
                'session': session,
                'experiment_block': str(block_number),
                'experiment_phase': 'ENCODING',
                'trial_index': str(trial_index),
                'top_word': top_word,
                'bottom_word': bottom_word,
                'study_answer': study_answer,
                'test_condition': test_condition,
            }
            study_phase_trials.append(trial)
            trial_index += 1

        test_phase_trials = []
        trial_index = 0
        for top_word, bottom_word, study_answer, test_condition in test_phase:
            trial = {
                'subject': subject,
                'session': session,
                'experiment_block': str(block_number),
                'experiment_phase': 'RETRIEVAL',
                'trial_index': str(trial_index),
                'top_word': top_word,
                'bottom_word': bottom_word,
                'study_answer': study_answer,
                'test_condition': test_condition,
            }
            test_phase_trials.append(trial)
            trial_index += 1
        
        experiment_block = {
            'experiment_block': str(block_number),
            'study_phase': study_phase_trials,
            'test_phase': test_phase_trials
        }
        experiment_block_list.append(experiment_block)

    ### Save experiment block list for use in experiment
    with open(experiment_block_list_file, 'w') as file_handle:
        json.dump(experiment_block_list, file_handle)
    
    ### Save configurations used for the experiment session
    with open(configurations_file, 'w') as file_handle:
        json.dump(configuration_dictionary, file_handle)

    message_dictionary = get_message_dictionary(subject, session)
    
    with open(message_dictionary_file, 'w') as f:
        json.dump(message_dictionary, f)
    
    ### Initialize .csv files to which data on trials will be added after execution of the experiment
    if not os.path.isfile(checkpoint_file):
        pd.DataFrame(columns=checkpoint_fieldnames).to_csv(checkpoint_file, index=False, header=True)
    
    if not os.path.isfile(pulses_file):
        pd.DataFrame(columns=pulses_fieldnames).to_csv(pulses_file, index=False, header=True)

    if not os.path.isfile(events_file):
        pd.DataFrame(columns=events_fieldnames).to_csv(events_file, index=False, header=True)

    if not os.path.isfile(timing_file):
        pd.DataFrame(columns=timing_fieldnames).to_csv(timing_file, index=False, header=True)

    if not os.path.isfile(communications_file):
        pd.DataFrame(columns=communications_fieldnames).to_csv(timing_file, index=False, header=True)
    
    ### Allow some time for writing of files before accessing them
    time.sleep(0.5)

# Function that arranges word pairs of an experiment block
# into the study and test phases, adding the test phase experimental conditions
def arrange_experiment_phases(block_word_pairs):
    
    top_words, bottom_words, study_answers = zip(*block_word_pairs)
    
    ### Divide word pairs into the three experimental conditions
    ### Add list of corresponding experimental condition
    ### Set half the trials of each condition to undergo stimulation
    ### For rearranged pairs swap all top words
    ### For new pairs switch study answer to 'none'

    same_top_words = top_words[0:30]
    same_bottom_words = bottom_words[0:30]
    same_study_answers = study_answers[0:30]
    same_test_conditions = ['same'] * 30
    same_word_pairs = list(zip(same_top_words, same_bottom_words, same_study_answers, same_test_conditions))
    
    rearranged_top_words = top_words[30:45]
    swapped_rearranged_top_words = swap_all_words(rearranged_top_words)
    rearranged_bottom_words = bottom_words[30:45]
    rearranged_study_answers = study_answers[30:45]
    rearranged_test_conditions = ['rearranged'] * 15
    rearranged_word_pairs_study = list(zip(rearranged_top_words, rearranged_bottom_words, rearranged_study_answers, rearranged_test_conditions))
    rearranged_word_pairs_test = list(zip(swapped_rearranged_top_words, rearranged_bottom_words, rearranged_study_answers, rearranged_test_conditions))

    new_top_words = top_words[45:60]
    new_bottom_words = bottom_words[45:60]
    new_study_answers = [-1] * 15
    new_test_conditions = ['new'] * 15 
    new_word_pairs = list(zip(new_top_words, new_bottom_words, new_study_answers, new_test_conditions))

    ### Combine word pairs from different experimental conditions to create study and test phases
    ### Randomize trial order
    study_phase = same_word_pairs + rearranged_word_pairs_study
    random.shuffle(study_phase)
    
    test_phase = same_word_pairs + rearranged_word_pairs_test + new_word_pairs
    random.shuffle(test_phase)

    return study_phase, test_phase

### Function that randomly shuffles words to be swapped for rearranged test condition
### and makes sure that they were all swapped
def swap_all_words(words):
    successful_swap = False
    swapped_words = list(words)
    while not successful_swap:
        successful_swap = True
        random.shuffle(swapped_words)
        for index in range(len(words)):
            if swapped_words[index] == words[index]:
                successful_swap = False
    return swapped_words

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
        ### Gather a valid number of experiment blocks (0-6):
        n_experiment_blocks = prompt_n_experiment_blocks()
        initialize_experiment_func(subject, session, session_directory, n_experiment_blocks)
    else:
        print(f"Session {session} for subject {subject} had already been initialized. Verify and try again.")