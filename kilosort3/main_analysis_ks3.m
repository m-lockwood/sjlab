function main_analysis_ks3(rootZ)

    rootH = 'D:\'; % path to temporary binary file (same size as data, should be on fast SSD)
    pathToYourConfigFile = 'C:\Github\sjlab\kilosort3\configFiles'; % take from Github folder and put it somewhere else (together with the master_file)
    chanMapFile = 'chanMap_Npx2p0.mat';
    
    ops.trange    = [0 Inf]; % time range to sort
    ops.NchanTOT  = 385; % total number of channels in your recording
    
    run(fullfile(pathToYourConfigFile, 'configFile384.m'))
    ops.fproc   = fullfile(rootH, 'temp_wh.dat'); % proc file on a fast SSD
    ops.chanMap = fullfile(pathToYourConfigFile, chanMapFile);
    %% this block runs all the steps of the algorithm
    fprintf('Looking for data inside %s \n', rootZ)
    
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
    fs          = dir(fullfile(rootZ, '**', 'Neuropix-PXI-100.ProbeA','**', '*.dat'));
    ops.fbinary = fullfile(fs(1).folder, fs(1).name);
    
    rez                = preprocessDataSub(ops);
    rez                = datashift2(rez, 1);
    [rez, st3, tF]     = extract_spikes(rez);
    rez                = template_learning(rez, tF, st3);
    [rez, st3, tF]     = trackAndSort(rez);
    rez                = final_clustering(rez, tF, st3);
    rez                = find_merges(rez, 1);
    
    rootZ = fullfile(rootZ, 'kilosort3');
    mkdir(rootZ)
    rezToPhy2(rez, rootZ);

end