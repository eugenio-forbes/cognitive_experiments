"""
Stimulation Parameter Search Experiment

This code runs a session of the experiment.
For details about experiment structure view initialize_experiment.py
For details about experiment parameters view configuration.py

"""

from smile.pennsyncbox import *
import pandas as pd
import numpy as np
import os
import sys 
import socket
import json
import time
import random
from csv import DictWriter
from datetime import datetime
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import Style
import ttkbootstrap as tb
import asyncio
from threading import Thread, Event
from PIL import Image, ImageTk

### Import configuration, initialization, and experiment functions
from configuration import *
from initialize_experiment import *
from experiment_utils import *

############################################################### Experiment initialization ###############################################################################

### Prompt subject code
subject = prompt_subject_code()

### Prompt whether stimulation will be delivered
stimulation_enabled = prompt_stimulation_enabled()

### Prompt whether connecting to server (Disabled for testing stimulation commands or just using sync box)
server_connection_enabled = prompt_server_connection_enabled()

### If stimulation is to be delivered, prompt for picking depth electrode label
if stimulation_enabled:
    stimulation_label = prompt_stimulation_channel_label(subject)
else:
    stimulation_label = 'none'

### Create new folder for saving trial list, configurations, and events files using date and time as name of folder
current_time = datetime.now().strftime(datetime_format)
session = current_time
session_directory = data_directory + subject + '/' + session + '/'

### Define session files
checkpoint_file = session_directory + 'checkpoint.csv'
pulses_file = session_directory + 'pulses.csv'
events_file = session_directory + 'events.csv'
ratings_file = session_directory + 'psych_ratings.csv'
scores_file = session_directory + 'psych_scores.csv'
communications_file = session_directory + 'communications.csv'
configurations_file = session_directory + 'configurations.json'
message_dictionary_file = session_directory + 'message_dictionary.json'
stimulus_list_file = session_directory + 'stimulus_list.json'

### Generate stimulation trial list and dictionary with messages and events
if not os.path.exists(session_directory):
    os.makedirs(session_directory)
initialize_experiment_func(subject, session, session_directory, stimulation_label)

### Check that data files for experiment were created
if not os.path.isfile(checkpoint_file):
    pd.DataFrame(columns=checkpoint_fieldnames).to_csv(checkpoint_file, index=False, header=True)
    
if not os.path.isfile(pulses_file):
    pd.DataFrame(columns=pulses_fieldnames).to_csv(pulses_file, index=False, header=True)
    
if not os.path.isfile(events_file):
    pd.DataFrame(columns=events_fieldnames).to_csv(events_file, index=False, header=True)
    
if not os.path.isfile(ratings_file):
    pd.DataFrame(columns=ratings_fieldnames).to_csv(ratings_file, index=False, header=True)
    
if not os.path.isfile(scores_file):
    pd.DataFrame(columns=scores_fieldnames).to_csv(scores_file, index=False, header=True)
    
if not os.path.isfile(communications_file):
    pd.DataFrame(columns=communications_fieldnames).to_csv(communications_file, index=False, header=True)

### Allow time for files to be written before accessing
time.sleep(0.5)

### If stimulation is enabled, get trial list
if stimulation_enabled:
    with open(stimulus_list_file, 'r') as file_handle:
        stimulus_list = json.load(file_handle)
    global max_trial_index
    max_trial_index = len(stimulus_list)

### Get message dictionary (event entries in addition to server-client messages)
with open(message_dictionary_file, 'r') as file_handle:
    message_dictionary = json.load(file_handle)

global stimulation_parameters, trial_index, experiment_block, pulse_id
stimulation_parameters = message_dictionary['STIMULATION_PARAMETERS']
trial_index = 0
experiment_block = 0

##################################################################### Experiment Function Definitions ###################################################################

############################ Pulses and communications #############################

### For executing sync pulse from imported pennsyncbox.py and recording client time in which it was sent
def single_sync_pulse():
    global pulse_id
    current_time = datetime.now().strftime(datetime_format)
    SyncPulse()
    pulse_entry = message_dictionary['PULSE']
    pulse_entry['time'] = current_time
    pulse_entry['pulse_id'] = pulse_id
    with open(pulses_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=pulses_fieldnames)
        writer.writerow(pulse_entry)
    pulse_id += 1
    
### For sending message to server and logging message in communications file
def send_server_message(server_handle, communications_file, message):
    global message_id
    message['client_time'] = datetime.now().strftime(datetime_format)
    message['sender'] = 'client'
    message['message_id'] = message_id
    message_string = json.dumps(message) + '\n'

    if server_connection_enabled:
        server_handle.send(message_string.encode('utf-8'))    

    with open(communications_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=communications_fieldnames)
        writer.writerow(message)
    message_id += 1

### For receiving response from server and logging message in communications file
def receive_server_response(server_handle, communications_file):
    global message_id
    buffer = ''
    continue_loop = True
    while continue_loop:
        new_data = server_handle.recv(1024)
        if not new_data:
            break
        buffer += new_data.decode('utf-8')
        while '\n' in buffer:
            message_string, buffer = buffer.split('\n', 1)
            message = json.loads(message_string)
        if not buffer:
            continue_loop = False
    message['client_time'] = datetime.now().strftime(datetime_format)
    message['sender'] = 'server'
    message['message_id'] = message_id
    with open(communications_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=communications_fieldnames)
        writer.writerow(message)
    message_id += 1

### For executing a quicker burst of sync pulses to signal experiment start/interruptions
def sync_pulses_burst():
    for idx in range(n_sync_pulses_burst):
        print("Burst Pulse")
        single_sync_pulse()
        time.sleep(inter_burst_time / 1000)

### For executing a thread that will intermittently send sync pulses with a jittered time interval
def sync_pulses_loop():
    time.sleep(burst_wait_time / 1000)
    global stop_sync_pulses
    while not stop_sync_pulses:
        print("Sync Pulse")
        single_sync_pulse()
        if not stimulation_enabled:
            send_sham() # So that the server continues receiving messages throughout the experiment
        jittered_time_duration = np.random.normal(inter_sync_pulses_interval, sync_pulses_jitter)
        time.sleep(jittered_time_duration / 1000)

### For sending stimulation configurations as a message to server and logging events
def send_stimulus():
    global trial_index, stimulation_parameters
    message = message_dictionary['STIMULATION_CONFIGURATION']
    message['data']['label'] = stimulation_parameters['location']['label']
    message['data']['anode'] = stimulation_parameters['location']['anode']
    message['data']['cathode'] = stimulation_parameters['location']['cathode']
    message['data']['amplitude'] = stimulation_parameters['amplitude']
    message['data']['frequency'] = stimulation_parameters['frequency']
    message['data']['pulse_width'] = stimulation_parameters['pulse_width']
    message['data']['duration'] = stimulation_parameters['duration']
    
    print("Sending stimulation configurations.")
    send_server_message(server_handle, communications_file, message)
    
    event_entry = message_dictionary['EVENT']
    current_time = datetime.now().strftime(datetime_format)
    event_entry['event_type'] = 'STIMULATION_CONFIGURATION'
    event_entry['label'] = stimulation_parameters['location']['label']
    event_entry['anode'] = stimulation_parameters['location']['anode']
    event_entry['cathode'] = stimulation_parameters['location']['cathode']
    event_entry['amplitude'] = stimulation_parameters['amplitude']
    event_entry['frequency'] = stimulation_parameters['frequency']
    event_entry['pulse_width'] = stimulation_parameters['pulse_width']
    event_entry['duration'] = stimulation_parameters['duration']
    event_entry['time'] = current_time
    event_entry['trial_index'] = trial_index

    with open(events_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=events_fieldnames)
        if os.stat(events_file).st_size == 0:
            writer.writeheader()
        writer.writerow(event_entry)

    checkpoint_entry = {'subject': subject, 'session': session, 'experiment_block': experiment_block, 'trial_index': trial_index}
    with open(checkpoint_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=checkpoint_fieldnames)
        if os.stat(checkpoint_file).st_size == 0:
            writer.writeheader()
        writer.writerow(checkpoint_entry)

    print("Receiving response from Blackrock.")
    if server_connection_enabled:
        receive_server_response(server_handle, communications_file)
    
    print("Done with stimulation.")

### For sending message to server that would stop execution of stimulus
def stop_stimulus():
    message = message_dictionary['STOP_STIMULATION']
    print("Stopping stimulation.")
    send_server_message(server_handle, communications_file, message)
    print("Stopped stimulation.")
    if server_connection_enabled:
        receive_server_response(server_handle, communications_file)

### For sending message to server to deliver sham trial
def send_sham():    
    print("Sham message to Blackrock.")    
    message = message_dictionary['SHAM']
    send_server_message(server_handle, communications_file, message)
    
    event_entry = message_dictionary['EVENT']
    current_time = datetime.now().strftime(datetime_format)
    event_entry['event_type'] = 'SHAM'
    event_entry['time'] = current_time

    ### If connected to server and not delivering stimuli, 
    ### preventing server timeout by sending messages for every sync pulse
    if not stimulation_enabled:
        event_entry['event_type'] = 'SYNC_PULSE'

    with open(events_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=events_fieldnames)
        writer.writerow(event_entry)

    print("Receiving response from Blackrock.")
    if server_connection_enabled:
        receive_server_response(server_handle, communications_file) 
    print("Done with sham.")
    

### For executing a thread that will loop through stimulation parameter combinations to send to server
def stimulation_loop():
    global stop_stimulation, stimulation_parameters, trial_index, max_trial_index
    
    while not stop_stimulation and trial_index < max_trial_index:
        
        stimulation_configuration = stimulus_list[trial_index]
        
        for parameter in parameter_fieldnames:
            stimulation_parameters[parameter] = stimulation_configuration[parameter]

        ### Before sending stimulus for each trial, wait interval of time for pre-stimulus classification
        time.sleep(classification_duration / 1000)
        
        ### Will randomly send sham instead p_sham_trials/100 times
        random_number = random.randint(1, 100)
        if random_number <= p_sham_trials:
            send_sham()
        else:
            send_stimulus()
            trial_index += 1
        
        ### After sending stimulus/sham, wait time of stimulus delivery, stimulation decay, and time for post-stimulus classification
        time.sleep(stimulation_duration / 1000)
        time.sleep(post_stim_lockout / 1000)
        time.sleep(classification_duration / 1000)

        ### Wait jittered intertrial interval before starting next trial
        jittered_time_duration = np.random.normal(intertrial_interval, intertrial_jitter)
        time.sleep(jittered_time_duration / 1000)

    if trial_index == max_trial_index:
        print("Max trial index for stimulation loop reached. Experiment ended.")
        on_closing()

################################## GUI Button Commands ####################################

### Series of functions to be executed after clicking on "Stop Sync" button
def command_stop_sync():
    command_stop_stimulus()
    start_experiment_button.configure(state='normal')
    end_experiment_button.configure(state='disabled')
    activate_stimulation_button.configure(state='disabled')
    deactivate_stimulation_button.configure(state='disabled')
    global sync_pulses_thread, sync_pulses_burst_thread, stop_sync_pulses
    stop_sync_pulses = True
    sync_pulses_burst_thread = Thread(target=sync_pulses_burst, daemon=True)
    sync_pulses_burst_thread.start()
    
### Series of functions to be executed after clicking on 'Send Stimulus' button
def command_send_stimulus():
    activate_stimulation_button.configure(state='disabled')
    deactivate_stimulation_button.configure(state='normal')
    send_stimulus_thread = Thread(target=send_stimulus, daemon=True)
    send_stimulus_thread.start()

### Series of functions to be executed after clicking on 'Stop Stimulus' button
def command_stop_stimulus():
    activate_stimulation_button.configure(state='normal')
    deactivate_stimulation_button.configure(state='disabled')
    stop_stimulus_thread = Thread(target=stop_stimulus, daemon=True)
    stop_stimulus_thread.start()

### For enabling experiment controls only when experiment is started (and sync pulses are sent)
def command_experiment_start():
    sync_pulses_burst_thread = Thread(target=sync_pulses_burst, daemon=True)
    sync_pulses_burst_thread.start()
    
    global sync_pulses_thread, stop_sync_pulses
    if stimulation_enabled:
        stimulation_button_state = 'normal'
    else:
        stimulation_button_state = 'disabled'
    
    start_experiment_button.configure(state='disabled')
    end_experiment_button.configure(state='normal')
    injection_start_button.configure(state='normal')
    activate_stimulation_button.configure(state=stimulation_button_state)
    for idx in range(n_psych_scales):
        ratings_boxes[idx].configure(state='normal')
    PANSS_update_button.configure(state='normal')
    MDRAS_update_button.configure(state='normal')
    CSSRS_update_button.configure(state='normal')
    YMRS_update_button.configure(state='normal')
    self_update_button.configure(state='normal')
    if sync_pulses_thread is None or not sync_pulses_thread.is_alive():
        stop_sync_pulses = False
        sync_pulses_thread = Thread(target=sync_pulses_loop, daemon=True)
        sync_pulses_thread.start()

### For stopping and disabling stimulation when injection is to be delivered (and logging injection start time)
def command_injection_start():
    global stimulation_thread, stop_stimulation
    stop_stimulation = True
    injection_start_button.configure(state='disabled')
    injection_end_button.configure(state='normal')
    activate_stimulation_button.configure(state='disabled')
    deactivate_stimulation_button.configure(state='disabled')
    
    event_entry = message_dictionary['EVENT']
    current_time = datetime.now().strftime(datetime_format)
    event_entry['event_type'] = 'INJECTION_START'
    event_entry['time'] = current_time
    with open(events_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=events_fieldnames)
        if os.stat(events_file).st_size == 0:
            writer.writeheader()
        writer.writerow(event_entry)

### For reenabling stimulation controls when injection has ended (and logging injection end time)
def command_injection_end():
    if stimulation_enabled:
        stimulation_button_state = 'normal'
    else:
        stimulation_button_state = 'disabled'
    injection_start_button.configure(state='normal')  
    injection_end_button.configure(state='disabled')
    activate_stimulation_button.configure(state=stimulation_button_state)

    event_entry = message_dictionary['EVENT']
    current_time = datetime.now().strftime(datetime_format)
    event_entry['event_type'] = 'INJECTION_END'
    event_entry['time'] = current_time
    with open(events_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=events_fieldnames)
        if os.stat(events_file).st_size == 0:
            writer.writeheader()
        writer.writerow(event_entry)

### For enabling stimulation delivery thread. Button is disabled after clicked. Enables deactivate stimulation button.
def command_activate_stimulation():
    global stop_stimulation
    activate_stimulation_button.configure(state='disabled')
    deactivate_stimulation_button.configure(state='normal')
    stop_stimulation = False
    stimulation_thread = Thread(target=stimulation_loop, daemon=True)
    stimulation_thread.start()

### For sending Blackrock a message to stop stimulus. Start stimulation button is reenabled.
def command_deactivate_stimulation():
    command_stop_stimulus()
    global stimulation_thread, stop_stimulation
    activate_stimulation_button.configure(state='normal')
    deactivate_stimulation_button.configure(state='disabled')
    stop_stimulation = True

### For logging psychiatric scale ratings entered in GUI
def command_ratings_box(psychiatric_scale, scale_type, ratings_box, idx):
    current_time = datetime.now().strftime(datetime_format)
    scale_ratings_index = ratings_box.current()
    global PANSS_scale_scores, YMRS_scale_scores, CSSRS_scale_scores, MDRAS_scale_scores, self_scale_scores
    
    if psychiatric_scale == 'PANSS':
        scale_score = scale_ratings_index + 1
        PANSS_scale_scores[idx] = scale_score
    elif psychiatric_scale == 'YMRS':
        scale_score = scale_ratings_index + 1
        if scale_type in YMRS_doubles:
            scale_score = 2 * scale_score
        YMRS_scale_scores[idx] = scale_score
    elif psychiatric_scale == 'CSSRS':
        scale_score = scale_ratings_index
        CSSRS_scale_scores[idx] = scale_score
    elif psychiatric_scale == 'MDRAS':
        scale_score = scale_ratings_index + 1
        MDRAS_scale_scores[idx] = scale_score
    elif psychiatric_scale == 'self':
        scale_score = scale_ratings_index + 1
        self_scale_scores[idx] = scale_score

    ratings_entry = {'subject': subject, 'session': session, 'test': psychiatric_scale, 'scale': scale_type,
                    'rating': scale_score, 'time': current_time}

    with open(ratings_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=ratings_fieldnames)
        if os.stat(ratings_file).st_size == 0:
            writer.writeheader()
        writer.writerow(ratings_entry)

### For logging sums of psychiatric scale ratings (scores) after pressing update button in GUI
def command_score_update(psychiatric_scale):
    current_time = datetime.now().strftime(datetime_format)

    global PANSS_scale_scores, PANSS_score, YMRS_scale_scores, YMRS_score
    global CSSRS_scale_scores, CSSRS_score, MDRAS_scale_scores, MDRAS_score
    
    if psychiatric_scale == 'PANSS':
        PANSS_score = sum(PANSS_scale_scores)
        score = PANSS_score
    elif psychiatric_scale == 'YMRS':
        YMRS_score = sum(YMRS_scale_scores)
        score = YMRS_score
    elif psychiatric_scale == 'CSSRS':
        CSSRS_score = sum(CSSRS_scale_scores)
        score = CSSRS_score
    elif psychiatric_scale == 'MDRAS':
        MDRAS_score = sum(MDRAS_scale_scores)
        score = MDRAS_score
    elif psychiatric_scale == 'self':
        self_score = sum(self_scale_scores)
        score = self_score

    scores_entry = {'subject': subject, 'session': session, 'test': psychiatric_scale, 'score': score, 'time': current_time}

    with open(scores_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=scores_fieldnames)
        if os.stat(scores_file).st_size == 0:
            writer.writeheader()
        writer.writerow(scores_entry)

############################## Other functions #######################################

### Series of functions to execute when clicking on 'Stop experiment' or window closing.
### Will stop current stimulus, stop stimulation thread, stop sync pulse thread, 
### send a burst of sync pulses to signal session end, close server connection, and close GUI.
def on_closing():
    command_stop_stimulus()
    global sync_pulses_thread, stimulation_thread, stop_stimulation, sync_pulses_burst_thread, stop_sync_pulses
    stop_sync_pulses = True
    stop_stimulation = True
    
    sync_pulses_burst_thread = Thread(target=sync_pulses_burst, daemon=False)
    sync_pulses_burst_thread.start()
    
    message = message_dictionary['END']
    print("Closing server.")
    send_server_message(server_handle, communications_file, message)
    if server_connection_enabled:
        server_handle.close()
    root.destroy()
    sys.exit()

################################################################### Initialization of GUI Window #########################################################################
root = tk.Tk()
root.title('Ketamine Experiment Client')
root.geometry(f'{screen_width}x{screen_height}')
root.resizable(False, False)
root.attributes('-fullscreen', True)
root.protocol('WM_DELETE_WINDOW', on_closing)
root.bind('<Command-q>', on_closing)

### Addition of background image to GUI
my_canvas = tk.Canvas(root, width=screen_width, height=screen_height, bd=0, highlightthickness=0)
my_canvas.pack(fill='both', expand=True)
background = Image.open(GUI_background)
GUI_image = ImageTk.PhotoImage(background.resize((screen_width, screen_height), Image.ANTIALIAS))
GUI_image_ID = my_canvas.create_image(0, 0, image=GUI_image, anchor='nw')

### Addition of experiment control buttons
start_experiment_button = tk.ttk.Button(root, command=command_experiment_start)
start_experiment_button.place(x=controls_x, y=controls_y[0], width=controls_width, height=controls_height)

end_experiment_button = tk.ttk.Button(root, command=on_closing, state='disabled')
end_experiment_button.place(x=controls_x, y=controls_y[1], width=controls_width, height=controls_height)

injection_start_button = tk.ttk.Button(root, command=command_injection_start, state='disabled')
injection_start_button.place(x=controls_x, y=controls_y[2], width=controls_width, height=controls_height)

injection_end_button = tk.ttk.Button(root, command=command_injection_end, state='disabled')
injection_end_button.place(x=controls_x, y=controls_y[3], width=controls_width, height=controls_height)

activate_stimulation_button = tk.ttk.Button(root, command=command_activate_stimulation, state='disabled')
activate_stimulation_button.place(x=controls_x, y=controls_y[4], width=controls_width, height=controls_height)

deactivate_stimulation_button = tk.ttk.Button(root, command=command_deactivate_stimulation, state = 'disabled')
deactivate_stimulation_button.place(x=controls_x, y=controls_y[5], width=controls_width, height=controls_height)

### Addition of boxes for ratings and scoring
ratings_boxes = []
for idx in range(n_PANSS_scales):
    ratings_box = tk.ttk.Combobox(root, values=PANSS_ratings, state='disabled')
    ratings_box.place(x=PANSS_ratings_x[idx], y=PANSS_ratings_y[idx], width=ratings_width, height=ratings_height)
    ratings_box.set(PANSS_ratings[0])
    ratings_box.bind('<<ComboboxSelected>>', lambda event, idx=idx, ratings_box=ratings_box: command_ratings_box('PANSS', PANSS_scales[idx], ratings_box, idx))
    ratings_boxes.append(ratings_box)

for idx in range(n_YMRS_scales):
    if YMRS_scales[idx] in YMRS_doubles:
        YMRS_ratings = YMRS_ratings_doubles.copy()
    else:
        YMRS_ratings = YMRS_ratings_singles.copy()
    ratings_box = tk.ttk.Combobox(root, values=YMRS_ratings, state='disabled')
    ratings_box.place(x=YMRS_ratings_x[idx], y=YMRS_ratings_y[idx], width=ratings_width, height=ratings_height)
    ratings_box.set(YMRS_ratings[0])
    ratings_box.bind('<<ComboboxSelected>>', lambda event, idx=idx, ratings_box=ratings_box: command_ratings_box('YMRS', YMRS_scales[idx], ratings_box, idx))
    ratings_boxes.append(ratings_box)

for idx in range(n_CSSRS_scales):
    ratings_box = tk.ttk.Combobox(root, values=CSSRS_ratings, state='disabled')
    ratings_box.place(x=CSSRS_ratings_x[idx], y=CSSRS_ratings_y[idx], width=ratings_width, height=ratings_height)
    ratings_box.set(CSSRS_ratings[0])
    ratings_box.bind('<<ComboboxSelected>>', lambda event, idx=idx, ratings_box=ratings_box: command_ratings_box('CSSRS', CSSRS_scales[idx], ratings_box, idx))
    ratings_boxes.append(ratings_box)

for idx in range(n_MDRAS_scales):
    ratings_box = tk.ttk.Combobox(root, values=MDRAS_ratings, state='disabled')
    ratings_box.place(x=MDRAS_ratings_x[idx], y=MDRAS_ratings_y[idx], width=ratings_width, height=ratings_height)
    ratings_box.set(MDRAS_ratings[0])
    ratings_box.bind('<<ComboboxSelected>>', lambda event, idx=idx, ratings_box=ratings_box: command_ratings_box('MDRAS', MDRAS_scales[idx], ratings_box, idx))
    ratings_boxes.append(ratings_box)

for idx in range(n_self_scales):
    ratings_box = tk.ttk.Combobox(root, values=self_ratings, state='disabled')
    ratings_box.place(x=self_ratings_x, y=self_ratings_y, width=ratings_width, height=ratings_height)
    ratings_box.set(self_ratings[-1:])
    ratings_box.bind('<<ComboboxSelected>>', lambda event, idx=idx, ratings_box=ratings_box: command_ratings_box('self', self_scales[idx], ratings_box, idx))
    ratings_boxes.append(ratings_box)

### Addition of buttons to update scores
PANSS_update_button = tk.ttk.Button(root, text='Update PANSS', command=lambda: command_score_update('PANSS'), state='disabled')
PANSS_update_button.place(x=PANSS_update_x, y=PANSS_update_y, width=update_width, height=update_height)

YMRS_update_button = tk.ttk.Button(root, text='Update YMRS', command=lambda: command_score_update('YMRS'), state='disabled')
YMRS_update_button.place(x=YMRS_update_x, y=YMRS_update_y, width=update_width, height=update_height)

CSSRS_update_button = tk.ttk.Button(root, text='Update CSSRS', command=lambda: command_score_update('CSSRS'), state='disabled')
CSSRS_update_button.place(x=CSSRS_update_x, y=CSSRS_update_y, width=update_width, height=update_height)

MDRAS_update_button = tk.ttk.Button(root, text='Udate MDRAS', command=lambda: command_score_update('MDRAS'), state='disabled')
MDRAS_update_button.place(x=MDRAS_update_x, y=MDRAS_update_y, width=update_width, height=update_height)

self_update_button = tk.ttk.Button(root, text='Udate Rating', command=lambda: command_score_update('self'), state='disabled')
self_update_button.place(x=self_update_x, y=self_update_y, width=update_width, height=update_height)

########################################################################### Experiment Start ############################################################################

### Keeping this this way: It was previously said that as of macOS10.15, 
### opening a U6 the first time after plugging it in sometimes fails,
### and that subsequent attempts to open succeed. These functions will connect
### task to pennsyncbox device.
CloseUSB()
OpenUSB()
CloseUSB()
OpenUSB()

### Establish connection with server
if server_connection_enabled:
    server_handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_handle.connect((server_ip, server_port))
    message = message_dictionary['CONNECTED']
    print("Connected to server.")
    send_server_message(server_handle, communications_file, message)
    receive_server_response(server_handle, communications_file)

### Function that will start execution of GUI for experiment to be started
root.mainloop()

############################################################################# Experiment End #############################################################################

### If all trials were completed with no interruptions, file created to lock session
if experiment_block == 1 and trial_index == max_trial_index:
    lock_session(lock_file)

### After the GUI finishes executing:
### Disconnect USB, send ending message to server, and close server.
CloseUSB()
if server_connection_enabled:
    message = message_dictionary['END']
    print("Closing server.")
    send_server_message(server_handle, communications_file, message)
    receive_server_response(server_handle, communications_file)
    server_handle.close()