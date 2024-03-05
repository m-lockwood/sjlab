clc
close all
clear

%% CONFIG

Animal_ID = '98';
input_folder = 'W:\projects\FlexiVexi\behavioural_data';
output_folder = 'C:\Users\megan\Documents\sjlab\flexible-navigation-task\Data Analysis';

%% write intermediate variables and save locally

% get list of files containing session-level behavioural data for each mouse
filelist_behaviour = dir(fullfile(input_folder, Animal_ID,'**', '*experimental-data.csv'));
sessionlist_behaviour = arrayfun(@(x) extractBetween(x.folder, ...
    strcat(Animal_ID, filesep), filesep),filelist_behaviour); %<-- find a cleaner way of adding this

% concatenate within-session data from all sessions for animal
trial_data_mouse = table();
for sessionNum=1:length(filelist_behaviour)
    trial_data_session = get_trial_data(fullfile(filelist_behaviour(sessionNum).folder, filelist_behaviour(sessionNum).name));
    trial_data_mouse = [trial_data_mouse;trial_data_session];
end

% save to local directory
writetable(trial_data_mouse, fullfile(output_folder, strcat('trial_summary_', Animal_ID, '.csv')));

%% summarise session-level information

% get list of ephys metadata files for animal ID and corresponding session
% folder
filelist_ephys = dir(fullfile(input_folder, Animal_ID,'**', '*settings.xml'));

% behavioural data session summary
session_summary_behaviour = get_session_summary(trial_data_mouse);

% ephys data session summary
variableNames = {'session_folder', 'Shanks', 'Reference'};
variableTypes = {'cell', 'cell', 'cell'};

session_summary_ephys = table('Size', [length(filelist_ephys),length(variableNames)], ...
    'VariableTypes', variableTypes, 'VariableNames',variableNames);

for sessionNum = 1:length(filelist_ephys)
    session_folder = extractBetween(filelist_ephys(sessionNum).folder, strcat(Animal_ID,filesep), filesep);
    settings = xml2struct(fullfile(filelist_ephys(sessionNum).folder, filelist_ephys(sessionNum).name));
    session_attributes = settings.SETTINGS.SIGNALCHAIN.PROCESSOR{1,1}.EDITOR.NP_PROBE.Attributes;
    rowData = [session_folder, session_attributes.electrodeConfigurationPreset, session_attributes.referenceChannel];
    session_summary_ephys(sessionNum,:) = rowData;
end

session_summary_behaviour.session_folder = sessionlist_behaviour;
session_summary=outerjoin(session_summary_behaviour, session_summary_ephys, 'Keys', 'session_folder', 'MergeKeys',true);

% save to local directory
writetable(session_summary, fullfile(output_folder, strcat('session_summary_', Animal_ID, '.csv')));

%% plot session summary
