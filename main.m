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
    strcat(Animal_ID, filesep), filesep),filelist_behaviour); %<-- find a cleaner way of adding this (perhaps add to trial summary)?

% concatenate within-session data from all sessions for animal
trial_data_mouse = table();
for sessionNum=1:length(filelist_behaviour)
    trial_data_session = get_trial_data(fullfile(filelist_behaviour(sessionNum).folder, filelist_behaviour(sessionNum).name));
    trial_data_mouse = [trial_data_mouse;trial_data_session];
end

% save to local directory
writetable(trial_data_mouse, fullfile(output_folder, strcat('trial_summary_', Animal_ID, '.csv')));

%% summarise session-level information

% 1 behavioural data session summary
session_summary_behaviour = get_session_summary_behaviour(trial_data_mouse);

% 2 ephys data session summary
    
% 2.1 get list of ephys metadata files for animal ID and corresponding session
    % folder
filelist_ephys = dir(fullfile(input_folder, Animal_ID,'**', '*settings.xml'));
% 2.2 summarise meta-data from every file in filelist_ephys
session_summary_ephys = get_session_summary_ephys(Animal_ID, filelist_ephys);

% 3 combine behaviour and ephys session summaries
session_summary_behaviour.session_folder = sessionlist_behaviour;
session_summary=outerjoin(session_summary_behaviour, session_summary_ephys, ...
    'Keys', 'session_folder', 'MergeKeys',true);

% 4 save to local directory
writetable(session_summary, fullfile(output_folder, strcat('session_summary_', ...
    Animal_ID, '.csv')));

%% plot session summary information

