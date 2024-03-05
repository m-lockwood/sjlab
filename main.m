clc
close all
clear

%% CONFIG

Animal_ID = '101';
input_folder = 'W:\projects\FlexiVexi\behavioural_data';
output_folder = 'C:\Users\megan\Documents\sjlab\flexible-navigation-task\Data Analysis';

%% write intermediate variables and save locally

% get list of files containing session-level behavioural data for each mouse
sessionList = dir(fullfile(input_folder, Animal_ID,'**', '*experimental-data.csv'));  

% concatenate within-session data from all sessions for animal
trial_data_mouse = table();
for sessionNum=1:length(sessionList)
    trial_data_session = get_trial_data(fullfile(sessionList(sessionNum).folder, sessionList(sessionNum).name));
    trial_data_mouse = [trial_data_mouse;trial_data_session];
end

% save to local directory
writetable(trial_data_mouse, fullfile(output_folder, strcat('trial_summary_', Animal_ID, '.csv')));

%% summarise session-level information

% behavioural data
session_summary_behaviour = get_session_summary(trial_data_mouse);

% ephys data

% get list of folders containing ephys data for all sessions of mouse with
% specified Animal-ID
sessionList = dir(fullfile(input_folder, Animal_ID,'**', '*settings.xml'));

variableNames = {'session_folder', 'Shanks', 'Reference'};
variableTypes = {'cell', 'cell', 'cell'};

session_summary_ephys = table('Size', [length(sessionList),length(variableNames)], ...
    'VariableTypes', variableTypes, 'VariableNames',variableNames);

for sessionNum = 1:length(sessionList)
    session_folder = extractBetween(sessionList(sessionNum).folder, strcat(Animal_ID,filesep), filesep);
    settings = xml2struct(fullfile(sessionList(sessionNum).folder, sessionList(sessionNum).name));
    session_attributes = settings.SETTINGS.SIGNALCHAIN.PROCESSOR{1,1}.EDITOR.NP_PROBE.Attributes;
    rowData = [session_folder, session_attributes.electrodeConfigurationPreset, session_attributes.referenceChannel];
    session_summary_ephys(sessionNum,:) = rowData;
end

% save to local directory
writetable(session_summary_mouse, fullfile(output_folder, strcat('session_summary_', Animal_ID, '.csv')));

%% plot session summary
