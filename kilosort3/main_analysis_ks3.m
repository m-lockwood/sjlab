function main_analysis_ks3(session_filepath)

    rootH = 'D:\'; % path to temporary binary file (same size as data, should be on fast SSD)
    pathToYourConfigFile = 'C:\Github\sjlab\kilosort3\configFiles'; 
    chanMapFilename = 'chanMap_Npx2p0.mat';
    
    ops.trange    = [0 Inf]; % time range to sort
    ops.NchanTOT  = 384; % total number of channels in your recording
    
    % get folder within session_filepath containing 'settings.xml'
    recording_dir = dir(fullfile(session_filepath, '**', '*settings.xml'));
    if isempty(recording_dir)
        warning(strcat("No settings.xml found within ", session_filepath))
    elseif isscalar(recording_dir)
        recording_folder = recording_dir.folder;
    else
        warning(strcat("Multiple settings.xml files were found within folder ", ...
            session_filepath, ". Using first of ", num2str(length(recording_dir))));
        recording_folder = recording_dir(1).folder;
    end

    % Create channel map file from settings.xml in recording_folder
    createChanMapFileFromXml(recording_folder, chanMapFilename)

    run(fullfile(pathToYourConfigFile, 'configFile384.m'))
    ops.fproc   = fullfile(rootH, 'temp_wh.dat'); % proc file on a fast SSD
    ops.chanMap = fullfile(recording_folder, chanMapFilename);



    %% this block runs all the steps of the algorithm
    fprintf('Looking for data inside %s \n', session_filepath)
    
    % main parameter changes from Kilosort2 to v2.5
    ops.sig        = 20;  % spatial smoothness constant for registration
    ops.fshigh     = 300; % high-pass more aggresively
    ops.nblocks    = 5; % blocks for registration. 0 turns it off, 1 does rigid registration. Replaces "datashift" option. 
    
    % main parameter changes from Kilosort2.5 to v3.0
    ops.Th       = [9 9];
    
    % is there a channel map file in this folder?
    fs = dir(fullfile(pathToYourConfigFile, 'chan*.mat'));
    if ~isempty(fs)
        ops.chanMap = fullfile(fs(1).folder, fs(1).name);
    end
    
    % find the binary file
    fs          = dir(fullfile(session_filepath, '**', 'Neuropix-PXI-100.ProbeA','**', '*.dat'));
    ops.fbinary = fullfile(fs(1).folder, fs(1).name);
    
    rez                = preprocessDataSub(ops);
    rez                = datashift2(rez, 1);
    [rez, st3, tF]     = extract_spikes(rez);
    rez                = template_learning(rez, tF, st3);
    [rez, st3, tF]     = trackAndSort(rez);
    rez                = final_clustering(rez, tF, st3);
    rez                = find_merges(rez, 1);
    
    session_filepath = fullfile(session_filepath, 'kilosort3');
    mkdir(session_filepath)
    rezToPhy2(rez, session_filepath);

end