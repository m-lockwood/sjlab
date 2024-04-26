clear
close all

%% directory CONFIG

%addpath(genpath('C:\Github\sjlab\kilosort3')) % path to kilosort folder
%addpath('D:\GitHub\npy-matlab') % for converting to Phy
rootDir= 'Z:\projects\FlexiVexi\behavioural_data';
Animal_ID='98';

% Find all ephys data within Animal_ID folder
sessionList = dir(fullfile(rootDir, Animal_ID,'**', 'Neuropix-PXI-100.ProbeA','**', '*continuous.dat'));

%% main 
for i=length(sessionList):-1:1
    
    sessionFolder = extractBetween(sessionList(i).folder,strcat(filesep,Animal_ID,filesep), filesep);
    sessionPath = fullfile(extractBefore(sessionList(i).folder,sessionFolder), sessionFolder);

    if isempty(dir(fullfile(sessionPath{1,1}, '**', '*amplitudes.npy'))) % check if kilosort has already been run on this session

        rootZ = sessionPath{1,1};
    
        kilosort3_main_analysis(rootZ);
    
        close all

    else
        disp(strcat("Kilosort has already been run on session ", sessionFolder{1,1}, ". Skipping analysis of this session."));
    end

end
