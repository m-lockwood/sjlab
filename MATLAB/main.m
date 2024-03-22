clc
close all
clear

%% CONFIG

para = CONFIG;
Animal_ID = '98';

%% write intermediate variables and save locally

% get list of files containing session-level behavioural data for each mouse
filelist_behaviour = dir(fullfile(para.input_folder, Animal_ID,'**', '*experimental-data.csv'));
sessionlist_behaviour = arrayfun(@(x) extractBetween(x.folder, ...
    strcat(Animal_ID, filesep), filesep),filelist_behaviour); %<-- find a cleaner way of adding this (perhaps add to trial summary)?

% concatenate within-session data from all sessions for animal
trial_data_mouse = table();
for sessionNum=1:length(filelist_behaviour)
    trial_data_session = get_trial_data(fullfile(filelist_behaviour(sessionNum).folder, ...
        filelist_behaviour(sessionNum).name));
    trial_data_mouse = [trial_data_mouse;trial_data_session];
end

% save to local directory
writetable(trial_data_mouse, fullfile(para.output_folder, 'intermediate_variables', ...
    strcat('trial_summary_', Animal_ID, '.csv')));

%% summarise session-level information

% 1 behavioural data session summary
sessions_summary_behaviour = get_session_summary_behaviour(trial_data_mouse);

% 2 ephys data session summary
    
% 2.1 get list of ephys metadata files for animal ID and corresponding session
    % folder
filelist_ephys = dir(fullfile(para.input_folder, Animal_ID,'**', '*settings.xml'));
% 2.2 summarise meta-data from every file in filelist_ephys
sessions_summary_ephys = get_session_summary_ephys(Animal_ID, filelist_ephys);

% 3 combine behaviour and ephys session summaries
sessions_summary_behaviour.session_folder = sessionlist_behaviour;
sessions_summary=outerjoin(sessions_summary_behaviour, sessions_summary_ephys, ...
    'Keys', 'session_folder', 'MergeKeys',true);

% 4 save to local directory
writetable(sessions_summary, fullfile(para.output_folder, 'intermediate_variables', ...
    strcat('session_summary_', Animal_ID, '.csv')));

%% plot session summary information

fig = plot_sessions_summary(para, sessions_summary_behaviour);
output_folder = fullfile(para.output_folder, 'plot_performance_across_sessions');
filename = strcat('plot_session_bias_accuracy_', Animal_ID);
save_figure(fig, output_folder, filename);