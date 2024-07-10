recording_filepath = 'Z:\projects\FlexiVexi\behavioural_data\98\2024-04-16T10-37-23\Open-Ephys\98_2024-04-16_11-37-19\Record Node 102\';

%% get metadata from OpenEphys output

% Load metadata from OpenEphys output using 'xml2struct' from open ephys 
% MATLAB tools (https://github.com/open-ephys/open-ephys-matlab-tools)
settings = xml2struct(fullfile(recording_filepath, 'settings.xml')); % tion

NP_probe_info = settings.SETTINGS.SIGNALCHAIN{1,1}.PROCESSOR{1,1}.EDITOR.NP_PROBE;

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
T.Properties.VariableNames = {'chanMap0ind', 'shankInd', 'xcoords', 'ycoords'};

% Convert channel ID to double
T.chanMap0ind = cellfun(@(x) str2double(x(7:end)), T.chanMap0ind);

% order rows by channel ID
T = sortrows(T, "chanMap0ind"); 

% replicate variable structure from open ephys output
chanMap0ind_ = T.chanMap0ind';
chanMap_ = chanMap0ind_+1;
shankInd_ = T.shankInd;
xcoords_ = T.xcoords;
ycoords_ = T.ycoords;

%% get metadata constants constants 
% ^ can also get these from xml after specifying the correct stream!

fs_ =30000;
name_ = 'Npx2p0';
connected_ = true(length(chanMap_),1);

save(fullfile(recording_filepath, 'chanMap_Npx2p0_.mat'), 'connected_', 'name_', ...
    'fs', 'chanMap_','chanMap0ind_', 'shankInd_', 'xcoords_', 'ycoords_');