function trial_summary = read_trial_summary(rootDir, Animal_ID)
% Obtains session summary table for animal with specified Animal_ID within
% root folder
    filelist = dir(fullfile(rootDir, '**', strcat('trial_summary_', Animal_ID, '.csv')));
    trial_summary = readtable(fullfile(filelist.folder, filelist.name));
end