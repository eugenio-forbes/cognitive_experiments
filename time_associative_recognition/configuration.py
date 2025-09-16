"""
Configurations for Time Associative Recognition Experiment

This document contains experiment variables that can be modified ('Editable Parameters')
and experiment variables set for use during experiment run time. Important experiment
variables are stored in a dictionary so that they can be saved as a file during experiment
run time.

"""

import os
import Quartz
import random

########################################################################################################################################################################

########################################################################## Editable Parameters #########################################################################

experiment_name = 'time_associative_recognition' # Folder with code and directories should have the same name
valid_subject_code_prefix = 'SC'
prefix_length = len(valid_subject_code_prefix)
n_subject_code_digits = 3
valid_subject_code_length = prefix_length + n_subject_code_digits
digit_string = '#' * n_subject_code_digits

### Durations in seconds of several experimental elements
### Sequence study: crosshair -> emoji image -> blank -> celebrity face image -> pause -> response about emoji
### Sequence test: crosshair -> emoji image -> blank -> celebrity face image -> pause -> response about image association -> pause -> response about time
logo_duration = 3
orient_duration = 3
image_duration = 3
short_blank_duration = 3
long_blank_duration = 6
intertrial_interval = 3
intertrial_jitter = 0.25
preresponse_pause = 2
allowed_response_time = 4

### Durations in seconds between blocks, with 1 - p_standard chance it will be different
standard_delay = 20
deviant_delay = 10
p_standard_delay = 0.8

### Control keys (Edit to correspond to those of controller used)
continue_key = 'SPACEBAR'
left_key = 'F'
right_key = 'H'

########################################################################################################################################################################

### Configuration dictionary to save parameters used in session in ms
### In case these are modified by user through time and to keep record of randomized keys
configuration_dictionary = {
    'orient_duration': orient_duration * 1000,
    'image_duration': image_duration * 1000,
    'short_blank_duration': short_blank_duration * 1000,
    'long_blank_duration': long_blank_duration * 1000,
    'intertrial_interval': intertrial_interval * 1000,
    'preresponse_pause': preresponse_pause * 1000,
    'allowed_response_time': allowed_response_time * 1000,
    'standard_delay': standard_delay * 1000,
    'deviant_delay': deviant_delay * 1000,
    'p_standard_delay': p_standard_delay,
    'left_key': left_key,
    'right_key': right_key,
}

### List of directories with experiment resources and subject files
this_file = os.path.abspath(__file__)
base_directory = os.path.dirname(os.path.dirname(this_file)) + '/'
task_directory = os.path.dirname(this_file) + '/'
resources_directory = base_directory + 'resources/'
instructions_directory = resources_directory + 'instructions/time_associative_recognition/'
image_directory = resources_directory + 'images/'
emoji_directory = image_directory + 'emojis/'
face_directory = image_directory + 'equalized_celebrities/'
list_directory = resources_directory + 'image_lists/'
data_directory = task_directory + 'subject_files/'
test_directory = task_directory + 'data/' + experiment_name + '/test000/'

### Frequently used images in experiment
blank_image = image_directory + 'other/blank.png' # Blank screen
crosshair_image = image_directory + 'other/crosshair.png' # Crosshair for subject to orient view to center
screen_divider = image_directory + 'other/screen_divider.png' # Line to divide response labels assigned to left or right keys
lab_logo = image_directory + 'other/LegaLab.png'

### Experiment instructions saved in text file and displayed in graphic reprenstation:
instructions_file = instructions_directory + 'instructions.txt'
with open(instructions_file, 'r') as file_handle:
    instructions_text = file_handle.read()
instructions_image = instructions_directory + 'instructions.png'

### Dataframe fieldnames
checkpoint_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase',
    'trial_index', 'log_num', 'log_time']

pulses_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase',
    'trial_index', 'pulse_time', 'log_num', 'log_time']

events_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase',
    'trial_index', 'item', 'item_category', 'celebrity_face', 
    'celebrity_gender', 'interval', 'interval_type', 'test_condition',
    'item_response', 'item_time_to_respond', 'face_response', 'face_time_to_respond',
    'interval_response', 'interval_time_to_respond', 'trial_time',
    'log_num', 'log_time']

timing_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase',
    'trial_index', 'sync_time', 'orient_time', 'trial_time',
    'item_time', 'interval_time', 'interval', 'face_time', 
    'item_question_time', 'item_time_to_respond', 'face_question_time',
    'face_time_to_respond', 'interval_question_time', 
    'interval_time_to_respond', 'log_num', 'log_time']

delays_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase',
    'delay_time', 'delay_duration', 'log_num', 'log_time']

### Getting screen size to adjust the size and position of experiment elements
display_id = Quartz.CGMainDisplayID()
display_mode = Quartz.CGDisplayCopyDisplayMode(display_id)
screen_width = Quartz.CGDisplayModeGetPixelWidth(display_mode)
screen_height = Quartz.CGDisplayModeGetPixelHeight(display_mode)
screen_size = (screen_width, screen_height)
f_width = screen_width/2880
f_height = screen_height/1800

### Size of displayed visual instructions
instructions_width = screen_width * 0.9
instructions_height = screen_height * 0.9
instructions_size = (instructions_width, instructions_height)

### Font sizes
large_font = 120 * f_height
medium_font = 100 * f_height
small_font = 80 * f_height
instructions_font_size = 50 * f_height

### Postions of experiment elements
top = screen_height
center_y = screen_height / 2

left_x = screen_width / 4
right_x = 3 * (screen_width / 4)

label_offset = 150 * f_height
logo_offset = 500 * f_height
small_offset = 75 * f_height