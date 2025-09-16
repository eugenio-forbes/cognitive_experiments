"""
Configurations for Associative Recognition with Closed-Loop Stimulation (Elemem) Experiment
This document contains experiment variables that can be modified ('Editable Parameters')
and experiment variables set for use during experiment run time. Important experiment
variables are stored in a dictionary so that they can be saved as a file during experiment
run time.

"""
import os
import Quartz # type: ignore

########################################################################################################################################################################

######################################################################## Editable Parameters ###########################################################################

experiment_name = 'associative_recogntion_closed-loop' # Folder with code and directories should have the same name
valid_subject_code_prefix = 'SC'
prefix_length = len(valid_subject_code_prefix)
n_subject_code_digits = 3
valid_subject_code_length = prefix_length + n_subject_code_digits
digit_string = '#' * n_subject_code_digits

### Connection to Blackrock computer server and stimulation parameters
server_ip_address = '127.0.0.1'
server_port = 5000
server_connection_enabled = False
stimulation_enabled = False

### Durations in seconds of several experimental elements
logo_duration = 3
countdown_duration = 3
distraction_math_duration = 30
distraction_break_duration = 120
orient_duration = 2
intertrial_interval = 3
intertrial_jitter = 0.25
allowed_response_time = 4
### Comment: Previously trial was divided by no_response_duration, 
### and response_duration, but subjects would often respond before 
### no_response_duration was over (thus not recording responses)
### and switching colors of words when response is allowed is perhaps 
### not appropriate

### Control keys (Edit to corresponding keys of controller used)
continue_key = 'SPACEBAR'
top_key = 'A'
bottom_key = 'S'
new_key = 'F'
same_key = 'G'
rearranged_key = 'H'

###############################################################################################################################

### Configuration dictionary to save parameters used in session (times in milliseconds for analysis)
### In case these are modified by user through time
configuration_dictionary = {
    'orient_duration': orient_duration * 1000,
    'allowed_response_time': allowed_response_time * 1000,
    'intertrial_interval': intertrial_interval * 1000,
    'allowed_response_time': allowed_response_time * 1000,
    'top_key': top_key,
    'bottom_key': bottom_key,
    'new_key': new_key,
    'same_key': same_key,
    'rearranged_key': rearranged_key,
    'server_connection_enabled': server_connection_enabled,
    'stimulation_enabled': stimulation_enabled
}

### List of directories with experiment resources and subject files
this_file = os.path.abspath(__file__)
base_directory = os.path.dirname(os.path.dirname(this_file)) + '/'
task_directory = os.path.dirname(this_file) + '/'
resources_directory = base_directory + 'resources/'
word_list_directory = resources_directory + 'word_lists/associative_recognition/'
instructions_directory = resources_directory + 'instructions/associative_recognition/'
image_directory = resources_directory + 'images/'
data_directory = task_directory + 'subject_files/'
test_directory = task_directory + 'data/' + experiment_name + '/test000/'

### Word lists
inside_nouns_list = word_list_directory + 'inside.txt'
outside_nouns_list = word_list_directory + 'outside.txt'

### Frequently used images in experiment
lab_logo = image_directory + 'other/LegaLab.png'
countdown_video = image_directory + 'other/countdown.mp4'
crosshair_image = image_directory + 'other/crosshair.png'
blank_image = image_directory + 'other/blank.png'
countdown_video = image_directory + 'other/blank.png'

### Experiment instructions saved in text files
instructions_file = instructions_directory + 'instructions.txt'
with open(instructions_file, 'r') as file_handle:
    instructions_text = file_handle.read()

### Message parameters and variables
### Used in initialization of message dictionary for communications with Elemem server
stimulation_mode = 'none'          # 'none', 'open' for open-loop, or 'closed' for closed-loop
stimulation_bool = False           # to be replaced by True only when stim is to be delivered
stimulation_tag = ''
data_entry_tags = []               # replace with tags in STIMSELECT experiments
classification_duration_ms = 1024  # duration of classifier based stimulation
message_time = 0.0                 # time variable to be replaced by actual time every time a message is sent
n_heartbeats = 50                  # 50 heartbeats to be sent both at the start and the end of the experiment
trial_number = 0                   # replaced by actual trial number in experiment run
word_pair = 'WORD_PAIR'            # replaced by actual word pair in experiment run
serial_position = 0                # replaced by actual serial position in experiment run int
recall_duration = 0.0              # replaced by actual recall time float
math_problem = 'math.slog'         # can't complete in real time with SMILE
math_response = 'math.slog'        # can't complete in real time with SMILE
math_rt_ms = 0                     # can't complete in real time with SMILE
math_correct = True                # can't complete in real time with SMILE
cps_duration_s = 5                 # replaced by actual cps duration in seconds

message_id = 0
heartbeat_count = 0
n_normalization_events = 30

### Dataframe fieldnames
checkpoint_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase', 'trial_index',
    'log_num', 'log_time']

pulses_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase', 'trial_index', 
    'pulse_time', 'log_num', 'log_time']

events_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase', 'trial_index',
    'top_word', 'bottom_word', 'study_answer', 'test_condition',
    'test_stimulation_condition', 'study_response', 'study_time_to_respond',
    'test_response', 'test_time_to_respond', 'log_num', 'log_time']

timing_fieldnames = [
    'subject', 'session', 'experiment_block', 'experiment_phase', 'trial_index', 
    'sync_time', 'orient_time', 'trial_time', 'response_time', 'log_num', 'log_time']

communications_fieldnames = [
    'type', 'time', 'data', 'id']

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

### Positions of experiment elements
top = screen_height
center_x = screen_width / 2
center_y = screen_height / 2

label_offset = 150 * f_height
logo_offset = 500 * f_height
small_offset = 15 * f_height

### Positions for words and key reminders in a trial
top_word_y = center_y + small_offset
bottom_word_y = center_y - small_offset
T_reminder_x = center_x + (screen_width / 6)
B_reminder_x = center_x + (screen_width / 3)
N_reminder_x = center_x + (screen_width / 8)
S_reminder_x = center_x + (screen_width / 4)
R_reminder_x = center_x + (3 * (screen_width / 8))