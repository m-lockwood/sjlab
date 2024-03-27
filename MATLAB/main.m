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

    session_data_filepath = fullfile(filelist_behaviour(sessionNum).folder, ...
            filelist_behaviour(sessionNum).name);
    session_ID = get_session_ID(session_data_filepath);

    % output folder for session intermediate variables
    output_folder_session = fullfile(para.output_folder, 'intermediate_variables', Animal_ID);
    filename = strcat(Animal_ID, '_', session_ID, '_trial_data.csv');

    if ~isfile(fullfile(output_folder_session, filename))
        trial_data_session = get_trial_data(session_data_filepath);
        save_table(trial_data_session, output_folder_session, filename);
    else % if trial summary already exists
       trial_data_session = read_trial_data(fullfile(output_folder_session, filename));
    end

    %concatenate across all sessions 
    trial_data_mouse = [trial_data_mouse;trial_data_session];

end
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

fig = plot_sessions_summary(para, sessions_summary);
output_folder = fullfile(para.output_folder, 'plot_performance_across_sessions');
filename = strcat('plot_session_bias_accuracy_', Animal_ID);
save_figure(fig, output_folder, filename);

%% plot trial summary information (within each session)

filelist = dir(fullfile(para.output_folder, 'intermediate_variables', Animal_ID, '*trial_data.csv'));

% loop through all session with local trial-level data saved
for sessionNum=1:length(filelist)

    % read trial-level information
    trial_data_session = read_trial_data(fullfile(filelist(sessionNum).folder, filelist(sessionNum).name));
    Session_ID = trial_data_session.Session_ID(1,:);
    
    % get output folder and filename for fig
    output_folder = fullfile(para.output_folder, 'plot_performance_across_trials', Animal_ID);
    filename = strcat('plot_trial_bias_accuracy_', Animal_ID, '_', Session_ID);

    if ~isfile(fullfile(output_folder, strcat(filename, '.png')))
        fig = plot_trials_summary(para, trial_data_session);
        save_figure(fig, output_folder, filename);
        close
    else
        disp(strcat("Skipping ", Session_ID, " session plot as it already exists."))
    end
end