"""
Configurations for Timed Sequence Recognition Experiment

This document contains experiment variables that can be modified ('Editable Parameters')
and experiment variables set for use during experiment run time. Important experiment
variables are stored in a dictionary so that they can be saved as a file during experiment
run time.

"""

import os
import Quartz

########################################################################################################################################################################

######################################################################## Editable Parameters ###########################################################################

experiment_name = 'timed_sequence_recognition' # Folder with code and directories should have the same name
valid_subject_code_prefix = 'SC'
prefix_length = len(valid_subject_code_prefix)
n_subject_code_digits = 3
valid_subject_code_length = prefix_length + n_subject_code_digits
digit_string = '#' * n_subject_code_digits

### Durations in seconds of several experimental elements
### Sequence study: crosshair -> emoji image -> blank -> celebrity face image -> pause -> response about emoji
### Sequence test: crosshair -> emoji image -> blank -> celebrity face image -> pause -> response about image association -> pause -> response about time
logo_duration = 3
orient_duration = 2
image_duration = 2
short_blank_duration = 2
long_blank_duration = 4
intersequence_interval = 3
intersequence_jitter = 0.25
intertrial_interval = 3
intertrial_jitter = 0.25
preresponse_pause = 3

### Durations in seconds between blocks, with 1 - p_standard chance it will be different 
standard_delay = 20
deviant_delay = 10
p_standard_delay = 0.8

####################################################################### Other Variables Used ###########################################################################

### Configuration dictionary to save parameters used in session (times in milliseconds for analysis)
### In case these are modified by user through time
configuration_dictionary = {
    'orient_duration': orient_duration * 1000,
    'image_duration': image_duration * 1000,
    'short_blank_duration': short_blank_duration * 1000,
    'long_blank_duration': long_blank_duration * 1000,
    'intersequence_interval': intersequence_interval * 1000,
    'intertrial_interval': intertrial_interval * 1000,
    'preresponse_pause': preresponse_pause * 1000,
    'standard_delay': standard_delay * 1000,
    'deviant_delay': deviant_delay * 1000,
    'p_standard_delay': p_standard_delay
}

### List of directories with experiment resources and subject files
this_file = os.path.abspath(__file__)
base_directory = os.path.dirname(os.path.dirname(this_file)) + '/'
task_directory = os.path.dirname(this_file) + '/'
resources_directory = base_directory + 'resources/'
instructions_directory = resources_directory + 'instructions/timed_sequence_recognition/'
image_directory = resources_directory + 'images/'
emoji_directory = image_directory + 'emojis/'
face_directory = image_directory + 'equalized_celebrities/'
list_directory = resources_directory + 'image_lists/'
data_directory = task_directory + 'subject_files/'
test_directory = task_directory + 'data/' + experiment_name + '/test000/'

### Files with lists of images used in experiment
emoji_list_file = list_directory + 'all_emojis.txt'
celebrity_list_file = list_directory + 'all_celebrities.txt'

### Frequently used image files in experiment
blank_image = image_directory + 'other/blank.png' # Blank screen
crosshair_image = image_directory + 'other/crosshair.png' # Crosshair for subject to orient view to center
test_sign_image = image_directory + 'other/test_sign.png'
lab_logo = image_directory + 'other/LegaLab.png'

### Experiment instructions saved in text file and displayed in graphic reprenstation:
instructions_file = instructions_directory + 'instructions.txt'
with open(instructions_file, 'r') as file_handle:
    instructions_text = file_handle.read()
instructions_image1 = instructions_directory + 'instructions1.png'
instructions_image2 = instructions_directory + 'instructions2.png'

### Dataframe fieldnames
checkpoint_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase',
    'sequence_index', 'log_num', 'log_time']

pulses_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase',
    'sequence_index', 'pulse_time', 'log_num', 'log_time']

events_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase',
    'sequence_index', 'sequence_group', 'interval_type', 'emoji',
    'interval', 'face1', 'face2', 'response', 'correct_response', 
    'time_to_respond', 'trial_time', 'log_num', 'log_time']

timing_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase', 
    'sequence_index', 'sequence_group', 'interval_type', 'sync_time',
    'orient_time', 'trial_time', 'emoji_time', 'face1_time', 'interval_time',
    'interval', 'face2_time', 'question_time', 'time_to_respond',
    'log_num', 'log_time']

delays_fieldnames = [
    'subject', 'session', 'experiment_block', 'delay_time',
    'delay_duration', 'log_num', 'log_time']

### Getting screen size to adjust the size and position of experiment elements
display_id = Quartz.CGMainDisplayID()
display_mode = Quartz.CGDisplayCopyDisplayMode(display_id)
screen_width = Quartz.CGDisplayModeGetPixelWidth(display_mode)
screen_height = Quartz.CGDisplayModeGetPixelHeight(display_mode)
screen_size = (screen_width, screen_height)
f_width = screen_width/2880
f_height = screen_height/1800

### Font sizes
large_font = 120 * f_height
medium_font = 100 * f_height
small_font = 80 * f_height
instructions_font_size = 50 * f_height

### Postions of experiment elements
top = screen_height
center_x = screen_width / 2
center_y = screen_height / 2

label_offset = 150 * f_height
logo_offset = 500 * f_height
small_offset = 75 * f_height
button_offset = 15 * f_height

### Size and positions of four buttons used in test phase response
button_width = 900 * f_width
button_height = 500 * f_height
button_size = (button_width, button_height)

top_left_x = center_x - (button_width / 2) - button_offset
top_left_y = center_y + (button_height / 2) + button_offset - label_offset
top_left_position = (top_left_x, top_left_y)
        
top_right_x = center_x + (button_width / 2) + button_offset
top_right_y = center_y + (button_height / 2) + button_offset - label_offset
top_right_position = (top_right_x, top_right_y)
        
bottom_left_x = center_x - (button_width / 2) - button_offset
bottom_left_y = center_y - (button_height / 2) - button_offset - label_offset
bottom_left_position = (bottom_left_x, bottom_left_y)
        
bottom_right_x = center_x + (button_width / 2) + button_offset
bottom_right_y = center_y - (button_height / 2) - button_offset - label_offset
bottom_right_position = (bottom_right_x, bottom_right_y)

### Keys
continue_key = 'SPACEBAR'