function session_summary_ephys = get_session_summary_ephys(Animal_ID, filelist)

    variableNames = {'session_folder', 'Shanks', 'Reference'};
    variableTypes = {'cell', 'cell', 'cell'};
    
    session_summary_ephys = table('Size', [length(filelist),length(variableNames)], ...
        'VariableTypes', variableTypes, 'VariableNames',variableNames);
    
    for sessionNum = 1:length(filelist)
        filelist(sessionNum).folder
        sessionNum
        session_folder = extractBetween(filelist(sessionNum).folder, strcat(Animal_ID,filesep), filesep);
        settings = xml2struct(fullfile(filelist(sessionNum).folder, filelist(sessionNum).name));
        signal_chain = settings.SETTINGS.SIGNALCHAIN;
        if isscalar(signal_chain) % without NI-daq
            session_attributes = signal_chain.PROCESSOR{1,1}.EDITOR.NP_PROBE.Attributes;
        else % with NI-daq
            session_attributes = signal_chain{1,1}.PROCESSOR{1,1}.EDITOR.NP_PROBE.Attributes;
        end
            
        rowData = [session_folder, session_attributes.electrodeConfigurationPreset, session_attributes.referenceChannel];
        session_summary_ephys(sessionNum,:) = rowData;
    end

end