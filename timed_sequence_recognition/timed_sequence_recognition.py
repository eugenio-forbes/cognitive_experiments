"""
Timed Sequence Recognition Experiment

This code runs a session of the experiment.
For details about experiment structure view initialize_experiment.py
For details about experiment parameters view configuration.py

"""

from smile.common import *
from smile.pennsyncbox import *
import pandas as pd
import os
import json
import time

### Import configuration, initialization, and experiment functions
from configuration import *
from initialize_experiment import *
from experiment_utils import *
from experiment_subroutines import *
from get_experiment_session_data import *

############################################################### Experiment initialization #############################################################################

experiment = Experiment(name=experiment_name)
date = experiment.session

### Make sure program was not executed in terminal with input argument for subject
if 'test000' not in experiment.subject:
    print("Please run task without '-s' argument.")
    print(f"i.e. just 'python3 {experiment_name}.py' <Enter>.")
    quit()

### Prompt subject and session information from user for easier file management
### and to enable starting a session from a completed checkpoint.

### Gather a valid subject code:
subject = prompt_subject_code()
        
### Gather a valid session number:
session = prompt_session_number()

### Define session directories and files
session_directory = data_directory + subject + '/session_'+ session + '/'
experiment_block_list_file = session_directory + 'experiment_block_list.json'
session_logs = session_directory + 'session_logs/'
checkpoint_file = session_directory + 'checkpoint.csv'
pulses_file = session_directory + 'pulses.csv'
events_file = session_directory + 'events.csv'
timing_file = session_directory + 'timing.csv'
delays_file = session_directory + 'delays.csv'
session_lock_file = session_directory + 'session_lock.txt'
smile_log_directory = test_directory + date + '/'
new_session_log = session_logs + date + '/'

### File dictionary for function transferring SMILE log data to .csv files
file_dictionary = {
    'pulse': (pulses_file, pulses_fieldnames),
    'event': (events_file, events_fieldnames),
    'timing': (timing_file, timing_fieldnames),
    'checkpoint': (checkpoint_file, checkpoint_fieldnames),
    'delay': (delays_file, delays_fieldnames)
}

### Create list of experiment_blocks if the experimental session had never been initialized
if not os.path.isdir(session_directory):
    os.makedirs(session_directory)
    os.makedirs(session_logs)
    ### Gather a valid number of trials (1-45) to be performed in this session
    n_experiment_blocks = prompt_n_experiment_blocks()
    initialize_experiment_func(subject, session, session_directory, n_experiment_blocks)

### If the experimental session has been already completed, 
### this will be indicated by existence of a lock file
if os.path.isfile(session_lock_file):
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

if not os.path.isfile(delays_file):
    pd.DataFrame(columns=delays_fieldnames).to_csv(delays_file, index=False, header=True)

### Allow some time for written files to be saved before accessing
time.sleep(0.5)

### Retrieve experiment block list from saved file
with open(experiment_block_list_file) as file_handle:
    experiment_block_list = json.load(file_handle)

### If experimental session has been executed before gather information 
### from checkpoint file to start from the appropriate trial
experiment_block_list, experiment.skip_study_phase = update_list_from_checkpoint(experiment_block_list, checkpoint_file, session_lock_file)

################################################################### Experiment Loop Definition #########################################################################

### Keeping this this way: It was previously said that as of macOS10.15, 
### opening a U6 the first time after plugging it in sometimes fails,
### and that subsequent attempts to open succeed. These functions will connect
### task to pennsyncbox device.
Func(CloseUSB)
Func(OpenUSB)
Func(CloseUSB)
Func(OpenUSB)

SyncPulseTest(subject, session)
DisplayLogo()
DisplayTextInstructions()

experiment.continue_instructions = True
with Loop(conditional=experiment.continue_instructions):
    DisplayInstructionsImage1()
    experiment.push = DisplayInstructionsImage2()
    experiment.continue_instructions = experiment.push.kp.pressed == 'B'         

InstructionsQuestions()

with Loop(experiment_block_list) as experiment_block:
    ### If subject did not complete a block's test phase, study phase and suceding delay phase will be skipped once
    with If(experiment.skip_study_phase):
        experiment.skip_study_phase = False
    with Else():
        ### Start study phase
        with Parallel():
            Label(text="Next up: Study Section " + experiment_block.current['experiment_block'], font_size=large_font)
            Label(text=f"Press {continue_key} to start.", font_size=small_font, bottom=small_offset)
        with UntilDone():
            KeyPress(keys=continue_key)
        
        StudyPhase(experiment_block.current['study_phase'])

        ### Experimental delay period between study phase and test phase
        DelayPeriod(experiment_block.current)
        
        ### Subject may start test phase when ready after delay period
        Label(text=f"Press {continue_key} to continue.", font_size=small_font, bottom=small_offset)
        with UntilDone():
            KeyPress(keys=continue_key)
    
    ### Start test phase
    with Parallel():
        Label(text="Next up: Test Section " + experiment_block.current['experiment_block'], font_size=large_font)
        Label(text=f"Press {continue_key} to start.", font_size=small_font, bottom=small_offset)
    with UntilDone():
        KeyPress(keys=continue_key)
    TestPhase(experiment_block.current['test_phase'])

### If the execution of the experiment ends with no exits or power interruptions:
### USB port will be closed, a file locking the session will be created, and thank you note displayed
Func(CloseUSB)
Func(lock_session, session_lock_file)
Label(text="Thank you for participating!", font_size=large_font, duration=5)

########################################################################################################################################################################

# Run the experiment
experiment.run()

################################################################## Post-Experiment Run Data Management #################################################################
### The line below will run at experiment end or after exiting the experiment
### If there is a power interruption, then experiment data may need to be recovered 
### from SMILE logs with get_data.py using corresponding datetime used as folder name within /data/time_associative_recognition/test000

get_experiment_data_func(new_session_log, smile_log_directory, file_dictionary)