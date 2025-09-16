"""
Configuarions for Stimulation Controller GUI

This document contains experiment variables that can be modified ('Editable Parameters')
and experiment variables set for use during experiment run time. Important experiment
variables are stored in a dictionary so that they can be saved as a file during experiment
run time.

"""

import os
import numpy as np

########################################################################################################################################################################

######################################################################## Editable Parameters ###########################################################################

experiment_name = 'stimulation_controller' # Folder with code and directories should have the same name
valid_subject_code_prefix = 'SC'
prefix_length = len(valid_subject_code_prefix)
n_subject_code_digits = 3
valid_subject_code_length = prefix_length + n_subject_code_digits
digit_string = '#' * n_subject_code_digits

### Enable connection to server
server_connection_enabled = True
server_ip = '127.0.0.1'
server_port = 5000

### Parameters being searched over
parameter_types = ['amplitude', 'frequency', 'pulse_width', 'duration', 'location']
n_parameter_types = len(parameter_types)
amplitudes = [4, 8]                # mA  (valid range: 0.1mA-10mA)
frequencies = [60, 120, 180]       # Hz  (valid range: 4Hz-5000Hz)
pulse_widths = [75, 150]           # microseconds (just leave as is)
durations = [10000, 20000, 30000]  # ms duration of stimulation pulse series
###Locations specific to subject and cables used, prepared with Matlab code, and saved in subject_data folder

###General parameters
post_stim_lockout = 400 #milliseconds
stimulation_duration = 500 #milliseconds
n_sync_pulses_burst = 25 #pulses in a burst
inter_burst_time = 50 #milliseconds
burst_wait_time = inter_burst_time * (n_sync_pulses_burst + 1)
inter_sync_pulses_interval = 5000 #milliseconds
sync_pulses_jitter = 300 #milliseconds

####################################################################### Other Variables Used ###########################################################################

### Making a dictionary to save file with the configurations used in a given session
configuration_dictionary = {
    'post_stim_lockout': post_stim_lockout,
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
GUI_background = image_directory + 'stimulation_controller_GUI.png'

### Definitions of fieldnames that will go into each type of event file
events_fieldnames = [
    'subject', 'session', 'location', 'amplitude', 'frequency',
    'pulse_width', 'time', 'trial_idx']

notes_fieldnames = ['subject', 'session', 'note', 'time', 'note_id']

pulses_fieldnames = ['subject', 'session', 'time', 'pulse_id']

communications_fieldnames = [
    'subject', 'session', 'message_type', 'data', 'sender', 
    'server_time', 'client_time', 'message_id']

parameter_fieldnames = ['location', 'amplitude', 'frequency', 'pulse_width']

location_fieldnames = ['label', 'anode', 'cathode']

### Adjusting sizes based on size of GUI background .png to smaller size
f_width = 675/745
f_height = 775/877
gui_width = int(745 * f_width)
gui_height = int(877 * f_height)

############ Parameters of GUI elements ############
parameter_box_width = 130 * f_width
parameter_box_height = 40 * f_height
parameter_box_x = 178 * f_width
parameter_box_y = np.linspace(175, 475, 5) * f_height

control_size = 100 * f_width
start_x = 400 * f_width
stop_x = 550 * f_width
sync_y = 225 * f_height
stimulus_y = 375 * f_height

notes_width = 655 * f_width
notes_height = 140 * f_height
notes_x = 42 * f_width
notes_y = 635 * f_height
enter_width = 160 * f_width
enter_height = 45 * f_height
enter_x = 550 * f_width
enter_y = 800 * f_height

#############################################################
### Variables to be initialized prior to experiment start ###
#############################################################

datetime_format = '%Y-%m-%d_%H-%M-%S_%f'
stimulation_thread = None
stop_stimulation = True
sync_pulses_thread = None
stop_sync_pulses = True
sync_pulse_burst_thread = None
trial_idx = 1
message_id = 1
pulse_id = 1
note_id = 1