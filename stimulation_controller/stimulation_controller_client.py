"""
Stimulation Controller GUI

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

### Create new folder for saving trial list, configurations, and events files using date and time as name of folder
current_time = datetime.now().strftime(datetime_format)
session = current_time
session_directory = data_directory + subject + '/' + session + '/'
os.makedirs(session_directory)

initialize_experiment_func(subject, session, session_directory)

### Define session files
pulses_file = session_directory + 'pulses.csv'
events_file = session_directory + 'events.csv'
notes_file = session_directory + 'notes.csv'
communications_file = session_directory + 'communications.csv'
message_dictionary_file = session_directory + 'message_dictionary.json'
parameters_file = session_directory + 'possible_stimulation_parameters.json'
    
if not os.path.isfile(pulses_file):
    pd.DataFrame(columns=pulses_fieldnames).to_csv(pulses_file, index=False, header=True)
    
if not os.path.isfile(events_file):
    pd.DataFrame(columns=events_fieldnames).to_csv(events_file, index=False, header=True)
    
if not os.path.isfile(notes_file):
    pd.DataFrame(columns=notes_fieldnames).to_csv(notes_file, index=False, header=True)
    
if not os.path.isfile(communications_file):
    pd.DataFrame(columns=communications_fieldnames).to_csv(communications_file, index=False, header=True)

### Allow time for files to be written before accessing
time.sleep(0.5)

### Get possible stimulation parameters
with open(parameters_file, 'r') as file_handle:
    possible_stimulation_parameters = json.load(file_handle)

### Get message dictionary (event entries in addition to server-client messages)
with open(message_dictionary_file, 'r') as file_handle:
    message_dictionary = json.load(file_handle)

stimulation_parameters = message_dictionary['STIMULATION_PARAMETERS']

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
def send_server_message(server, communications_file, message):
    global message_id
    
    message['client_time'] = datetime.now().strftime(datetime_format)
    message['sender'] = 'client'
    message['message_id'] = message_id
    message_string = json.dumps(message) + '\n'

    if server_connection_enabled:
        server.send(message_string.encode('utf-8'))    
    
    with open(communications_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=communications_fieldnames)
        writer.writerow(message)
    
    message_id += 1

### For receiving response from server and logging message in communications file
def receive_server_response(server, communications_file):
    global message_id
    
    buffer = ''
    continue_loop = True
    
    while continue_loop:
        new_data = server.recv(1024)
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
        time.sleep(inter_burst_time/1000)

### For executing a thread that will intermittently send sync pulses with a jittered time interval
def sync_pulses_loop():
    time.sleep(burst_wait_time/1000)
    global stop_sync_pulses
    while not stop_sync_pulses:
        print("Sync Pulse")
        single_sync_pulse()
        jittered_time_duration = np.random.normal(inter_sync_pulses_interval, sync_pulses_jitter)
        time.sleep(jittered_time_duration/1000)

### For sending stimulation configurations as a message to server
def send_stimulus():
    global trial_idx, stimulation_parameters
    message = message_dictionary['STIMULATION_CONFIGURATION'].copy()
    message['data']['label'] = stimulation_parameters['location']['label']
    message['data']['anode'] = stimulation_parameters['location']['anode']
    message['data']['cathode'] = stimulation_parameters['location']['cathode']
    message['data']['amplitude'] = stimulation_parameters['amplitude']
    message['data']['frequency'] = stimulation_parameters['frequency']
    message['data']['pulse_width'] = stimulation_parameters['pulse_width']
    message['data']['duration'] = stimulation_parameters['duration']
    
    print("Sending stimulation configurations.")
    send_server_message(server, communications_file, message)
    
    event_entry = message_dictionary['EVENT']
    current_time = datetime.now().strftime(datetime_format)
    event_entry['label'] = stimulation_parameters['location']['label']
    event_entry['anode'] = stimulation_parameters['location']['anode']
    event_entry['cathode'] = stimulation_parameters['location']['cathode']
    event_entry['amplitude'] = stimulation_parameters['amplitude']
    event_entry['frequency'] = stimulation_parameters['frequency']
    event_entry['pulse_width'] = stimulation_parameters['pulse_width']
    event_entry['duration'] = stimulation_parameters['duration']
    event_entry['time'] = current_time
    event_entry['trial_idx'] = trial_idx

    print("Receiving response from Blackrock.")
    
    if server_connection_enabled:
        receive_server_response(server, communications_file)
    
    time.sleep(stimulation_duration/1000)
    time.sleep(post_stim_lockout/1000)
    time.sleep(0.1)
    trial_idx = trial_idx + 1

### For sending message to server that would stop execution of stimulus
def stop_stimulus():
    message = message_dictionary['STOP_STIMULATION']
    
    print("Stopping stimulation.")
    send_server_message(server, communications_file, message)
    
    print("Stopped stimulation.")
    if server_connection_enabled:
        receive_server_response(server, communications_file)

################################## GUI Button Commands ####################################

### Series of functions to be executed after clicking on 'Start Sync' button
def command_start_sync():
    global sync_pulses_thread, sync_pulses_burst_thread, stop_sync_pulses
    start_sync_button.configure(state='disabled')
    stop_sync_button.configure(state='normal')
    send_stimulus_button.configure(state='normal')
    for idx in range(n_parameter_types):
        parameter_boxes[idx].configure(state='normal')
    clear_note_button.configure(state='normal')
    enter_note_button.configure(state='normal')
    stop_sync_pulses = False
    sync_pulses_burst_thread = Thread(target=sync_pulses_burst, daemon=True)
    sync_pulses_burst_thread.start()
    sync_pulses_thread = Thread(target=sync_pulses_loop, daemon=True)
    sync_pulses_thread.start()

### Series of functions to be executed after clicking on 'Stop Sync' button
def command_stop_sync():
    command_stop_stimulus()
    start_sync_button.configure(state='normal')
    stop_sync_button.configure(state='disabled')
    send_stimulus_button.configure(state='disabled')
    stop_stimulus_button.configure(state='disabled')
    for idx in range(n_parameter_types):
        parameter_boxes[idx].configure(state='disabled')
    clear_note_button.configure(state='disabled')
    enter_note_button.configure(state='disabled')
    global sync_pulses_thread, sync_pulses_burst_thread, stop_sync_pulses
    stop_sync_pulses = True
    sync_pulses_burst_thread = Thread(target=sync_pulses_burst, daemon=True)
    sync_pulses_burst_thread.start()
    
### Series of functions to be executed after clicking on 'Send Stimulus' button
def command_send_stimulus():
    send_stimulus_button.configure(state='disabled')
    stop_stimulus_button.configure(state='normal')
    send_stimulus_thread = Thread(target=send_stimulus, daemon=True)
    send_stimulus_thread.start()

### Series of functions to be executed after clicking on 'Stop Stimulus' button
def command_stop_stimulus():
    send_stimulus_button.configure(state='normal')
    stop_stimulus_button.configure(state='disabled')
    stop_stimulus_thread = Thread(target=stop_stimulus, daemon=True)
    stop_stimulus_thread.start()

### Updating global stimulation parameter after interacting with parameter boxes
def command_update_parameter(idx, parameter_type, parameter_index):
    global stimulation_parameters, possible_stimulation_parameters
    stimulation_parameters[parameter_type] = possible_stimulation_parameters[parameter_type][parameter_index]
    print(parameter_type)
    print(parameter_index)

### Command to clear note text box after clicking 'Clear' button
def command_clear_text():
    global note_entry_box
    note_entry_box.delete(1.0, tk.END)

### Command for saving entry in notes.csv file
def command_enter_note():
    current_time = datetime.now().strftime(datetime_format)
    global note_entry_box, note_id
    note_text = note_entry_box.get(1.0, tk.END)
    note_entry = message_dictionary['NOTE']
    note_entry['note'] = note_text
    note_entry['note_id'] = note_id
    note_entry['time'] = current_time
    with open(notes_file, 'a') as file_handle:
        writer = DictWriter(file_handle, fieldnames=notes_fieldnames)
        writer.writerow(note_entry)
    note_id += 1
    note_entry_box.delete(1.0, END)


############################## Other functions #######################################

### Series of functions to execute when clicking on 'Stop experiment' or window closing.
### Will stop current stimulus, stop stimulation thread, stop sync pulse thread, 
### send a burst of sync pulses to signal session end, close server connection, and close GUI.
def on_closing():
    command_stop_stimulus()
    global sync_pulses_thread, sync_pulses_burst_thread, stop_sync_pulses
    stop_sync_pulses = True
    
    sync_pulses_burst_thread = Thread(target=sync_pulses_burst, daemon=False)
    sync_pulses_burst_thread.start()
    
    message = message_dictionary['END']
    print("Closing server.")
    send_server_message(server, communications_file, message)
        
    if server_connection_enabled:
        server.close()

    root.destroy()
    sys.exit()

######################################################################## GUI Window Initialization ######################################################################
root = tk.Tk()
root.title('Stimulation Client')
root.geometry(f'{gui_width}x{gui_height}')
root.resizable(False, False)
root.protocol('WM_DELETE_WINDOW', on_closing)
root.bind('<Command-q>', on_closing)

my_canvas = tk.Canvas(root, width=gui_width, height=gui_height, bd=0, highlightthickness=0)
my_canvas.pack(fill='both', expand=True)
background = Image.open(GUI_background)
GUI_image = ImageTk.PhotoImage(background.resize((gui_width, gui_height), Image.ANTIALIAS))
GUI_image_ID = my_canvas.create_image(0, 0, image=GUI_image, anchor='nw')

### Addition of experiment control buttons
start_sync_button = tk.ttk.Button(root, command=command_start_sync)
start_sync_button.place(x=start_x, y=sync_y, width=control_size, height=control_size)
stop_sync_button = tk.ttk.Button(root, command=command_stop_sync, state='disabled')
stop_sync_button.place(x=stop_x, y=sync_y, width=control_size, height=control_size)
send_stimulus_button = tk.ttk.Button(root, command=command_send_stimulus, state='disabled')
send_stimulus_button.place(x=start_x, y=stimulus_y, width=control_size, height=control_size)
stop_stimulus_button = tk.ttk.Button(root, command=command_stop_stimulus, state='disabled')
stop_stimulus_button.place(x=stop_x, y=stimulus_y, width=control_size, height=control_size)

### Addition of boxes to select parameters
parameter_boxes = []
for idx in range(n_parameter_types):
    current_parameter = parameter_types[idx]
    if 'location' in current_parameter:
        current_parameter = 'label'
    parameter_box = tk.ttk.Combobox(root, values=possible_stimulation_parameters[current_parameter], state='disabled')
    parameter_box.place(x=parameter_box_x, y=parameter_box_y[idx], width=parameter_box_width, height=parameter_box_height)
    parameter_box.set(possible_stimulation_parameters[current_parameter][0])
    parameter_box.bind('<<ComboboxSelected>>', lambda event, idx=idx:command_update_parameter(idx, parameter_types[idx], parameter_boxes[idx].current()))
    parameter_boxes.append(parameter_box)

### Addition of text box to enter notes and buttons to clear the text box and save note
note_entry_box = tk.Text(root)#, width=notes_width, height=notes_height)
note_entry_box.place(x=notes_x, y=notes_y, width=notes_width, height=notes_height)
clear_note_button = tk.ttk.Button(root, text='Clear', command=command_clear_text, state='disabled')
clear_note_button.place(x=enter_x - enter_width - 20, y=enter_y, width=enter_width, height=enter_height)
enter_note_button = tk.ttk.Button(root, text='Enter Note', command=command_enter_note, state='disabled')
enter_note_button.place(x=enter_x, y=enter_y, width=enter_width, height=enter_height)

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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((server_ip, server_port))
    message = message_dictionary['CONNECTED']
    print("Connected to server.")
    send_server_message(server, communications_file, message)
    receive_server_response(server, communications_file)
else:
    server = None

### Function that will start execution of GUI
root.mainloop()

############################################################################ Experiment End #############################################################################

### After the GUI finishes executing:
### Disconnect USB, send ending message to server, and close server.
CloseUSB()
if server_connection_enabled:
    message = message_dictionary['END']
    print("Closing server.")
    send_server_message(server, communications_file, message)
    server.close()