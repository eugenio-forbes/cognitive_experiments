"""
Message Dictionary for Associative Recognition Elemem

This document contains a series of dictionaries used in server-client communication,
holding information about experiment events and stimulation configurations.
Initialized when running an experiment.

"""
from configuration import *

def get_message_dictionary(subject, session):

    ############################ Message dictionaries ################################
    
    # Definition of dictionaries that are sent as JSON format string messages
    # to University of Pennsylvania's RAM project "Elemem" server for recording
    # signal from Blackrock Neurotech and open-loop and closed-loop stimulation
    
    CCLSTARTSTIM_message = {
        'type': 'CCLSTARTSTIM',
        'data': {'duration_s': cps_duration_s},
        'id': message_id,
        'time': message_time}

    CLNORMALIZE_message = {
        'type': 'CLNORMALIZE',
        'data': {'classifyms': classification_duration_ms},
        'id': message_id,
        'time': message_time}

    CLSHAM_message = {
        'type': 'CLSHAM',
        'data': {'classifyms': classification_duration_ms},
        'id': message_id,
        'time': message_time}

    CLSTIM_message = {
        'type': 'CLSTIM',
        'data': {'classifyms': classification_duration_ms},
        'id': message_id,
        'time': message_time}

    CONFIGURE_message = {
        'type': 'CONFIGURE',
        'data': {
            'stim_mode': stimulation_mode, 
            'experiment': experiment_name, 
            'subject': subject, 
            'tags': data_entry_tags},
        'id': message_id,
        'time': message_time}

    CONNECTED_message = {
        'type': 'CONNECTED',
        'data': {},
        'id': message_id,
        'time': message_time}

    COUNTDOWN_message = {
        'type': 'COUNTDOWN',
        'data': {},
        'id': message_id,
        'time': message_time}

    DISTRACT_message = {
        'type': 'DISTRACT',
        'data': {},
        'id': message_id,
        'time': message_time}

    EXIT_message = {
        'type': 'EXIT',
        'data': {},
        'id': message_id,
        'time': message_time}

    HEARTBEAT_message = {
        'type': 'HEARTBEAT',
        'data': {'count': heartbeat_count},
        'id': message_id,
        'time': message_time}

    INSTRUCT_message = {
        'type': 'INSTRUCT',
        'data': {},
        'id': message_id,
        'time': message_time}

    MATH_message = {
        'type': 'MATH',
        'data': {
            'problem': math_problem,
            'response': math_response,
            'response_time_ms': math_rt_ms,
            'correct': math_correct},
        'id': message_id,
        'time': message_time}

    ORIENT_message = {
        'type': 'ORIENT',
        'data': {},
        'id': message_id,
        'time': message_time}
    
    READY_message = {
        'type': 'READY',
        'data': {},
        'id': message_id,
        'time': message_time}
    
    RECALL_message = {
        'type': 'RECALL',
        'data': {'duration': recall_duration},
        'id': message_id,
        'time': message_time}
    
    REST_message = {
        'type': 'REST',
        'data': {},
        'id': message_id,
        'time': message_time}
    
    SESSION_message = {
        'type': 'SESSION',
        'data': {'session': int(session)},
        'id': message_id,
        'time': message_time}
    
    STIM_message = {
        'type': 'STIM',
        'data': {},
        'id': message_id,
        'time': message_time}
    
    STIMSELECT_message = {
        'type': 'STIMSELECT',
        'data': {'stimtag': stimulation_tag},
        'id': message_id,
        'time': message_time}
    
    TRIAL_message = {
        'type': 'TRIAL',
        'data': {
            'trial': trial_number,
            'stim': stimulation_bool},
        'id': message_id,
        'time': message_time}
    
    TRIALEND_message = {
        'type': 'TRIALEND',
        'data': {},
        'id': message_id,
        'time': message_time}
    
    WORD_message = {
        'type': 'WORD',
        'data': {
            'word': word_pair,
            'serialpos': serial_position,
            'stim': stimulation_bool}, 
        'id': message_id,
        'time': message_time}
    
    message_dictionary = {
        'CCLSTARTSTIM': CCLSTARTSTIM_message,
        'CLNORMALIZE': CLNORMALIZE_message,
        'CLSHAM': CLSHAM_message,
        'CLSTIM': CLSTIM_message,
        'CONFIGURE': CONFIGURE_message,
        'CONNECTED': CONNECTED_message,
        'COUNTDOWN': COUNTDOWN_message,
        'DISTRACT': DISTRACT_message,
        'EXIT': EXIT_message,
        'HEARTBEAT': HEARTBEAT_message,
        'INSTRUCT': INSTRUCT_message,
        'MATH': MATH_message,
        'ORIENT': ORIENT_message,
        'READY': READY_message,
        'RECALL': RECALL_message,
        'REST': REST_message,
        'SESSION': SESSION_message,
        'STIM': STIM_message,
        'STIMSELECT': STIMSELECT_message,
        'TRIAL': TRIAL_message,
        'TRIALEND': TRIALEND_message,
        'WORD': WORD_message}
    
    return message_dictionary