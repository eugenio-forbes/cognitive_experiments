"""
Configurations for Item Consolidation Experiment

This document contains experiment variables that can be modified ('Editable Parameters')
and experiment variables set for use during experiment run time. Important experiment
variables are stored in a dictionary so that they can be saved as a file during experiment
run time.

"""

import os
import Quartz # type: ignore

########################################################################################################################################################################

######################################################################## Editable Parameters ###########################################################################

experiment_name = 'item_consolidation' # Folder with code and directories should have the same name
valid_subject_code_prefix = 'SC'
prefix_length = len(valid_subject_code_prefix)
n_subject_code_digits = 3
valid_subject_code_length = prefix_length + n_subject_code_digits
digit_string = '#' * n_subject_code_digits

### Durations in seconds of several experimental elements
logo_duration = 3
countdown_duration = 3
orient_duration = 2
intertrial_interval = 3
intertrial_jitter = 0.25
allowed_response_time = 4
### Comment: Previously trial was divided by no_response_duration, 
### and response_duration, but subjects would often respond before 
### no_response_duration was over (thus not recording responses)
### and switching colors of words when response is allowed is perhaps 
### not appropriate

### Number of times items will be encoded during study
n_repetitions_study = 3

### Control keys: Edit to correspond to those in controller used
continue_key = 'SPACEBAR'
animate_key = 'A'
inanimate_key = 'S'
new_key = 'F'
same_key = 'G'
rearranged_key = 'H'

####################################################################### Other Variables Used ###########################################################################

### Configuration dictionary to save parameters used in session (times in milliseconds for analysis)
### In case these are modified by user through time
configuration_dictionary = {
    'orient_duration': orient_duration * 1000,
    'allowed_response_time': allowed_response_time * 1000,
    'intertrial_interval': intertrial_interval * 1000,
    'allowed_response_time': allowed_response_time * 1000,
    'animate_key': animate_key,
    'inanimate_key': inanimate_key,
    'new_key': new_key,
    'same_key': same_key,
    'rearranged_key': rearranged_key
}

### List of directories with experiment resources and subject files
this_file = os.path.abspath(__file__)
base_directory = os.path.dirname(os.path.dirname(this_file)) + '/'
task_directory = os.path.dirname(this_file) + '/'
resources_directory = base_directory + 'resources/'
image_directory = resources_directory + 'images/'
environment_directory = image_directory + 'environments/'
word_list_directory = resources_directory + 'word_lists/item_consolidation/'
instructions_directory = resources_directory + 'instructions/item_consolidation/'
data_directory = task_directory + 'subject_files/'
test_directory = task_directory + 'data/' + experiment_name + '/test000/'

### Animate noun lists
mammals_list = word_list_directory + 'mammals.txt'
birds_list = word_list_directory + 'birds.txt'
aquatic_species_list = word_list_directory + 'aquatic_species.txt'
people_list = word_list_directory + 'people.txt'

### Inanimate noun lists
vehicles_list = word_list_directory + 'vehicles.txt'
clothing_list = word_list_directory + 'clothing.txt'
food_list = word_list_directory + 'food.txt'
furniture_list = word_list_directory + 'furniture.txt'

### Frequently used images in experiment
lab_logo = image_directory + 'other/LegaLab.png'
countdown_video = image_directory + 'other/countdown.mp4'
crosshair_image = image_directory + 'other/crosshair.png'
blank_image = image_directory + 'other/blank.png'

### Experiment instructions saved in text files
general_instructions_file = instructions_directory + 'general_instructions.txt'
instructions_study_file = instructions_directory + 'instructions_study.txt'
instructions_test_file = instructions_directory + 'instructions_test.txt'

with open(general_instructions_file, 'r') as file_handle:
    general_instructions_text = file_handle.read()

with open(instructions_study_file, 'r') as file_handle:
    instructions_study_text = file_handle.read()

with open(instructions_test_file, 'r') as file_handle:
    instructions_test_text = file_handle.read()

instructions = {'STUDY1': instructions_study_text,
                'STUDY2': instructions_study_text, 
                'TEST': instructions_test_text}

phase_questions = ['Animate or Inanimate?', 'New, Same or Rearranged?']

phase_labels = {'STUDY1': ['Study Section #1', phase_questions[0]],
                'STUDY2': ['Study Section #2', phase_questions[0]],
                'TEST': ['Test Section', phase_questions[1]]}

### Experimental variables
noun_type_set = ['ANIMATE', 'INANIMATE']
noun_category_set = ['mammals', 'aquatic_species', 'birds', 'people', 'furniture', 'vehicles', 'food', 'clothing']
environments = ['beach', 'canyon', 'forest', 'glacier', 'mountain', 'sand_dunes', 'snow', 'wheat_field']

### Max numbers of consecutive trials with same environment, noun type or category
### Numbers were chosen for more spread distribution of trials while keeping runtime seamless
n_max_environments_study = 3
n_max_types_study = 3
n_max_categories_study = 2
max_consecutives_study = (n_max_environments_study, n_max_types_study, n_max_categories_study)
n_max_environments_test = 3
n_max_types_test = 4
n_max_categories_test = 2
max_consecutives_test = (n_max_environments_test, n_max_types_test, n_max_categories_test)

### Dataframe fieldnames
checkpoint_fieldnames = [
    'subject', 'session', 'experiment_phase', 'trial_index',
    'log_num', 'log_time']

pulses_fieldnames = [
    'subject', 'session', 'experiment_phase', 'trial_index',
    'pulse_time', 'log_num', 'log_time']

events_fieldnames = [
    'subject', 'session', 'experiment_phase', 'event', 'trial_index',
    'noun', 'noun_type', 'noun_category', 'environment',
    'test_condition', 'response', 'time_to_respond', 'log_num', 'log_time']

timing_fieldnames = [
    'subject', 'session', 'experiment_phase', 'event', 'trial_index', 
    'sync_time', 'orient_time', 'trial_time', 'time_to_respond',
    'log_num', 'log_time']

### Getting screen size to adjust the size and position of experiment elements
display_id = Quartz.CGMainDisplayID()
display_mode = Quartz.CGDisplayCopyDisplayMode(display_id)
screen_width = Quartz.CGDisplayModeGetPixelWidth(display_mode)
screen_height = Quartz.CGDisplayModeGetPixelHeight(display_mode)
screen_size = (screen_width, screen_height)
f_width = screen_width/2880
f_height = screen_height/1800

### Size of displayed environment images
environment_width = screen_width * 0.8
environment_height = screen_height * 0.8
environment_size = (environment_width, environment_height)

### Font sizes
large_font = 120 * f_height
medium_font = 100 * f_height
small_font = 80 * f_height
instructions_font_size = 50 * f_height

### Positions of experiment elements
top = screen_height
center_x = screen_width / 2
center_y = screen_height / 2

label_offset = 150 * f_height
logo_offset = 500 * f_height
small_offset = 75 * f_height
button_offset = 15 * f_height