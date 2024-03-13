function session_summary = read_session_summary(rootDir, Animal_ID)
% Obtains session summary table for animal with specified Animal_ID within
% root folder
    filelist = dir(fullfile(rootDir, '**', strcat('session_summary_', Animal_ID, '.csv')));
    session_summary = readtable(fullfile(filelist.folder, filelist.name));
end