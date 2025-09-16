"""
Associative Recognition Experiment Subroutines

This code contains functions for experiment subroutines including
display of trials during study phase and collection of response in test phase.

"""
from smile.common import *
from smile.pennsyncbox import *
from smile.clock import clock
from configuration import *

############################################################## Experiment Subroutine and Function Definitions ###########################################################

### Function to trigger delivery of sync pulse from device and return the time when this is done    
def send_sync_pulse():
    SyncPulse()
    return clock.now()

### Function that sends Blackrock server message request to trigger server action
def send_server_request(server, request):
    request_uint32 = np.uint32(request)
    structured_request = struct.pack('@I', request_uint32)
    server.sendall(structured_request) 

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

### Subroutine to display word pairs and gather response regarding subdominant item in interaction
@Subroutine
def StudyPhase(self, study_phase):
    with Loop(study_phase) as trial:
        
        ### Send a sync pulse right before each sequence is started
        sync_pulse = Func(send_sync_pulse)

        ### Display crosshair for subject to orient view to center of screen
        orient_image = Image(source=crosshair_image, size=screen_size, duration=orient_duration, allow_stretch=True)
        
        ### Start of trial with gathering of response
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

        ### Use SMILE's log function to capture details of trial during intertrial interval
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
                test_stimulation_condition=trial.current['test_stimulation_condition'],
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
                subject=trial.current['subject'],
                session=trial.current['session'],
                experiment_block=trial.current['experiment_block'],
                experiment_phase=trial.current['experiment_phase'],
                trial_index=trial.current['trial_index'])

@Subroutine
def TestPhase(self, test_phase, server_connection_enabled, server):
    with Loop(test_phase) as trial:
        
        ### Send a sync pulse right before each sequence is started
        sync_pulse = Func(send_sync_pulse)

        ### Display crosshair for subject to orient view to center of screen
        orient_image = Image(source=crosshair_image, duration=orient_duration, size=screen_size, allow_stretch=True)
        
        ### Start of trial with gathering of response
        ### Simultaneously sends message to Blackrock computer server to trigger action for stimulation or sham conditions
        with Parallel():
            ### Request to Blackrock computer server
            with If(server_connection_enabled):
                with If(trial.current['test_stimulation_condition']):
                    Func(send_server_request, server, blackrock_messages['start_stimulation'])
                with Else():
                    Func(send_server_request, server, blackrock_messages['no_stimulation'])
            
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

        # Use SMILE's log function to capture details of trial during intertrial interval
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
                test_stimulation_condition=trial.current['test_stimulation_condition'],
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