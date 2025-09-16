% This script opens a server waiting for commands from a client.
% In addition to other commands, the server will receive stimulation
% configurations from the client, configure Blackrock's Cerestim, deliver
% the stimulation with the provided parameters, and respond with the time
% in which the stimulation was delivered.
% Latest update : July 4, 2024

clearvars; 
close all;
clc;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Enter session information before running script %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
global subject_code
subject_code = 'SC000';
server_ip = '192.168.1.1'
server_port = 8888

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Initialization of Experiment Session %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
global datetime_format
datetime_format = 'yyyy-mm-dd_HH-MM-SS';
global session
session = datestr(now, datetime_format); %Each new session will be in a folder with start date and time as name

session_directory = ['D:\data\stimulation_controller\', subject_code, '\stimulation_server\session_', session, '\'];
mkdir(session_directory)

time_out_seconds = 3600;    % Inactive duration in seconds before server times out

%%% Initializing variables that will hold stimulation configurations,
%%% being extended as arrays and input into table before saving. 
label = cell(1, 1);         % Bipolar depth electrode label
anode = 0;                  % Anode depth electrode channel number
cathode = 0;                % Cathode depth electrode channel number
amplitude = 0;              % Stimulation pulse amplitude in mA
frequency = 0;              % Stimulation pulse frequency in Hz
pulse_width = 0;            % Width of half of square wave in microseconds
duration = 0;               % Stimulation pulse series duration in milliseconds
time = 0;                   % Time of delivery in datetime format
parameter_index = 1;        % Index to increment with each configuration received to extend arrays

%%% Initialize Cerestim
addpath(genpath('C:\Blackrock Microsystems\Binaries'))
stimulator = cerestim96();
device_list = stimulator.scanForDevices();
stimulator.selectDevice(device_list(1));
stimulator.connect; 
if (stimulator.isConnected())
    disp("Cerestim is connected.");
else
    disp("Cerestim is not connected."); %Turn Cerestim OFF and ON, and try again.
    exit
end

%%% Initialize and Configure Server
server = tcpserver(server_ip, server_port, "Timeout", time_out_seconds, "ConnectionChangedFcn", @connectionFcn);
configureCallback(server, "byte", 4, @readDataFcn); % At least 4 bytes need to be received to trigger server response

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% Function to manage connection to and closure of server
function connectionFcn(server_handle, ~)
if server_handle.Connected
    disp("Client connection accepted by server.")
else
    disp("Client has disconnected.")
    evalin('base', 'stimulator.stop');
    evalin('base', 'stimulator.disconnect');
    evalin('base', 'clear stimulator');
    evalin('base', 'clear server');
    evalin('base', 'parameters_used = table(label'', anode'', cathode'', amplitude'', frequency'', pulse_width'', duration'', time'');');
    evalin('base', 'save([session_directory, ''parameters_used.mat''], ''parameters_used'')');
end
end

%%% Function to read and execute requests from task computer client and send back response
function readDataFcn(server_handle, ~)
disp("Data was received from the client.\n")

received_message = readline(server_handle);
received_message = jsondecode(received_message);
message_type = received_message.message_type;

switch message_type
    case 'CONNECTED'
        disp("Client connected.")
        message_struct = get_message_struct();
        message_struct.message_type = "WAITING";
        message_struct.server_time = datetime('now'); 
        message_string = jsonencode(message_struct);
        writeline(server_handle, message_string);
        
    case 'SHAM'
        disp("Sham event.")
        message_struct = get_message_struct();
        message_struct.message_type = "SHAMMING";
        message_struct.server_time = datetime('now'); 
        message_string = jsonencode(message_struct);
        writeline(server_handle, message_string);
        
    case 'STIMULATION_CONFIGURATION'
        %%% Stop any previous stimulus if still ongoing
        evalin('base','stimulator.stop');
        
        %%% Process configuration and add to parameter array
        stimulation_configuration = received_message.data;
        
        configuration_label = stimulation_configuration.label;
        evalin('base',sprintf('time(parameter_index) = %d;', datetime('now')));
        evalin('base',sprintf('label{parameter_index} = ''%s'';', configuration_label));
        
        configuration_anode = stimulation_configuration.anode;
        evalin('base', sprintf('anode(parameter_index) = %s;', configuration_anode));
        
        configuration_cathode = stimulation_configuration.cathode;
        evalin('base', sprintf('cathode(parameter_index) = %s;', configuration_cathode));
        
        configuration_amplitude = stimulation_configuration.amplitude;
        evalin('base', sprintf('amplitude(parameter_index) = %d;', configuration_amplitude));
        
        configuration_frequency = stimulation_configuration.frequency;
        evalin('base', sprintf('frequency(parameter_index) = %d;', configuration_frequency));
        
        configuration_pulse_width = stimulation_configuration.pulse_width;
        evalin('base', sprintf('pulse_width(parameter_index) = %d;', configuration_pulse_width));
        
        configuration_duration = stimulation_configuration.duration;
        evalin('base', sprintf('duration(parameter_index) = %d;', configuration_duration));
        evalin('base', 'parameter_index = parameter_index + 1;')
        
        n_pulses =  floor(configuration_frequency * (configuration_duration / 1000));
    
        if configuration_amplitude > 10 %mA
            quit()
        end
        
        %%% Configure Cerestim
        fprintf('Configuring stimulation %s at: %d mA,%s Hz,%d us pulse width for %d ms in duration.\n', configuration_label, configuration_amplitude, configuration_frequency, configuration_pulse_width, configuration_duration);
        
        %%% Pseudobipolar pattern, because both patterns are technically monopolar
        
        %%% Stimulation pattern for cathode
        evalin('base', ['stimulator.setStimPattern(''waveform'', 1, ''polarity'', 0,',...
            sprintf('''pulses'', %d,', n_pulses),...
            sprintf('''amp1'', %d, ''amp2'', %d,', repmat(configuration_amplitude * 1000, 1 , 2)),... % Cerestim amplitude configuration in uA
            sprintf('''width1'',%d,''width2'',%d,', repmat(configuration_pulse_width, 1, 2)),...
            sprintf('''interphase'', 55, ''frequency'', %d)', configuration_frequency)]);
        
        %%% Stimulation pattern for anode with opposite polarity
        evalin('base', ['stimulator.setStimPattern(''waveform'', 2, ''polarity'', 1,',...
            sprintf('''pulses'', %d,', n_pulses),...
            sprintf('''amp1'', %d, ''amp2'', %d,', repmat(configuration_amplitude * 1000, 1, 2)),...
            sprintf('''width1'',%d,''width2'',%d,', repmat(configuration_pulse_width, 1, 2)),...
            sprintf('''interphase'', 55, ''frequency'', %d)', configuration_frequency)]);
        
        evalin('base', 'stimulator.beginSequence');
        evalin('base', 'stimulator.beginGroup');
        evalin('base', sprintf('stimulator.autoStim(%d, 1)', str2double(configuration_cathode)));
        evalin('base', sprintf('stimulator.autoStim(%d, 2)', str2double(configuration_anode)));
        evalin('base', 'stimulator.endGroup');
        evalin('base', 'stimulator.endSequence');
        
        %%% Prepare response with time right before stimulation pattern delivered
        disp("Delivering stimulus.")
        message_struct = get_message_struct();
        message_struct.message_type = "DELIVERING_STIMULUS";
        message_struct.server_time = datetime('now'); 
        
        %%% Stimulus delivery
        evalin('base', 'stimulator.play(1)');
        
        %%% Send response to client
        message_string = jsonencode(message_struct);
        writeline(server_handle, message_string);
        
    case 'STOP_STIMULATION'
        disp("Stopping stimulation.")
        message_struct = get_message_struct();
        message_struct.message_type = "STOPPING_STIMULATION";
        message_struct.server_time = datetime('now'); 
        
        evalin('base','stimulator.stop');
        
        message_string = jsonencode(message_struct);
        writeline(server_handle,message_string);
        
    case 'END'
        disp("Experiment ended.");
        evalin('base','stimulator.stop');
        evalin('base','stimulator.disconnect');
        evalin('base','clear stimulator');
        evalin('base','clear server');
        evalin('base','parameters_used = table(label'', anode'', cathode'', amplitude'', frequency'', pulse_width'', duration'', time'');');
        evalin('base', 'save([session_directory, ''parameters_used.mat''], ''parameters_used'')');
end
end

%%% Function that prepares message struct for server's response to client
function message_struct = get_message_struct()
global subject_code
global session
message_struct = struct;
message_struct.subject = subject_code;
message_struct.session = session;
message_struct.message_type = "RESPONSE";
data = struct;
data.n_fields = 0;
message_struct.data = data;
message_struct.sender = "server";
message_struct.server_time = 0;
message_struct.client_time = 0;
message_struct.message_id = 0;
end