function session_summary_ephys = get_session_summary_ephys(Animal_ID, filelist)

    variableNames = {'session_folder', 'Shanks', 'Reference'};
    variableTypes = {'cell', 'cell', 'cell'};
    
    session_summary_ephys = table('Size', [length(filelist),length(variableNames)], ...
        'VariableTypes', variableTypes, 'VariableNames',variableNames);
    
    for sessionNum = 1:length(filelist)
        session_folder = extractBetween(filelist(sessionNum).folder, strcat(Animal_ID,filesep), filesep);
        settings = xml2struct(fullfile(filelist(sessionNum).folder, filelist(sessionNum).name));
        session_attributes = settings.SETTINGS.SIGNALCHAIN{1,1}.PROCESSOR{1,1}.EDITOR.NP_PROBE.Attributes;
        rowData = [session_folder, session_attributes.electrodeConfigurationPreset, session_attributes.referenceChannel];
        session_summary_ephys(sessionNum,:) = rowData;
    end

end