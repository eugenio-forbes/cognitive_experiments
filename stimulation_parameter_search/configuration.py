"""
Configuarions for Stimulation Parameter Search Experiment

This document contains experiment variables that can be modified ('Editable Parameters')
and experiment variables set for use during experiment run time. Important experiment
variables are stored in a dictionary so that they can be saved as a file during experiment
run time.

"""

import os
import numpy as np
import Quartz

########################################################################################################################################################################

########################################################################## Editable Parameters #########################################################################

experiment_name = 'stimulation_parameter_search' # Folder with code and directories should have the same name
valid_subject_code_prefix = 'SC'
prefix_length = len(valid_subject_code_prefix)
n_subject_code_digits = 3
valid_subject_code_length = prefix_length + n_subject_code_digits
digit_string = '#' * n_subject_code_digits

### Server IP address and port number
### Make sure that IP address matches the one set in Blackrock computer and stimulation_server.m
server_ip = '127.0.0.1'
server_port = 5000

### Parameters being searched over
amplitudes = [1, 2, 4]       # mA  (valid range: 0.1mA-10mA)
frequencies = [20, 50, 130]  # Hz  (valid range: 4Hz-5000Hz)
pulse_widths = [75, 150]     # microseconds (just leave as is)
stimulation_duration = 500   # ms (total time stimulation will occur for a series of pulses, constant in this case for all parameter combinations)
### Locations specific to subject and cables used, prepared with Matlab code, and saved in /subject_cofigurations/UT### folder

### General parameters
trials_per_combination = 20 #trials for each possible combination of stimulation parameters
p_sham_trials = 3 #percentage of times (integer from 0-100) that sham event will occur throughout run
classification_duration = 1200 # milliseconds (duration of recording event used in classifier)
post_stim_lockout = 400 # milliseconds (wait time for next event following stimulation)
configuration_wait = 100 # milliseconds (wait time for server to receive and process stimulation configuration)
n_sync_pulses_burst = 25 # pulses in a burst
inter_burst_time = 50 #milliseconds
inter_sync_pulses_interval = 5000 # milliseconds
sync_pulses_jitter = 300 # milliseconds
burst_wait_time = inter_burst_time * (n_sync_pulses_burst + 1) + inter_sync_pulses_interval
intertrial_interval = 500 # milliseconds
intertrial_jitter = 50 # milliseconds

####################################################################### Other Variables Used ###########################################################################

### Making a dictionary to save file with the configurations used in a given session
configuration_dictionary = {
    'pre_stim_classification_duration': classification_duration,
    'post_stim_classification_duration': classification_duration,
    'stimulation_duration': stimulation_duration,
    'post_stim_lockout': post_stim_lockout,
    'intertrial_interval': intertrial_interval,
    'intertrial_jitter': intertrial_jitter
}

### List of directories with experiment resources and subject files
this_file = os.path.abspath(__file__)
base_directory = os.path.dirname(os.path.dirname(this_file)) + '/'
task_directory = os.path.dirname(this_file) + '/'
resources_directory = base_directory + 'resources/'
image_directory = resources_directory + 'images/gui_backgrounds/'
configurations_directory = resources_directory + 'subject_configurations/'
data_directory = task_directory + 'subject_files/'

### File names for experiment resources
GUI_background = image_directory + 'stimulation_parameter_search_GUI.png'

### Definitions of fieldnames that will go into each type of event file
events_fieldnames = [
    'subject', 'session', 'event_type', 'label', 'anode', 'cathode',
    'amplitude', 'frequency', 'pulse_width', 'duration', 'time', 'trial_index']

notes_fieldnames = ['subject', 'session', 'note', 'time']

pulses_fieldnames = ['subject', 'session', 'time', 'pulse_id']

communications_fieldnames = [
    'subject', 'session', 'message_type', 'data', 'sender',
    'server_time', 'client_time', 'message_id']

ratings_fieldnames = ['subject', 'session', 'test', 'scale', 'rating', 'time']

scores_fieldnames = ['subject', 'session', 'test', 'score', 'time']

checkpoint_fieldnames = ['subject', 'session', 'experiment_block', 'trial_index']

parameter_fieldnames = ['location', 'amplitude', 'frequency', 'pulse_width']

location_fieldnames = ['label', 'anode', 'cathode']

### Getting screen size to adjust the size of GUI screen and button positions
display_id = Quartz.CGMainDisplayID()
screen_width = Quartz.CGDisplayPixelsWide(display_id)
screen_height = Quartz.CGDisplayPixelsHigh(display_id)
screen_size = (screen_width, screen_height)
f_width = screen_width/1920
f_height = screen_height/1080

############################# Button parameters ##################################

### General controls
controls_x = 90 * f_width
controls_y_start = 280 * f_height
controls_y_end = 805 * f_height
controls_y = np.linspace(controls_y_start, controls_y_end, 6).tolist()
controls_width = 60 * f_width
controls_height = 60 * f_height

### Psychiatric scales and ratings
ratings_width = 240 * f_width
ratings_height = 36 * f_height
update_width = 200 * f_width
update_height = 36 * f_height

######################################## PANSS scales and ratings ######################################################

PANSS_scales = ['P01_delusion', 'P02_disorganization', 'P03_hallucination', 'P04_excitement',
                'P05_grandiosity', 'P06_suspiciousness', 'P07_hostility',
                'N01_affect', 'N02_emotional', 'N03_rapport', 'N04_apathy',
                'N05_abstraction', 'N06_spontaneity', 'N07_stereotyped',
                'G01_somatic', 'G02_anxiety', 'G03_guilt', 'G04_tension',
                'G05_posturing', 'G06_depression', 'G07_motor-retardation',
                'G08_uncooperative', 'G09_unusual-thoughts', 'G10_disorientation',
                'G11_attention', 'G12_judgement', 'G13_volition', 'G14_impulse',
                'G15_preoccupation', 'G16_avoidance']
n_PANSS_scales = len(PANSS_scales)
PANSS_ratings = ['Absent', 'Minimal', 'Mild', 'Moderate', 'Moderate-Severe', 'Severe', 'Extreme']
PANSS_ratings_x1 = 260 * f_width
PANSS_ratings_x2 = 520 * f_width
PANSS_ratings_x3 = 780 * f_width
PANSS_ratings_x4 = 1040 * f_width
PANSS_ratings_x = [PANSS_ratings_x1] * 7 + [PANSS_ratings_x2] * 7 + [PANSS_ratings_x3] * 8 + [PANSS_ratings_x4] * 8
ratings_y_start = 120 * f_height
ratings_y_end = 645 * f_height
y_positions = np.linspace(ratings_y_start, ratings_y_end, 8).tolist()
PANSS_ratings_y = y_positions[:7] * 2 + y_positions[:8] * 2
PANSS_update_x = 1060 * f_width
PANSS_update_y = 705 * f_height

####################################### YMRS scales and ratings #########################################################

YMRS_scales = ['M01_elevated-mood', 'M02_hyperactivity', 'M03_sexual-interest', 'M04_sleep',
                'M05_irritability', 'M06_speech', 'M07_thought-order',
                'M08_thought-content', 'M09_agressiveness', 'M10_appearance', 'M11_insight']

n_YMRS_scales = len(YMRS_scales)
YMRS_doubles = ['M05_irritability', 'M06_speech', 'M08_thought-content', 'M09_agressiveness']
YMRS_ratings_singles = ['0', '1', '2', '3', '4']
YMRS_ratings_doubles = ['0', '2', '4', '6', '8']
YMRS_ratings_x1 = 1360 * f_width
YMRS_ratings_x2 = 1620 * f_width
YMRS_ratings_x = [YMRS_ratings_x1] * 6 + [YMRS_ratings_x2] * 5
ratings_y_start = 80 * f_height
ratings_y_end = 455 * f_height
y_positions = np.linspace(ratings_y_start, ratings_y_end, 6).tolist()
YMRS_ratings_y = y_positions[:6] + y_positions[:5]
YMRS_update_x = 1640 * f_width
YMRS_update_y = 515 * f_height

###################################### C-SSRS scales and ratings ########################################################

CSSRS_scales = ['S01_passive-ideation', 'S02_active-ideation', 'S03_planning', 'S04_intention',
                'S05_execution', 'S06_attempted']
n_CSSRS_scales = len(CSSRS_scales)
CSSRS_ratings = ['no', 'yes']
CSSRS_ratings_x1 = 780 * f_width
CSSRS_ratings_x2 = 1040 * f_width
CSSRS_ratings_x = [CSSRS_ratings_x1] * 3 + [CSSRS_ratings_x2] * 3
ratings_y_start = 810 * f_height
ratings_y_end = 960 * f_height
y_positions = np.linspace(ratings_y_start, ratings_y_end, 3).tolist()
CSSRS_ratings_y = y_positions[:3] * 2
CSSRS_update_x = 1060 * f_width
CSSRS_update_y = 1020 * f_height

####################################### MDRAS scales and ratings #########################################################

MDRAS_scales = ['D01_apparent-sadness', 'D02_reported-sadness', 'D03_inner-tension', 'D04_reduced-sleep',
                'D05_reduced-appetite', 'D06_concentration', 'D07_lassitude',
                'D08_feelings', 'D09_pessimism', 'D10_SI']
n_MDRAS_scales = len(MDRAS_scales)
MDRAS_ratings = ['0', '1', '2', '3', '4', '5', '6']
MDRAS_ratings_x1 = 1360 * f_width
MDRAS_ratings_x2 = 1620 * f_width
MDRAS_ratings_x = [MDRAS_ratings_x1] * 5 + [MDRAS_ratings_x2] * 5
ratings_y_start = 660 * f_height
ratings_y_end = 960 * f_height
y_positions = np.linspace(ratings_y_start, ratings_y_end, 5).tolist()
MDRAS_ratings_y = y_positions[:5] * 2
MDRAS_update_x = 1640 * f_width
MDRAS_update_y = 1020 * f_height

################################### Self report scales and ratings ########################################################

self_scales = ['R01_symptom-severity']
n_self_scales = len(self_scales)
self_ratings = ['1-worst', '2', '3', '4', '5', '6', '7', '8', '9', '10-best']
self_ratings_x = 260 * f_width
self_ratings_y = 960 * f_height
self_update_x = 308 * f_width
self_update_y = 1020 * f_height

n_psych_scales = n_PANSS_scales + n_MDRAS_scales + n_CSSRS_scales + n_YMRS_scales + n_self_scales
ratings_style = 'light-outline'

#############################################################
### Variables to be initialized prior to experiment start ###
#############################################################

datetime_format = '%Y-%m-%d_%H-%M-%S_%f'
stimulation_thread = None
stop_stimulation = True
sync_pulses_thread = None
stop_sync_pulses = True
sync_pulses_burst_thread = None
PANSS_scale_scores = [1] * n_PANSS_scales
PANSS_score = sum(PANSS_scale_scores)
YMRS_scale_scores = [0] * n_YMRS_scales
YMRS_score = sum(YMRS_scale_scores)
CSSRS_scale_scores = [0] * n_CSSRS_scales
CSSRS_score = sum(CSSRS_scale_scores)
MDRAS_scale_scores = [0] * n_MDRAS_scales
MDRAS_score = sum(MDRAS_scale_scores)
self_scale_scores = [0] * n_self_scales
self_score = sum(self_scale_scores)
block = 0
trial_index = 0
message_id = 1
pulse_id = 1
note_id = 1