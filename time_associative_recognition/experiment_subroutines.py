"""
Timed Associative Recognition Experiment Subroutines

This code contains functions for experiment subroutines including
display of trials during study phase and collection of response in test phase.

"""

from smile.common import *
from smile.pennsyncbox import *
from smile.clock import clock
import random
from configuration import *

######################################################### Experiment Subroutine and Function Definitions ###############################################################

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
                trial_index=-1,
                pulse_time=sync_pulse.result * 1000)
            Wait(duration=1)
    
    Wait(duration=1)
    
    with Parallel():
        label1 = Label(text="Did you see sync pulses on clinical EEG?", font_size=large_font)
        label2 = Label(text="If YES, press Y to contine.", font_size=medium_font, bottom=label1.bottom - label_offset)
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

### Display instructions on screen that ends with any key press
@Subroutine
def DisplayInstructions(self):
    with Parallel():
        Image(source=instructions_image, size=instructions_size, top=top, allow_stretch = True)
        Label(text="Study the structure of each trial. Press any key to continue.", font_size=small_font, bottom=small_offset, blocking=False)   
    with UntilDone():
        KeyPress()

### Ask user whether there are any questions about instructions before starting experiment
@Subroutine
def InstructionsQuestions(self):
    with Parallel():
        label1 = Label(text="If you have any questions about the task,\nplease ask the researcher now.", font_size=large_font)
        Label(text="Press any key to start the task.", font_size=small_font, bottom=small_offset)
    with UntilDone():
        KeyPress()  

### Function to display sequences (crosshair -> emoji -> blank time interval -> celebrity face) 
### followed by keypress choice of whether emoji is organic or inorganic
@Subroutine
def StudyPhase(self, study_phase, session_keys_dictionary):

    study_left_label = session_keys_dictionary['study_left_label']
    study_right_label = session_keys_dictionary['study_right_label']

    with Loop(study_phase) as sequence:
        
        ### Send a sync pulse right before each sequence is started
        sync_pulse = Func(send_sync_pulse)
        
        ### Display crosshair for subject to orient view to center of screen
        orient_image = Image(source=crosshair_image, size=screen_size, duration=orient_duration, allow_stretch=True)
        
        ### Display trial's corresponding item emoji
        item_source = emoji_directory + sequence.current['item'] + '.jpg'
        item_image = Image(source=item_source, size=screen_size, duration=image_duration, allow_stretch=True)
        
        ### Display blank image for time interval corresponding to trial
        interval_image = Image(source=blank_image, size=screen_size, duration=sequence.current['interval'], allow_stretch=True)
        
        ### Display face of trial's corresponding celebrity
        face_source = face_directory + sequence.current['celebrity_face'] + '.jpg'
        face_image = Image(source=face_source, duration=image_duration, size=screen_size, allow_stretch=True)
        
        ### Standard pause after completion of each sequence prior to question
        preresponse_image = Image(source=blank_image, size=screen_size, duration=preresponse_pause, allow_stretch=True)
        
        ### Indication for user to press left or right key to answer question about item emoji (organic vs inorganic)
        with Parallel():
            Image(source=screen_divider, size=screen_size, duration=allowed_response_time, allow_stretch=True)
            item_question = Label(text='ITEM', font_size=large_font, top=top - label_offset, duration=allowed_response_time)
            Label(text=study_left_label, font_size=large_font, center_x=left_x, duration=allowed_response_time)
            Label(text=study_right_label, font_size=large_font, center_x=right_x, duration=allowed_response_time)
            item_response = KeyPress(keys=[left_key, right_key], base_time=preresponse_image.appear_time['time'], blocking=False)
        item_time_to_respond = Ref(lambda t: -999 if t is None else (t - preresponse_pause) * 1000, item_response.rt)

        ### Use SMILE's log function to capture details of trial during intertrial interval
        with Parallel():
            intertrial_blank = Image(source=blank_image, size=screen_size, duration=intertrial_interval, jitter=intertrial_jitter, allow_stretch=True)
        
            Log(name='pulse',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                trial_index=sequence.current['trial_index'],
                pulse_time=sync_pulse.result * 1000)
            
            Log(name='event',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                trial_index=sequence.current['trial_index'],
                item=sequence.current['item'],
                item_category=sequence.current['item_category'],
                celebrity_face=sequence.current['celebrity_face'],
                celebrity_gender=sequence.current['celebrity_gender'],
                interval=sequence.current['interval'],
                interval_type=sequence.current['interval_type'],
                test_condition=sequence.current['test_condition'],
                item_response=item_response.pressed,
                item_time_to_respond=item_time_to_respond,
                face_response='none',
                face_time_to_respond = -999,
                interval_response='none',
                interval_time_to_respond=-999,
                trial_time=item_image.appear_time['time'] * 1000)
            
            Log(name='timing',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                trial_index=sequence.current['trial_index'],
                sync_time=sync_pulse.result * 1000,
                orient_time=orient_image.appear_time['time'] * 1000,
                trial_time=item_image.appear_time['time'] * 1000,
                item_time=item_image.appear_time['time'] * 1000,
                interval_time=interval_image.appear_time['time'] * 1000,
                interval=sequence.current['interval'] * 1000,
                face_time=face_image.appear_time['time'] * 1000,
                item_question_time=item_question.appear_time['time'] * 1000,
                item_time_to_respond=item_time_to_respond,
                face_question_time=-999,
                face_time_to_respond=-999,
                interval_question_time=-999,
                interval_time_to_respond=-999)
            
            Log(name='checkpoint',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                trial_index=sequence.current['trial_index'])

### Additional experiment of temporal memory in which a fraction of inter-phase (study-test) intervals are deviant        
@Subroutine
def DelayPeriod(self, experiment_block):
    
    self.lucky_number = random.randint(1, 100)
    
    with If(self.lucky_number <= p_standard_delay * 100):
        self.delay_duration = standard_delay
    with Else():
        self.delay_duration = deviant_delay
    
    delay_image = Image(source=blank_image, size=screen_size, duration=self.delay_duration)
    
    Log(name='delay',
        subject=experiment_block['subject'],
        session=experiment_block['session'],
        experiment_block=experiment_block['experiment_block'],
        delay_time=delay_image.appear_time['time'] * 1000,
        delay_duration=self.delay_duration * 1000)      

### Function to display sequences during the test phase followed by two questions,
### whether the celebrity face associated to emoji has changed,
### whether the time interval between them has changed
@Subroutine
def TestPhase(self, test_phase, session_keys_dictionary):
    
    test_left_label = session_keys_dictionary['test_left_label']
    test_right_label = session_keys_dictionary['test_right_label']

    with Loop(test_phase) as sequence:
        
        ### Send a sync pulse right before each sequence is started
        sync_pulse = Func(send_sync_pulse)
        
        ### Display crosshair for subject to orient view to center of screen
        orient_image = Image(source=crosshair_image, size=screen_size, duration=orient_duration, allow_stretch=True)
        
        ### Display trial's corresponding item emoji
        item_source = emoji_directory + sequence.current['item'] + '.jpg'
        item_image = Image(source=item_source, size=screen_size, duration=image_duration, allow_stretch=True)
        
        ### Display blank image for time interval corresponding to trial
        interval_image = Image(source=blank_image, size=screen_size, duration=sequence.current['interval'], allow_stretch=True)

        ### Display face of trial's corresponding celebrity
        face_source = face_directory + sequence.current['celebrity_face'] + '.jpg'
        face_image = Image(source=face_source, size=screen_size, duration=image_duration, allow_stretch=True)
        
        ### Standard pause after completion of each sequence prior to question
        preresponse_image1 = Image(source=blank_image, size=screen_size, duration=preresponse_pause, allow_stretch=True)
        
        ### Indication for user to press left or right to answer question regarding whether celebrity face associated to item has changed
        with Parallel():
            Image(source=screen_divider, size=screen_size, duration=allowed_response_time, allow_stretch=True)
            face_question = Label(text='FACE', font_size=large_font, top=top - label_offset, duration=allowed_response_time)
            Label(text=test_left_label, font_size=large_font, center_x=left_x, duration=allowed_response_time)
            Label(text=test_right_label, font_size=large_font, center_x=right_x, duration=allowed_response_time)
            face_response = KeyPress(keys=[left_key, right_key], base_time=preresponse_image1.appear_time['time'], blocking=False)
        face_time_to_respond = Ref(lambda t: -999 if t is None else (t - preresponse_pause) * 1000, face_response.rt)
            
        preresponse_image2 = Image(source=blank_image, size=screen_size, duration=preresponse_pause, allow_stretch=True)
        
        ### Indication for user to press left or right to answer question regarding whether time interval after item has changed
        with Parallel():
            Image(source=screen_divider, size=screen_size, duration=allowed_response_time, allow_stretch=True)
            interval_question = Label(text='TIME INTERVAL', font_size=large_font, top=top - label_offset, duration=allowed_response_time)
            Label(text=test_left_label, font_size=large_font, center_x=left_x, duration=allowed_response_time)
            Label(text=test_right_label, font_size=large_font, center_x=right_x, duration=allowed_response_time)
            interval_response = KeyPress(keys=[left_key, right_key], base_time=preresponse_image2.appear_time['time'], blocking=False)
        interval_time_to_respond = Ref(lambda t: -999 if t is None else (t - preresponse_pause) * 1000, interval_response.rt)

        ### Use SMILE's log function to capture details of trial during intertrial interval
        with Parallel():
            intertrial_blank = Image(source=blank_image, size=screen_size, duration=intertrial_interval, jitter=intertrial_jitter)
        
            Log(name='pulse',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                trial_index=sequence.current['trial_index'],
                pulse_time=sync_pulse.result * 1000)

            Log(name='event',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                trial_index=sequence.current['trial_index'],
                item=sequence.current['item'],
                item_category=sequence.current['item_category'],
                celebrity_face=sequence.current['celebrity_face'],
                celebrity_gender=sequence.current['celebrity_gender'],
                interval=sequence.current['interval'] * 1000,
                interval_type=sequence.current['interval_type'],
                test_condition=sequence.current['test_condition'],
                item_response='none',
                item_time_to_respond=-999,
                face_response=face_response.pressed,
                face_time_to_respond=face_time_to_respond,
                interval_response=interval_response.pressed,
                interval_time_to_respond=interval_time_to_respond,
                trial_time=item_image.appear_time['time'] * 1000)
        
            Log(name='timing',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                trial_index=sequence.current['trial_index'],
                sync_time=sync_pulse.result * 1000,
                orient_time=orient_image.appear_time['time'] * 1000,
                trial_time=item_image.appear_time['time'] * 1000,
                item_time=item_image.appear_time['time'] * 1000,
                interval_time=interval_image.appear_time['time'] * 1000,
                interval=sequence.current['interval'] * 1000,
                face_time=face_image.appear_time['time'] * 1000,
                item_question_time=-999,
                item_time_to_respond=-999,
                face_question_time=face_question.appear_time['time'] * 1000,
                face_time_to_respond=face_time_to_respond,
                interval_question_time=interval_question.appear_time['time'] * 1000,
                interval_time_to_respond=interval_time_to_respond)
        
            Log(name='checkpoint',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                trial_index=sequence.current['trial_index'])