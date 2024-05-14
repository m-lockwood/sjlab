clear
close all

%% directory CONFIG
rootDir= 'Z:\projects\FlexiVexi\behavioural_data';
Animal_ID='FNT099';

% Find all ephys data within Animal_ID folder
%sessionList = dir(fullfile(rootDir, Animal_ID,'**', 'Neuropix-PXI-100.ProbeA','**', '*continuous.dat'));
sessionList = dir(fullfile(rootDir, Animal_ID,'**', '*settings.xml'));

para = CONFIG_KS3;

%% main 
for i=1:length(sessionList)
    
    sessionFolder = extractBetween(sessionList(i).folder,strcat(filesep,Animal_ID,filesep), filesep);
    session_filepath = fullfile(extractBefore(sessionList(i).folder,sessionFolder), sessionFolder);
    session_filepath = session_filepath{1,1};

    % run if either 'overwrite' set to 'True' or analysis has not already run on this session
    if or(para.overwrite, isempty(dir(fullfile(session_filepath, '**', '*amplitudes.npy')))) 

        main_analysis_ks3(para, session_filepath);
        close all

    else
        disp(strcat("Kilosort has already been run on session ", sessionFolder{1,1}, ...
            ". Skipping analysis of this session."));
    end

end