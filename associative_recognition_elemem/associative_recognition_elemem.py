"""
Associative Recognition Experiment (Elemem Compatible)

This code runs a session of the experiment.

Make sure configurations for subject are located in
resources/subject_configurations/subject_folder.

For details about experiment structure view initialize_experiment.py
For details about experiment parameters view configuration.py

"""
from smile.common import *
from smile.pennsyncbox import *
from smile.math_distract import MathDistract
from smile.clock import clock
from smile.log import log2dl
import pandas as pd
import os
import socket
import json
import time
from csv import DictWriter

### Import configuration, initialization, and experiment functions
from configuration import *
from initialize_experiment import *
from experiment_utils import *
from get_experiment_session_data import *

##################################################################### Experiment initialization #########################################################################

experiment = Experiment(name=experiment_name)
date = experiment.session

### Make sure program was not executed in terminal with input argument for subject
### test000 is the default subject and files will initially be saved to a folder with this name
if 'test000' not in experiment.subject:
    print("Please run task without '-s' argument.")
    print(f"i.e. just 'python3 {experiment_name}.py' <Enter>.")
    quit()

### Start connection to server
### SMILE's server utility only allows sending but not receiving communication at runtime
if server_connection_enabled:
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((server_ip_address, server_port))
    except:
        print("Could not establish connection to server. Check connection and try again.")
        quit()
else:
    server = None

### Prompt subject and session information from user for easier file management
### and to enable starting a session from a completed checkpoint.

### Gather a valid subject code:
subject = prompt_subject_code()
        
### Gather a valid session number:
session = prompt_session_number()

### Define session directories and files
session_directory = data_directory + subject + '/session_'+ session + '/'
session_logs = session_directory + 'session_logs/'
experiment_block_list_file = session_directory + 'experiment_block_list.json'
checkpoint_file = session_directory + 'checkpoint.csv'
pulses_file = session_directory + 'pulses.csv'
events_file = session_directory + 'events.csv'
timing_file = session_directory + 'timing.csv'
communications_file = session_directory + 'communications.csv'
message_dictionary_file = session_directory + 'message_dictionary.json'
session_lock_file = session_directory + 'session_lock.txt'
smile_log_directory = test_directory + date + '/'
new_session_log = session_logs + date + '/'

### File dictionary for function transferring SMILE log data to .csv files
file_dictionary = {
    'pulse': (pulses_file, pulses_fieldnames),
    'event': (events_file, events_fieldnames),
    'timing': (timing_file, timing_fieldnames),
    'checkpoint': (checkpoint_file, checkpoint_fieldnames)
}

### Create list of trials if the experimental session had never been initialized
### Otherwise if session has been completed, quit.
if not os.path.isdir(session_directory):
    os.makedirs(session_directory)
    ### Gather a valid number of experiment blocks (0-6):
    n_experiment_blocks = prompt_n_experiment_blocks()
    initialize_experiment_func(subject, session, session_directory, n_experiment_blocks)
elif os.path.isfile(session_lock_file):
    print(f"Subject {subject} has already completed session {session}.")
    print("Please verify and run experiment again.")
    quit()

### Safeguards in case there was an error or files were deleted
if not os.path.isdir(session_logs):
    os.makedirs(session_logs)

if not os.path.isfile(experiment_block_list_file):
    n_experiment_blocks = prompt_n_experiment_blocks()
    initialize_experiment_func(subject, session, session_directory, n_experiment_blocks)        

if not os.path.isfile(checkpoint_file):
    pd.DataFrame(columns=checkpoint_fieldnames).to_csv(checkpoint_file, index=False, header=True)
    
if not os.path.isfile(pulses_file):
    pd.DataFrame(columns=pulses_fieldnames).to_csv(pulses_file, index=False, header=True)

if not os.path.isfile(events_file):
    pd.DataFrame(columns=events_fieldnames).to_csv(events_file, index=False, header=True)

if not os.path.isfile(timing_file):
    pd.DataFrame(columns=timing_fieldnames).to_csv(timing_file, index=False, header=True)

if not os.path.isfile(communications_file):
    pd.DataFrame(columns=communications_fieldnames).to_csv(communications_file, index=False, header=True)

### Allow time for files to be written before accessing
time.sleep(0.5)

### Retrieve experiment block list and message dictionaries from saved files
with open(experiment_block_list_file, 'r') as file_handle:
    experiment_block_list = json.load(file_handle)

with open(message_dictionary_file, 'r') as file_handle:
    message_dictionary = json.load(file_handle)

### If experimental session has been executed before gather information from checkpoint file
### to start from the appropriate trial
experiment_block_list, experiment.skip_study_phase = update_list_from_checkpoint(experiment_block_list, checkpoint_file, session_lock_file)

############################################################## Experiment Subroutine and Function Definitions ###########################################################
### TODO: Runtime error caused by handling of message variables. Already tried fully parameterizing functions and separating them in different files.
### Will still continue to error when handling 'WORD' type messages during test phase. No errors after commenting out this part.

############# Functions for communications between task client and Elemem server ##########

### Function to send messages to Elemem server and write communication to .csv
### During experiment runtime, messages can only be sent
def send_server_message(message):

    message['time'] = round(clock.now() * 1000)
    
    message_string = json.dumps(message) + '\n'
    
    if server_connection_enabled:
        server.send(message_string.encode('utf-8'))
    
    with open(communications_file, 'a', newline='') as file_handle:
        csv_writer = DictWriter(file_handle, fieldnames=communications_fieldnames)
        csv_writer.writerow(message)

### Function to receive messages from Elemem server and write communication to .csv
### Can only receive messages from server during experiment buildtime and after runtime
def receive_server_response():
    
    message_buffer = ''

    receiving_from_server = True
    while receiving_from_server:

        new_bytes = server.recv(1024)  ### Read up to 1024 bytes

        ### If no data is received, the connection has been closed or lost
        if not new_bytes:
            break
        
        ### Decode the data and add it to the buffer
        message_buffer += new_bytes.decode('utf-8')

        ### Process complete messages
        while '\n' in message_buffer:
            ### Split the buffer at the first newline
            message_string, message_buffer = message_buffer.split('\n', 1)

            ### Parse the JSON string into a dictionary
            message = json.loads(message_string)
                    
        ### If buffer is empty after processing the message, stop the loop
        if not message_buffer:
            receiving_from_server = False
    
    with open(communications_file, 'a', newline='') as file_handle:
        csv_writer = DictWriter(file_handle, fieldnames=communications_fieldnames)
        csv_writer.writerow(message)

### Initial communications with Elemem server
def initial_communications():
    global message_id, heartbeat_count
    ### CONNECTED message
    message_id += 1
    message = message_dictionary['CONNECTED'].copy()
    message['id'] = message_id
    send_server_message(message)
    if server_connection_enabled:
        receive_server_response()

    ### CONFIGURE message
    message_id += 1
    message = message_dictionary['CONFIGURE'].copy()
    message['id'] = message_id
    send_server_message(message)
    if server_connection_enabled:
        receive_server_response()

    ### READY message
    message_id += 1
    message = message_dictionary['READY'].copy()
    message['id'] = message_id
    send_server_message(message)
    if server_connection_enabled:
        receive_server_response()

    ### Series of 'HEARTBEAT' messages
    for _ in range(n_heartbeats):
        message_id += 1
        heartbeat_count += 1
        message = message_dictionary['HEARTBEAT'].copy()
        message['id'] = message_id
        message['data']['count'] = heartbeat_count
        send_server_message(message)
        if server_connection_enabled:
            receive_server_response()
        time.sleep(0.1)
    
### Final communications with Elemem server
def final_communications():
    global message_id, heartbeat_count
    ### Series of 'HEARTBEAT' messages
    for _ in range(n_heartbeats):
        message_id += 1
        heartbeat_count += 1
        message = message_dictionary['HEARTBEAT'].copy()
        message['id'] = message_id
        message['data']['count'] = heartbeat_count
        send_server_message(message)
        if server_connection_enabled:
            receive_server_response()
        time.sleep(0.1)
    
    ### EXIT message
    message_id += 1
    message = message_dictionary['EXIT'].copy()
    message['id'] = message_id
    send_server_message(message)

###################### Messages to Elemem Server #########################

### To indicate that experiment session has started
@Subroutine
def SessionMessage(self):
    experiment.message_id += 1
    message = message_dictionary['SESSION'].copy()
    message['id'] = experiment.message_id
    Func(send_server_message, message)

### To indicate that instructions are being displayed
@Subroutine
def InstructionsMessage(self):
    experiment.message_id += 1
    message = message_dictionary['INSTRUCT'].copy()
    message['id'] = experiment.message_id
    Func(send_server_message, message)

### To indicate time that crosshair to orient view to center is being displayed
@Subroutine
def OrientMessage(self):
    experiment.message_id += 1
    message = message_dictionary['ORIENT'].copy()
    message['id'] = experiment.message_id
    Func(send_server_message, message)

### To provide information about trial including start time, words displayed, and serial position
@Subroutine
def WordMessage(self, message):
    Func(send_server_message, message)

@Subroutine
def WordMessageTest(self, message):
    Func(send_server_message, message)

### To indicate the end time of a trial
@Subroutine
def TrialEndMessage(self):
    experiment.message_id += 1
    message = message_dictionary['TRIALEND'].copy()
    message['id'] = experiment.message_id
    Func(send_server_message, message) 

### To indicate the start time of math distraction trials
@Subroutine
def MathMessage(self):
    experiment.message_id += 1
    message = message_dictionary['MATH'].copy()
    message['id'] = experiment.message_id
    Func(send_server_message, message)

####################### Exeriment Subroutines ###########################

### Function to trigger delivery of sync pulse from device and return the time when this is done    
def send_sync_pulse():
    SyncPulse()
    return clock.now() 

### Subroutine to deliver a series of 10 pulses to assert they appear in EEG recording device
@Subroutine
def SyncPulseTest(self, subject, session):
    KeyPress()
    with Meanwhile():
        Label(text="PRESS ANY KEY TO START SYNC PULSE TEST", font_size=large_font)

    ### Series of 10 pulses spaced by a second
    with Parallel():
        Label(text="Check whether you see sync pulses on clinical EEG...", font_size=medium_font, blocking=False)
        with Loop(10):
            with Parallel():
                sync_pulse = Func(send_sync_pulse)
            Log(name='pulse',
                subject=subject,
                session=session,
                experiment_block='-1',
                experiment_phase='SYNC_PULSE_TEST',
                trial_index='-1',
                pulse_time=sync_pulse.result * 1000)
            Wait(duration=1)
    
    Wait(duration=1)
    
    with Parallel():
        label1 = Label(text="Did you see sync pulses on clinical EEG?", font_size=large_font)
        label2 = Label(text="If YES, press Y to continue.", font_size=medium_font, bottom=label1.bottom - label_offset)
        Label(text="If NO, exit the experiment and check the DC channels and sync set-up.", font_size=small_font, bottom=label2.bottom - label_offset)
    with UntilDone():
        KeyPress(keys='Y')

### Subroutine to display lab logo
@Subroutine
def DisplayLogo(self):  
    with Parallel():
        Image(source=lab_logo, duration=logo_duration)
        Label(text="Texas Computational Memory Lab", font_size=large_font, center_y=center_y + logo_offset, blocking=False)
        Label(text="UT Southwestern Medical Center", font_size=large_font, center_y=center_y - logo_offset, blocking=False)

### Subroutine to display text instructions
@Subroutine
def DisplayTextInstructions(self):
    with Parallel():
        ScrollView(do_scroll_x=False)
        RstDocument(text=instructions_text, size=screen_size, base_font_size=instructions_font_size, do_scroll_y=True)
    with UntilDone():
        KeyPress(keys=continue_key)

### Subroutine for looping through trials of study phase of an experiment block
@Subroutine
def StudyPhase(self, study_phase):
    
    with Loop(study_phase) as trial:
        
        ### Send a sync pulse right before each sequence is started
        sync_pulse = Func(send_sync_pulse)

        ### Display crosshair for subject to orient view to center of screen
        OrientMessage()
        orient_image = Image(source=crosshair_image, size=screen_size, duration=orient_duration, allow_stretch=True)

        ### Start of trial with gathering of response
        experiment.message_id += 1
        message = message_dictionary['WORD'].copy()
        message['id'] = experiment.message_id
        message['data']['word'] = trial.current['top_word'] + '/' + trial.current['bottom_word']
        message['data']['serialpos'] = trial.current['trial_index']
        WordMessage(message)

        with Parallel():
            ### Display of word pair
            top_word = Label(text=trial.current['top_word'], duration=allowed_response_time, font_size=large_font, bottom=top_word_y)
            Label(text=trial.current['bottom_word'], duration=allowed_response_time, font_size=large_font, top=bottom_word_y)
            
            ### Labels for appropriate key presses
            Label(text='T', duration=allowed_response_time, font_size=large_font, bottom=small_offset, center_x=T_reminder_x)
            Label(text='B', duration=allowed_response_time, font_size=large_font, bottom=small_offset, center_x=B_reminder_x)
            
            ### Gather response to trial
            trial_response = KeyPress(keys=[top_key, bottom_key], base_time=orient_image.appear_time['time'], blocking=False)
        
        time_to_respond = Ref(lambda t: -999 if t is None else (t - orient_duration) * 1000, trial_response.rt)

        TrialEndMessage()

        ### Send message to indicate end of trial while intertrial interval ellapses
        ### Use SMILE's log function to capture details of trial
        with Parallel():
            
            intertrial_blank = Image(source=blank_image, size=screen_size, duration=intertrial_interval, jitter=intertrial_jitter, allow_stretch=True)

            Log(name='pulse',
                subject=trial.current['subject'],
                session=trial.current['session'],
                experiment_block=trial.current['experiment_block'],
                experiment_phase=trial.current['experiment_phase'],
                trial_index=trial.current['trial_index'],
                pulse_time=sync_pulse.result * 1000)
            
            Log(name='event',
                subject=trial.current['subject'],
                session=trial.current['session'],
                experiment_block=trial.current['experiment_block'],
                experiment_phase=trial.current['experiment_phase'],
                trial_index=trial.current['trial_index'],
                top_word=trial.current['top_word'],
                bottom_word=trial.current['bottom_word'],
                study_answer=trial.current['study_answer'],
                test_condition=trial.current['test_condition'],
                study_response=trial_response.pressed,
                study_time_to_respond=time_to_respond,
                test_response='none',
                test_time_to_respond=-999,
                trial_time=top_word.appear_time['time'] * 1000)
            
            Log(name='timing',
                subject=trial.current['subject'],
                session=trial.current['session'],
                experiment_block=trial.current['experiment_block'],
                experiment_phase=trial.current['experiment_phase'],
                trial_index=trial.current['trial_index'],
                sync_time=sync_pulse.result * 1000,
                orient_time=orient_image.appear_time['time'] * 1000,
                trial_time=top_word.appear_time['time'] * 1000,
                time_to_respond=time_to_respond)
        
            Log(name='checkpoint',
                ssubject=trial.current['subject'],
                session=trial.current['session'],
                experiment_block=trial.current['experiment_block'],
                experiment_phase=trial.current['experiment_phase'],
                trial_index=trial.current['trial_index'])

### Subroutine for looping through trials of test phase of an experiment block
@Subroutine
def TestPhase(self, test_phase):
    with Loop(test_phase) as trial:
        
        ### Send a sync pulse right before each sequence is started
        sync_pulse = Func(send_sync_pulse)

        ### Display crosshair for subject to orient view to center of screen
        OrientMessage()
        orient_image = Image(source=crosshair_image, duration=orient_duration, size=screen_size, allow_stretch=True)

        ### Start of trial with gathering of response
        #experiment.message_id += 1
        #message = message_dictionary['WORD'].copy()
        #message['id'] = experiment.message_id
        #message['data']['word'] = trial.current['top_word'] + '/' + trial.current['bottom_word']
        #message['data']['serialpos'] = trial.current['trial_index']
        #WordMessageTest(message)

        with Parallel():
            ### Display of word pair
            top_word = Label(text=trial.current['top_word'], duration=allowed_response_time, font_size=large_font, bottom=top_word_y)
            Label(text=trial.current['bottom_word'], duration=allowed_response_time, font_size=large_font, top=bottom_word_y)
            
            ### Labels for appropriate key presses
            Label(text='N', duration=allowed_response_time, font_size=small_font, bottom=small_offset, center_x=N_reminder_x)
            Label(text='S', duration=allowed_response_time, font_size=small_font, bottom=small_offset, center_x=S_reminder_x)
            Label(text='R', duration=allowed_response_time, font_size=small_font, bottom=small_offset, center_x=R_reminder_x)
            
            ### Gather response to trial
            trial_response = KeyPress(keys=[new_key, same_key, rearranged_key], base_time=orient_image.appear_time['time'], blocking=False)
        
        time_to_respond = Ref(lambda t: -999 if t is None else (t - orient_duration) * 1000, trial_response.rt)
        
        ### Send message to indicate end of trial while intertrial interval ellapses
        ### Use SMILE's log function to capture details of trial
        TrialEndMessage()
        
        with Parallel():
            
            intertrial_blank = Image(source=blank_image, size=screen_size, duration=intertrial_interval, jitter=intertrial_jitter, allow_stretch=True)

            Log(name='pulse',
                subject=trial.current['subject'],
                session=trial.current['session'],
                experiment_block=trial.current['experiment_block'],
                experiment_phase=trial.current['experiment_phase'],
                trial_index=trial.current['trial_index'],
                pulse_time=sync_pulse.result * 1000)
            
            Log(name='event',
                subject=trial.current['subject'],
                session=trial.current['session'],
                experiment_block=trial.current['experiment_block'],
                experiment_phase=trial.current['experiment_phase'],
                trial_index=trial.current['trial_index'],
                top_word=trial.current['top_word'],
                bottom_word=trial.current['bottom_word'],
                study_answer=trial.current['study_answer'],
                test_condition=trial.current['test_condition'],
                study_response='none',
                study_time_to_respond=-999,
                test_response=trial_response.pressed,
                test_time_to_respond=time_to_respond,
                trial_time=top_word.appear_time['time'] * 1000)
            
            Log(name='timing',
                subject=trial.current['subject'],
                session=trial.current['session'],
                experiment_block=trial.current['experiment_block'],
                experiment_phase=trial.current['experiment_phase'],
                trial_index=trial.current['trial_index'],
                sync_time=sync_pulse.result * 1000,
                orient_time=orient_image.appear_time['time'] * 1000,
                trial_time=top_word.appear_time['time'] * 1000,
                time_to_respond=time_to_respond)
        
            Log(name='checkpoint',
                subject=trial.current['subject'],
                session=trial.current['session'],
                experiment_block=trial.current['experiment_block'],
                experiment_phase=trial.current['experiment_phase'],
                trial_index=trial.current['trial_index'])

####################################################################### Experiment Definition ###########################################################################

### Initial communications with Elemem Server
initial_communications()

experiment.message_id = message_id

### Keeping this this way: It was previously said that as of macOS10.15, 
### opening a U6 the first time after plugging it in sometimes fails,
### and that subsequent attempts to open succeed. These functions will connect
### task to pennsyncbox device.
CloseUSB()
OpenUSB()
CloseUSB()
OpenUSB()

SyncPulseTest(subject, session)

SessionMessage()
DisplayLogo()

InstructionsMessage()
DisplayTextInstructions()

with Loop(experiment_block_list) as experiment_block:

    ### Study phase, math distraction and, break before test phase
    with If(experiment.skip_study_phase):
        experiment.skip_study_phase = False
    with Else():
        ### Subject can start study phase when ready
        with Parallel():
            label1 = Label(text="Next up: Study Section " + experiment_block.current['experiment_block'], font_size=large_font)
            Label(text="Top or Bottom?", font_size=medium_font, bottom=label1.bottom - label_offset)
            Label(text=f"Press {continue_key} to start.", font_size=small_font, bottom=small_offset)
        with UntilDone():
            KeyPress(keys=continue_key)
        
        ### Start study phase
        StudyPhase(experiment_block.current['study_phase'])

        ### Small pause before start of math distraction
        Wait(1)
        experiment.message_id += 1
        MathMessage()
        MathDistract(duration=distraction_math_duration)
        
        ### Break of several minutes before test phase
        Label(text='Break', font_size=large_font, duration=distraction_break_duration)

    ### Subject can start test phase when ready
    with Parallel():
        label1 = Label(text="Next up: Test Section " + experiment_block.current['experiment_block'], font_size=large_font)
        Label(text="New, Same or Rearranged?", font_size=medium_font, bottom=label1.bottom - label_offset)
        Label(text=f"Press {continue_key} to start.", font_size=small_font, bottom=small_offset)
    with UntilDone():
        KeyPress(keys=continue_key)
    
    ### Start test phase
    TestPhase(experiment_block.current['test_phase'])
    Wait(1)

### If the execution of the experiment ends with no exits or power interruptions:
### USB port will be closed, a file locking the session will be created, and thank you note displayed
Func(CloseUSB)
Func(lock_session, session_lock_file)
Label(text="Thank you for participating!", font_size=large_font, duration=5)

#########################################################################################################################################################################
### Run the experiment
experiment.run()

### Final communications with Elemem server
message_id = experiment.get_var('message_id')
final_communications()

### Close server
if server_connection_enabled:
    server.close()

#################################################################### Post-Experiment Run Data Management ################################################################
### The lines below will run at experiment end or after exiting the experiment
### If there is a power interruption, then experiment data may need to be recovered 
### from SMILE logs with get_data.py using corresponding datetime used as folder name within /data/associative_recognition_elemem/test000

get_experiment_data_func(new_session_log, smile_log_directory, file_dictionary)