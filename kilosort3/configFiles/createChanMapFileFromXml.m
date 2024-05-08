function createChanMapFileFromXml(recording_folder, filename)

    include_sync_line=false;
    stack_channels = false;

    %% get metadata from OpenEphys settings.xml file under 'recording_filepath'
    
    % Load metadata from OpenEphys output using 'xml2struct' from open ephys 
    % MATLAB tools (https://github.com/open-ephys/open-ephys-matlab-tools)
    settings = xml2struct(fullfile(recording_folder, 'settings.xml')); 
    
    signal_chain = settings.SETTINGS.SIGNALCHAIN;
    
    if isscalar(signal_chain) % without NI-daq
        NP_probe_info = signal_chain.PROCESSOR{1,1}.EDITOR.NP_PROBE;
    else % with NI-daq
        NP_probe_info = signal_chain{1,1}.PROCESSOR{1,1}.EDITOR.NP_PROBE;
    end
    
    %% get mapping from channel ID to shankID, xcoords and ycoords
    
    channels_info = NP_probe_info.CHANNELS.Attributes;
    channels_info = struct2table(channels_info);
    
    % Extract 3rd-Last characters from channel mapping for shank ID
    channels_info = varfun(@(x) str2double(x(3:end)),channels_info);
    
    % get x and y coords for all channels
    xcoords_info = NP_probe_info.ELECTRODE_XPOS.Attributes;
    xcoords_info = (struct2table(xcoords_info));
    xcoords_info = varfun(@(x) str2double(x), xcoords_info);
    
    ycoords_info = NP_probe_info.ELECTRODE_YPOS.Attributes;
    ycoords_info = (struct2table(ycoords_info));
    ycoords_info = varfun(@(x) str2double(x), ycoords_info);
    
    % concatenate shank ID, x and y coordinates into a table T
    T = vertcat(channels_info, xcoords_info, ycoords_info);
    
    % Make channel ID a variable
    T = rows2vars(T);
    T.Properties.VariableNames = {'chanMap0ind', 'shankInd', 'xcoords','ycoords'};
    
    % Convert channel ID to double
    T.chanMap0ind = cellfun(@(x) str2double(x(7:end)), T.chanMap0ind);
    
    % order rows by channel ID
    T = sortrows(T, "chanMap0ind"); 

    if stack_channels
        % reconfigure to vertically stack channels 
        deltaY = max(T.ycoords) - min(T.ycoords);
        T.ycoords(T.shankInd==1) = T.ycoords(T.shankInd==1)+deltaY+100;
        T.ycoords(T.shankInd==2) = T.ycoords(T.shankInd==2)+deltaY+200;
        T.ycoords(T.shankInd==3) = T.ycoords(T.shankInd==2)+deltaY+300;
    
        T.xcoords(T.xcoords==258)=8;
        T.xcoords(T.xcoords==290)=40;
        T.xcoords(T.xcoords==508)=8;
        T.xcoords(T.xcoords==540)=40;
        T.xcoords(T.xcoords==758)=8;
        T.xcoords(T.xcoords==790)=40;
    end

    % replicate variable structure from open ephys output 
    if include_sync_line % including 'dead' channel where sync line would be)
        chanMap0ind = [T.chanMap0ind', T.chanMap0ind(end)+1];
        chanMap = chanMap0ind+1;
        shankInd = [T.shankInd; 1];
        xcoords = [T.xcoords; 0];
        ycoords = [T.ycoords; 0];
    else
        chanMap0ind = T.chanMap0ind';
        chanMap = chanMap0ind+1;
        shankInd = T.shankInd;
        xcoords = T.xcoords;
        ycoords = T.ycoords;
    end


    
    %% get metadata constants constants 
    % ^ can also get these from xml after specifying the correct stream!
    
    fs =30000;
    name = 'Npx2p0';
    connected = [true(length(chanMap)-1,1); false(1,1)];
    
    save(fullfile(recording_folder, filename), 'connected', 'name', ...
        'fs', 'chanMap','chanMap0ind', 'shankInd', 'xcoords', 'ycoords');

end