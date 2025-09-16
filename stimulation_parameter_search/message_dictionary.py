"""
Message Dictionary for Stimulation Parameter Search Experiment

This document contains a series of dictionaries used in server-client communication,
holding information about experiment events and stimulation configurations.
Initialized when running an experiment.

"""

def get_message_dictionary(subject, session, stimulation_parameters=None):

    ############################ Message dictionaries ################################
    
    ### Dictionaries below will be used in communications with server
    
    ### Template of the general structure of a message
    template_dictionary = {
        'subject': subject,
        'session': session,
        'message_type': '',
        'data': {'n_fields': 0},
        'sender': 'client',
        'server_time': 0,
        'client_time': 0,
        'message_id': 0
    }

    ### Initial communication with server upon connection
    CONNECTED_message = template_dictionary.copy()
    CONNECTED_message['message_type'] = 'CONNECTED'

    ### Parameters for a specific stimulation trial for server to deliver upon receipt
    STIMULATION_CONFIGURATION_message = template_dictionary.copy()
    STIMULATION_CONFIGURATION_data = {
        'n_fields': 7,
        'label': '',
        'anode': 0,
        'cathode': 0,
        'amplitude': 0,
        'frequency': 0,
        'pulse_width': 0,
        'duration': 0
    }
    STIMULATION_CONFIGURATION_message['message_type'] = 'STIMULATION_CONFIGURATION'
    STIMULATION_CONFIGURATION_message['data'] = STIMULATION_CONFIGURATION_data
    
    ### Signal for server to stop current delivery of a stimulus
    STOP_STIMULATION_message = template_dictionary.copy()
    STOP_STIMULATION_message['message_type'] = 'STOP_STIMULATION'

    ### Indicating to server that trial is sham (will only print message in console)
    ### If stimulatiton is not enabled, message type will be switched to 'SYNCPULSE'
    ### and will be sent intermittently to server to avoid timeout.
    ### Done this way to avoid conflicts between asynchronous threads.
    SHAM_message = template_dictionary.copy()
    SHAM_message['message_type'] = 'SHAM'

    ### Indicating to server that experiment has ended
    END_message = template_dictionary.copy()
    END_message['message_type'] = 'END'

    ### Dictionaries below for data entry throughout execution of experiment

    ### For all events taking place (stimulation configured, sham trial)
    EVENT_dict = {
        'subject': subject,
        'session': session,
        'label': '',
        'anode': 0,
        'cathode': 0,
        'amplitude': 0,
        'frequency': 0,
        'pulse_width': 0,
        'duration': 0,
        'time': 0,
        'trial_index': 0
    }
    
    ### For logging times in which sync pulses were delivered to recording system
    PULSE_dict = {
        'subject': subject,
        'session': session,
        'time': 0,
        'pulse_id': 0
    }
    
    ### For logging entry of psychiatric scale rating by user
    RATING_dict = {
        'subject': subject,
        'session': session,
        'scale': '',
        'rating': 0,
        'time': 0,
        'rating_id': 0
    }

    ### For logging calculation of total psychiatric scale score by user
    SCORE_dict = {
        'subject': subject,
        'session': session,
        'score': 0,
        'time': 0,
        'score_id': 0
    }

    ### Nested dictionary to hold every type of message or data log
    message_dictionary = {
        'STIMULATION_PARAMETERS': stimulation_parameters,
        'CONNECTED': CONNECTED_message,
        'STIMULATION_CONFIGURATION': STIMULATION_CONFIGURATION_message,
        'STOP_STIMULATION': STOP_STIMULATION_message,
        'SHAM': SHAM_message,
        'END': END_message,
        'EVENT': EVENT_dict,
        'PULSE': PULSE_dict,
        'RATING': RATING_dict,
        'SCORE': SCORE_dict
    }
    
    return message_dictionary