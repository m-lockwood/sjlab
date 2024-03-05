function session_data = get_session_data(session_data_filepath)

    session_data = readtable(session_data_filepath);

    % Extract logical value for whether trial was correct
    session_data.correctTrial = cellfun(@(x) strcmp(x(1:end-1),'RewardedNosepoke'), session_data.TrialCompletionCode);
    session_data.abortTrial = cellfun(@(x) strcmp(x(1:end-2),'AbortedTrial'), session_data.TrialCompletionCode);
    
    % Extract the choice to poke port 0 or port 1
    session_data.nosePoke = cellfun(@(x) str2double(x(end)), session_data.TrialCompletionCode);
    session_data.nosePoke(session_data.abortTrial)=nan;
    
    % reorder variables
    session_data = movevars(session_data,"nosePoke",'After',"TrialCompletionCode");
    session_data = movevars(session_data,"abortTrial",'After',"TrialCompletionCode");
    session_data = movevars(session_data,"correctTrial",'After',"TrialCompletionCode");

end