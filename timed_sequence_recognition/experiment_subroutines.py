"""
Timed Sequence Recognition Experiment Subroutines

This code contains functions for experiment subroutines including:
display of trials during study phase and collection of response in test phase

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
                sequence_index=-1,
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

### Subroutines to display text and visual representations of instructions
@Subroutine
def DisplayTextInstructions(self):
    Label(text=instructions_text, font_size=instructions_font_size)
    with UntilDone():
        KeyPress()

@Subroutine
def DisplayInstructionsImage1(self):
    with Parallel():
        Image(source=instructions_image1, width=screen_width * 0.9, height=screen_height * 0.9, top=top, allow_stretch=True)
        Label(text="Study the structure of each trial. Press any key to continue.", font_size=small_font, bottom=small_offset, blocking=False)   
    with UntilDone():
        KeyPress()

@Subroutine
def DisplayInstructionsImage2(self):
    with Parallel():
        Image(source=instructions_image2, width=screen_width * 0.9, height=screen_height * 0.9, top=top, allow_stretch=True)
        Label(text="Press ENTER to continue. Press B to go back.", font_size=small_font, bottom=small_offset, blocking=False)  
    with UntilDone():
        self.kp = KeyPress(keys=['B', 'ENTER'])


### Ask user whether there are any questions about instructions before starting experiment
@Subroutine
def InstructionsQuestions(self):
    with Parallel():
        label1 = Label(text="If you have any questions about the task,\nplease ask the researcher now.", font_size=large_font)
        Label(text="Press any key to start the task.", font_size=small_font, bottom=small_offset)
    with UntilDone():
        KeyPress()  

### Subroutine to display study phase sequences (crosshair -> emoji -> celebrity face 1 -> blank time interval -> celebrity face 2) 
### followed by intersequence interval blank
@Subroutine
def StudyPhase(self, study_phase):
    with Loop(study_phase) as sequence:
        
        ### Send a sync pulse right before each sequence is started
        sync_pulse = Func(send_sync_pulse)
        
        ### Display crosshair for subject to orient view to center of screen
        orient_image = Image(source=crosshair_image, size=screen_size, duration=orient_duration, allow_stretch=True)
        
        ### Display sequence's corresponding emoji
        emoji_source = emoji_directory + sequence.current['emoji'] + '.jpg'
        emoji_image = Image(source=emoji_source, size=screen_size, duration=image_duration, allow_stretch=True)
        
        ### Display face of sequence's first corresponding celebrity
        face1_source = face_directory + sequence.current['face1'] + '.jpg'
        face1_image = Image(source=face1_source, size=screen_size, duration=image_duration, allow_stretch=True)

        ### Display blank image for time interval corresponding to sequence
        interval_image = Image(source=blank_image, size=screen_size, duration=sequence.current['interval'], allow_stretch=True)
        
        ### Display face of sequence's second corresponding celebrity
        face2_source = face_directory + sequence.current['face2'] + '.jpg'
        face2_image = Image(source=face2_source, size=screen_size, duration=image_duration, allow_stretch=True)

        ### Use SMILE's log function to capture details of sequence during intersequence interval
        with Parallel():
            intersequence_blank = Image(source=blank_image, size=screen_size, duration=intersequence_interval, jitter=intersequence_jitter, allow_stretch=True)
        
            Log(name='pulse',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                sequence_index=sequence.current['sequence_index'],
                pulse_time=sync_pulse.result * 1000)
            
            Log(name='event',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                sequence_index=sequence.current['sequence_index'],
                sequence_group=sequence.current['sequence_group'],
                interval_type=sequence.current['interval_type'],
                emoji=sequence.current['emoji'],
                face1=sequence.current['face1'],
                interval=sequence.current['interval'] * 1000,
                face2=sequence.current['face2'],
                response='none',
                correct_response='none',
                time_to_respond=-999,
                trial_time=emoji_image.appear_time['time'] * 1000)
            
            Log(name='timing',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                sequence_index=sequence.current['sequence_index'],
                sequence_group=sequence.current['sequence_group'],
                interval_type=sequence.current['interval_type'],
                sync_time=sync_pulse.result * 1000,
                orient_time=orient_image.appear_time['time'] * 1000,
                trial_time=emoji_image.appear_time['time'] * 1000,
                emoji_time=emoji_image.appear_time['time'] * 1000,
                face1_time=face1_image.appear_time['time'] * 1000,
                interval_time=interval_image.appear_time['time'] * 1000,
                interval=sequence.current['interval'] * 1000,
                face2_time=face2_image.appear_time['time'] * 1000,
                question_time=-999,
                time_to_respond=-999)
            
            Log(name='checkpoint',
                subject=sequence.current['subject'],
                session=sequence.current['session'],
                experiment_block=sequence.current['experiment_block'],
                experiment_phase=sequence.current['experiment_phase'],
                sequence_index=sequence.current['sequence_index'])

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

### Function to display test phase sequence followed by choice of associated emoji
@Subroutine
def TestPhase(self, test_phase):
        
    ### Send a sync pulse right before each sequence is started
    sync_pulse = Func(send_sync_pulse)
        
    ### Display crosshair for subject to orient view to center of screen
    orient_image = Image(source=crosshair_image, size=screen_size, duration=orient_duration, allow_stretch=True)
        
    ### Display test sign instead of emoji
    test_image = Image(source=test_sign_image, size=screen_size, duration=image_duration, allow_stretch=True)

    ### Display face of test sequence's first corresponding celebrity
    face1_source = face_directory + test_phase['sequence']['face1'] + '.jpg'
    face1_image = Image(source=face1_source, size=screen_size, duration=image_duration, allow_stretch=True)

    ### Display blank image for time interval corresponding to test sequence
    interval_image = Image(source=blank_image, size=screen_size, duration=test_phase['sequence']['interval'], allow_stretch=True)
        
    ### Display face of sequence's second corresponding celebrity
    face2_source = face_directory + test_phase['sequence']['face2'] + '.jpg'
    face2_image = Image(source=face2_source, size=screen_size, duration=image_duration, allow_stretch=True)
        
    ### Standard pause after completion of test sequence prior to question
    preresponse_blank = Image(source=blank_image, size=screen_size, duration=preresponse_pause)
        
    ### Screen for selection of test response
    with ButtonPress(correct_resp=test_phase['correct_response']) as test_response:    

        ### Define sources of emoji images placed on button locations
        top_left_emoji = emoji_directory + test_phase['emojis'][0] + '.jpg'
        top_right_emoji = emoji_directory + test_phase['emojis'][1] + '.jpg'
        bottom_left_emoji = emoji_directory + test_phase['emojis'][2] + '.jpg'
        bottom_right_emoji = emoji_directory + test_phase['emojis'][3] + '.jpg'
        
        ### Required to show the mouse on the screen during the experiment!
        MouseCursor()
        test_question = Label(text="Which emoji identifies the test sequence last shown?", font_size=medium_font, top=top-label_offset)
        
        ### Give names to bottons corresponding to position and response
        Button(name='top_left', size=button_size, center=top_left_position)
        Image(source=top_left_emoji, size=button_size, center=top_left_position)

        Button(name='top_right', size=button_size, center=top_right_position)
        Image(source=top_right_emoji, size=button_size, center=top_right_position)

        Button(name='bottom_left', size=button_size, center=bottom_left_position)
        Image(source=bottom_left_emoji, size=button_size, center=bottom_left_position)

        Button(name='bottom_right', size=button_size, center=bottom_right_position)
        Image(source=bottom_right_emoji, size=button_size, center=bottom_right_position)
    
    ### Use SMILE's log function to capture details of trial during intertrial interval
    with Parallel():
        intertrial_blank = Image(source=blank_image, size=screen_size, duration=intertrial_interval, jitter=intertrial_jitter)

        Log(name='pulse',
            subject=test_phase['subject'],
            session=test_phase['session'],
            experiment_block=test_phase['experiment_block'],
            experiment_phase=test_phase['experiment_phase'],
            sequence_index=test_phase['sequence']['sequence_index'],
            pulse_time=sync_pulse.result * 1000)
            
        Log(name='event',
            subject=test_phase['subject'],
            session=test_phase['session'],
            experiment_block=test_phase['experiment_block'],
            experiment_phase=test_phase['experiment_phase'],
            sequence_index=test_phase['sequence']['sequence_index'],
            sequence_group=test_phase['sequence']['sequence_group'],
            interval_type=test_phase['sequence']['interval_type'],
            emoji=test_phase['sequence']['emoji'],
            face1=test_phase['sequence']['face1'],
            interval=test_phase['sequence']['interval'] * 1000,
            face2=test_phase['sequence']['face2'],
            response=test_response.pressed,
            correct_response=test_phase['correct_response'],
            time_to_respond=test_response.rt * 1000,
            trial_time=test_image.appear_time['time'] * 1000)
            
        Log(name='timing',
            subject=test_phase['subject'],
            session=test_phase['session'],
            experiment_block=test_phase['experiment_block'],
            experiment_phase=test_phase['experiment_phase'],
            sequence_index=test_phase['sequence']['sequence_index'],
            sequence_group=test_phase['sequence']['sequence_group'],
            interval_type=test_phase['sequence']['interval_type'],
            sync_time=sync_pulse.result * 1000,
            orient_time=orient_image.appear_time['time'] * 1000,
            trial_time=test_image.appear_time['time'] * 1000,
            emoji_time=test_image.appear_time['time'] * 1000,
            face1_time=face1_image.appear_time['time'] * 1000,
            interval_time=interval_image.appear_time['time'] * 1000,
            interval=test_phase['sequence']['interval'] * 1000,
            face2_time=face2_image.appear_time['time'] * 1000,
            question_time=test_question.appear_time['time'] * 1000,
            time_to_respond=test_response.rt * 1000)

        Log(name='checkpoint',
            subject=test_phase['subject'],
            session=test_phase['session'],
            experiment_block=test_phase['experiment_block'],
            experiment_phase=test_phase['experiment_phase'],
            sequence_index=test_phase['sequence']['sequence_index'])