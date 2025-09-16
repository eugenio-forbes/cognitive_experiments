"""
Initialization of Item Consolidation Experiment

Experiment consists of two study blocks and one test block. There is a longer delay between the    
first study block and test than the second one. Each trial presents an environment paired with     
a noun. During the study block subject must select whether the noun is animate or inanimate.       
A third of the nouns presented during a study block will be presented with a different environment 
during the test block (rearranged), while the others will be presented with the same (same).       
During the test block new nouns equal in number to those rearranged are also presented. Subject    
must select whether the nouns and environment pair is new, same, or rearranged.                    
This code randomizes and balances a total of 192 nouns paired with 6 different environments:       
-Study 1: 72 trials (48 same + 24 rearranged) (presented 3 times each)                             
-Study 2: 72 trials (48 same + 24 rearranged) (presented 3 times each)                             
-Test : 192 trials (144 study + 48 new)                                                            
Balancing 4 animate and inanimate subcategories.

"""

import pandas as pd
import random
import os
import json
import time
from configuration import *

########################################################################################################################################################################

def initialize_experiment_func(subject, session, session_directory):

    ### Define session files
    checkpoint_file = session_directory + 'checkpoint.csv'
    pulses_file = session_directory + 'pulses.csv'
    events_file = session_directory + 'events.csv'
    timing_file = session_directory + 'timing.csv'
    experiment_block_list_file = session_directory + 'experiment_block_list.json'
    configurations_file = session_directory + 'configurations.json'

    ### Randomize animate nouns from each subcategory
    with open(mammals_list, 'r') as file_handle:
        mammals = [line.strip() for line in file_handle]
    random.shuffle(mammals)
    
    with open(birds_list, 'r') as file_handle:
        birds = [line.strip() for line in file_handle]
    random.shuffle(birds)
    
    with open(aquatic_species_list, 'r') as file_handle:
        aquatic_species = [line.strip() for line in file_handle]
    random.shuffle(aquatic_species)
    
    with open(people_list, 'r') as file_handle:
        people = [line.strip() for line in file_handle]
    random.shuffle(people)
    
    ### Shuffle inanimate nouns from each subcategory
    with open(vehicles_list, 'r') as file_handle:
        vehicles = [line.strip() for line in file_handle]
    random.shuffle(vehicles)
    
    with open(clothing_list, 'r') as file_handle:
        clothing = [line.strip() for line in file_handle]
    random.shuffle(clothing)
    
    with open(food_list, 'r') as file_handle:
        food = [line.strip() for line in file_handle]
    random.shuffle(food)
    
    with open(furniture_list, 'r') as file_handle:
        furniture = [line.strip() for line in file_handle]
    random.shuffle(furniture)
    
    ### Balance 24 nouns from each subcategory into experimental conditions:
    ### i.e 12 same (6 per study block), 6 rearranged (3 per study block),
    ### and 6 new (test)
    animate_same1 = mammals[0:6] + aquatic_species[0:6] + birds[0:6] + people[0:6]
    animate_same2 = mammals[6:12] + aquatic_species[6:12] + birds[6:12] + people[6:12]
    animate_rearranged1 = mammals[12:15] + aquatic_species[12:15] + birds[12:15] + people[12:15]
    animate_rearranged2 = mammals[15:18] + aquatic_species[15:18] + birds[15:18] + people[15:18]
    animate_new = mammals[18:24] + aquatic_species[18:24] + birds[18:24] + people[18:24]
    
    inanimate_same1 = vehicles[0:6] + food[0:6] + furniture[0:6] + clothing[0:6]
    inanimate_same2 = vehicles[6:12] + food[6:12] + furniture[6:12] + clothing[6:12]
    inanimate_rearranged1 = vehicles[12:15] + food[12:15] + furniture[12:15] + clothing[12:15]
    inanimate_rearranged2 = vehicles[15:18] + food[15:18] + furniture[15:18] + clothing[15:18]
    inanimate_new = vehicles[18:24] + food[18:24] + furniture[18:24] + clothing[18:24]
    
    ### Combine animate and inanimate lists
    same_study1_nouns = animate_same1 + inanimate_same1
    same_study2_nouns = animate_same2 + inanimate_same2
    rearranged_study1_nouns = animate_rearranged1 + inanimate_rearranged1
    rearranged_study2_nouns = animate_rearranged2 + inanimate_rearranged2
    new_nouns = animate_new + inanimate_new
    
    ### Create lists of categories, noun types, and conditions that match above lists
    same_categories_animate = ['mammals'] * 6 + ['aquatic_species'] * 6 + ['birds'] * 6 + ['people'] * 6
    same_categories_inanimate = ['vehicles'] * 6 + ['food'] * 6 + ['furniture'] * 6 + ['clothing'] * 6
    same_categories = same_categories_animate + same_categories_inanimate 
    same_noun_types = ['ANIMATE'] * 24 + ['INANIMATE'] * 24
    same_conditions = ['SAME'] * 48

    rearranged_categories_animate = ['mammals'] * 3 + ['aquatic_species'] * 3 + ['birds'] * 3 + ['people'] * 3
    rearranged_categories_inanimate = ['vehicles'] * 3 + ['food'] * 3 + ['furniture'] * 3 + ['clothing'] * 3
    rearranged_categories = rearranged_categories_animate + rearranged_categories_inanimate 
    rearranged_noun_types = ['ANIMATE'] * 12 + ['INANIMATE'] * 12
    rearranged_conditions = ['REARRANGED'] * 24
    
    new_categories_animate = ['mammals'] * 6 + ['aquatic_species'] * 6 + ['birds'] * 6 + ['people'] * 6
    new_categories_inanimate = ['vehicles'] * 6 + ['food'] * 6 + ['furniture'] * 6 + ['clothing'] * 6
    new_categories = new_categories_animate + new_categories_inanimate
    new_noun_types = ['ANIMATE'] * 24 + ['INANIMATE'] * 24
    new_conditions = ['NEW'] * 48
    
    ### Environments imported from configuration
    ### Shuffle and divide environments into two sets of 3 (for balance of subcategories associated with environment)
    random.shuffle(environments)
    environments_set1 = environments[0:3]
    environments_set2 = environments[3:6]

    ### Balanced distribution of environments across subcategories for each experimental condition
    same_study1_environments = environments_set1 * 16
    same_study2_environments = environments_set2 * 16
    rearranged_study1_environments = environments_set1 * 8
    rearranged_study2_environments = environments_set2 * 8
    new_environments = (environments_set1 + environments_set2) * 8
    
    ### Shuffling of environments for nouns in rearranged condition
    ### This shuffle makes sure that there is a balanced switched from one environment to one of other two
    test_rearranged_study1_environments = rearrange_environments(environments_set1, 8)
    test_rearranged_study2_environments = rearrange_environments(environments_set2, 8)
    
    ### Define experimental phases for each of the experimental condition groups
    same_study1_events = ['ENCODING_LONG'] * 48
    same_study2_events = ['ENCODING_SHORT'] * 48
    rearranged_study1_events = ['ENCODING_LONG'] * 24
    rearranged_study2_events = ['ENCODING_SHORT'] * 24
    new_events = ['NEW_NOUN'] * 48

    ### Zip together matched list to create tuple lists
    same_study1 = list(zip(same_study1_nouns, same_noun_types, same_categories, same_study1_environments, same_study1_events, same_conditions))
    same_study2 = list(zip(same_study2_nouns, same_noun_types, same_categories, same_study2_environments, same_study2_events, same_conditions))
    rearranged_study1 = list(zip(rearranged_study1_nouns, rearranged_noun_types, rearranged_categories, rearranged_study1_environments, rearranged_study1_events, rearranged_conditions))
    rearranged_study2 = list(zip(rearranged_study2_nouns, rearranged_noun_types, rearranged_categories, rearranged_study2_environments, rearranged_study2_events, rearranged_conditions))
    test_rearranged_study1 = list(zip(rearranged_study1_nouns, rearranged_noun_types, rearranged_categories, test_rearranged_study1_environments, rearranged_study1_events, rearranged_conditions))
    test_rearranged_study2 = list(zip(rearranged_study2_nouns, rearranged_noun_types, rearranged_categories, test_rearranged_study2_environments, rearranged_study2_events, rearranged_conditions))
    new = list(zip(new_nouns, new_noun_types, new_categories, new_environments, new_events, new_conditions))

    ### Make lists for study and test blocks
    study1_block = same_study1 + rearranged_study1
    study2_block = same_study2 + rearranged_study2
    test_block = same_study1 + same_study2 + test_rearranged_study1 + test_rearranged_study2 + new

    ### Triplicate and pseudorandomize trials from study blocks and pseudorandomize test block
    study1 = []
    for _ in range(n_repetitions_study):
        block = pseudorandomize_trials(study1_block, environments_set1, max_consecutives_study)
        study1.extend(block)

    study2 = []
    for _ in range(n_repetitions_study):
        block = pseudorandomize_trials(study2_block, environments_set2, max_consecutives_study)
        study2.extend(block)

    test = pseudorandomize_trials(test_block, environments_set1 + environments_set2, max_consecutives_test)
    
    ### Convert tuple lists to dictionaries, make final changes, and save to .json files for use in experiment
    study1 = tuple_list_to_dict_list(study1, 'STUDY1', subject, session)
    study2 = tuple_list_to_dict_list(study2, 'STUDY2', subject, session)
    test = tuple_list_to_dict_list(test, 'TEST', subject, session)

    experiment_block_list = {
        'STUDY1': study1,
        'STUDY2': study2,
        'TEST': test
    }

    ### Save experiment block list to be used for the experiment session
    with open(experiment_block_list_file, 'w') as file_handle:
        json.dump(experiment_block_list, file_handle)

    ### Save configurations used for the experiment session
    with open(configurations_file, 'w') as file_handle:
        json.dump(configuration_dictionary, file_handle)

    ### Initialize .csv files to which data on trials will be added after execution of the experiment
    if not os.path.isfile(checkpoint_file):
        pd.DataFrame(columns=checkpoint_fieldnames).to_csv(checkpoint_file, index=False, header=True)
    
    if not os.path.isfile(pulses_file):
        pd.DataFrame(columns=pulses_fieldnames).to_csv(pulses_file, index=False, header=True)

    if not os.path.isfile(events_file):
        pd.DataFrame(columns=events_fieldnames).to_csv(events_file, index=False, header=True)

    if not os.path.isfile(timing_file):
        pd.DataFrame(columns=timing_fieldnames).to_csv(timing_file, index=False, header=True)
    
    ### Allow some time for writing of files before accessing them
    time.sleep(0.5)

### Function to shuffle without any nouns remaining in original position
### Inputing set of 3 environments
### 6 permutations out of which 2 have no equalities to original so probability of success is a third
def unequal_shuffle(original_items):
    shuffled_items = original_items.copy()
    successful_shuffle = False
    while not successful_shuffle:
        successful_shuffle = True
        random.shuffle(shuffled_items)
        for index in range(len(original_items)):
            if shuffled_items[index] == original_items[index]:
                successful_shuffle = False                
    return shuffled_items    

### Function to create list of rearranged environments
def rearrange_environments(environments_set, n_extensions):
    successful_rearrangement = False
    while not successful_rearrangement:
        successful_rearrangement = True
        rearranged_list = []

        ### Extending original set of 3 n_extensions times with deranged permutations
        for _ in range(n_extensions):
            shuffled_set = unequal_shuffle(environments_set)
            rearranged_list.extend(shuffled_set)
        
        ### Loop to verify that not one permutation was selected
        ### more than half the times (+1 for higher chance of success)
        for environment in environments_set:
            n_repetitions_position1 = 0
            n_repetitions_position2 = 0
            n_repetitions_position3 = 0
            for j in range(8):

                if rearranged_list[j*3] == environment:
                    n_repetitions_position1 += 1

                if rearranged_list[j*3+1] == environment:
                    n_repetitions_position2 += 1

                if rearranged_list[j*3+2] == environment:
                    n_repetitions_position3 += 1

            if n_repetitions_position1 > 5 or n_repetitions_position2 > 5 or n_repetitions_position3 > 5:
                successful_rearrangement = False       
    return rearranged_list

### Function that shuffles study block and ensures that there are no more than
### 5 consecutive trials with the same environment or noun type or noun category
def pseudorandomize_trials(block, environments_set, max_consecutives):

    n_max_environments, n_max_types, n_max_categories = max_consecutives
    successful_shuffle = False
    while not successful_shuffle:
        successful_shuffle = True
        
        random.shuffle(block)
        nouns, types, categories, environments, events, conditions = zip(*block)
        
        last_environment = 'none'
        environment_count = 0
        environment_count_max = 0

        for environment in environments:
            if environment == last_environment:
                environment_count += 1
            else:
                if environment_count > environment_count_max:
                    environment_count_max = environment_count
                last_environment = environment
                environment_count = 1
        
        last_type = 'none'
        type_count = 0
        type_count_max = 0
        
        for item_type in types:
            if item_type == last_type:
                type_count += 1
            else:
                if type_count > type_count_max:
                    type_count_max = type_count
                last_type = item_type
                type_count = 1
        
        last_category = 'none'
        category_count = 0
        category_count_max = 0
        
        for category in categories:
            if category == last_category:
                category_count += 1
            else:
                if category_count > category_count_max:
                    category_count_max = category_count
                last_category = category
                category_count = 1
        
        if environment_count_max > n_max_environments or type_count_max > n_max_types or category_count_max > n_max_categories:
            successful_shuffle = False

    return block

### Function that converts tuple list to dictionaries and saves to .json file for use in experiment
def tuple_list_to_dict_list(tuple_list, experiment_phase, subject, session):

    experiment_block = []
    trial_index = 0

    for noun, noun_type, noun_category, environment, event, test_condition in tuple_list:
        
        ### Edit event type for test block trials
        if experiment_phase == 'TEST':
            if event == 'ENCODING_LONG':
                event = 'RETRIEVAL_LONG'
            elif event == 'ENCODING_SHORT':
                event = 'RETRIEVAL_SHORT'

        trial = {
            'subject': subject,
            'session': session,
            'experiment_phase': experiment_phase,
            'event': event,
            'trial_index': trial_index,
            'noun': noun,
            'noun_type': noun_type,
            'noun_category': noun_category,
            'environment': environment,
            'test_condition': test_condition,
            }
        
        experiment_block.append(trial)
        trial_index += 1

    return experiment_block

### Function can be executed independently from experiment prior to start to review files and stimuli
if __name__ == '__main__':
    
    ### Prompt subject and session information from user for easier file management
    ### and to enable starting a session from a completed checkpoint.

    ### Gather a valid subject code:
    subject = prompt_subject_code()
        
    ### Gather a valid session number:
    session = prompt_session_number()
           
    session_directory = data_directory  + subject + '/session_'+ session + '/'
    session_logs = session_directory + 'session_logs/'

    ### Create list of trials if the experimental session had never been initialized
    if not os.path.isdir(session_directory):
        os.makedirs(session_directory)
        os.makedirs(session_logs)
        initialize_experiment_func(subject, session, session_directory)
    else:
        print(f"Session {session} for subject {subject} had already been initialized. Verify and try again.")