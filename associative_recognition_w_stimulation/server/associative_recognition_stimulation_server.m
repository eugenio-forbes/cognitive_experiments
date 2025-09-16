% Blackrock stimulation script to be executed during associative recognition with stimulation task.
% This script will act as a server and will deliver theta burst stimulation pulses at the request
% of task client running in experiment laptop.
% 
% Parameters of theta burst stimulation can be edited.
%
%
% Eugenio Forbes
% Acknowledgement: Thanks to David Wang and Tung To for their contributions

clear all; 
close all;
clc;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Enter session information before running script %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
subject_code = 'SC000';
session_number = 0;
server_ip = '192.168.1.1';
server_post = 8888;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  Editable Parameters %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
pulse_frequency = 150;       % Frequency of pulses within each burst (bursts delivered in theta frequency range)
burst_frequency = 4;         % Theta burst Frequency.
f_cycle_burst = 0.25;        % Fraction of theta frequency cycle that will contain a burst of pulses
stimulation_duration = 4;    % Duration in seconds of theta burst stimulation
pulse_amplitude = 2000;      % Amplitude of pulses in stimulation, in uA.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Initialization of Experiment Session %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% Initializing Cerestim
addpath(genpath('C:\Blackrock Microsystems\Binaries'));
stimulator = cerestim96();
device_list = stimulator.scanForDevices();
stimulator.selectDevice(device_list(1));
stimulator.connect; 

if(stimulator.isConnected())
    disp("Cerestim is connected.");
else
    disp("Cerestim is not connected."); %Turn Cerestim OFF and ON, and try again.
end

%%% Making session directory to save session data
session_directory = ['C:\data\', subject_code, '\associative_recognition_w_stimulation\session_', num2str(session_number), '\'];
if ~exist(session_directory, 'dir')
    mkdir(session_directory)
else
    error("Choose a different session number or delete previous files.");
end

%%% Array to save at the end of session for adding information to events.csv saved by client computer
parameters_used = zeros(1,3);
parameter_index = 1;

%%% Calculation of interburst interval to time delivery of each burst and number of pulses in a burst
cycle_duration = 1/burst_frequency % Time between each first pulse. This is time used as interburst interval because stimulation runs asynchronously.
burst_duration = cycle_duration * f_cycle_burst;
n_pulses = floor(burst_duration * pulse_frequency);
global interburst_interval;
interburst_interval = cycle_duration;
global n_repetitions;
n_repetitions = stimulation_duration * burst_frequency; % Number of bursts delivered based on stimulation duration

%%% Configuring Cerestim for delivery of a single burst of pulses with the specified parameters
stimulator.setStimPattern('waveform', 1, 'polarity', 0, 'pulses', n_pulses, 'amp1', pulse_amplitude,...
        'amp2', pulse_amplitude, 'width1', 300, 'width2', 300, 'interphase', 55, 'frequency', pulse_frequency)
stimulator.beginSequence;
stimulator.autoStim(1, 1);
stimulator.endSequence;

%%% Server initialization
server = tcpserver(server_ip, server_port, 'Timeout', 3600, 'ConnectionChangedFcn', @connectionFcn)
configureCallback(server, 'byte', 4, @readDataFcn); % Server responds every time 4 bytes are received. Client will be sending commands as uint32 integers.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% Function to manage connection to and closure of server
function connectionFcn(server_handle, ~)
if server_handle.Connected
    disp("Client connection accepted by server.")
else
    disp("Client has disconnected.")
    evalin('base', 'stimulator.disconnect');
    evalin('base', 'clear stimulator');
    evalin('base', 'clear server');
    evalin('base', 'save([session_directory,''parameters_used.mat''],''parameters_used'')');
end
end

%%% Function to read and execute requests from task computer client
function readDataFcn(server_handle, ~)
global n_repetitions;
global interburst_interval;
disp("Data was received from the client.")
data = read(server_handle, 1, 'uint32');
disp(data);
switch data
    case 0
        disp("No stimulus delivered.")
    case 1
        disp("Delivering theta burst stimulus.")
        for i = 1 : n_repetitions
            evalin(base, 'stimulator.play(1)');
            pause(interburst_interval);
        end
        evalin('base', 'parameters_used(parameter_index, 1) = burst_frequency;')
        evalin('base', 'parameters_used(parameter_index, 2) = pulse_amplitude;')
        evalin('base', 'parameters_used(parameter_index, 3) = pulse_frequency;')
        evalin('base', 'parameter_index = parameter_index + 1;')
end
end