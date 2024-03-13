function session_summary = get_session_summary_behaviour(trial_data_mouse)

    % index rows corresponding to each session
    sessionIdx = findgroups(cellstr(trial_data_mouse.Session_ID));
    
    % get session summary info
    session_summary = table();
    session_summary.Animal_ID = splitapply(@(x) {unique(cellstr(x))}, trial_data_mouse.Animal_ID, sessionIdx);
    session_summary.Session_ID = splitapply(@(x) {unique(cellstr(x))}, trial_data_mouse.Session_ID, sessionIdx);
    session_summary.Stage = splitapply(@(x) {unique(x)}, trial_data_mouse.TrainingStage, sessionIdx);
    session_summary.Substage = splitapply(@(x) {unique(x)}, trial_data_mouse.TrainingSubstage, sessionIdx);
    session_summary.AudioCueIdentities = splitapply(@(x) {unique(x)}, trial_data_mouse.AudioCueIdentity, sessionIdx);
    
    % get session summary stats
    session_summary.numTrials = splitapply(@(x) length(x), trial_data_mouse.CorrectTrial, sessionIdx);
    session_summary.numTrialsCompleted = splitapply(@(x) sum(~x), trial_data_mouse.AbortTrial, sessionIdx);
    session_summary.abortTrialRate = splitapply(@(x) sum(x)/length(x), trial_data_mouse.AbortTrial, sessionIdx);
    session_summary.accuracy_all_trials = splitapply(@(x) sum(x)/sum(~isnan(x)), trial_data_mouse.CorrectTrial, sessionIdx);
    session_summary.accuracy_all_trials_bpci = get_bpci(session_summary.accuracy_all_trials, session_summary.numTrials);
    session_summary.accuracy_completed_trials = splitapply(@(x,y) sum(x)/sum(~y), trial_data_mouse.CorrectTrial, trial_data_mouse.AbortTrial, sessionIdx);
    session_summary.accuracy_completed_trials_bpci = get_bpci(session_summary.accuracy_completed_trials, session_summary.numTrialsCompleted);
    session_summary.choice_port_0 = splitapply(@(x) sum(x==0)/sum(~isnan(x)), trial_data_mouse.ChoicePort, sessionIdx);
    session_summary.choice_port_1 = splitapply(@(x) sum(x==1)/sum(~isnan(x)), trial_data_mouse.ChoicePort, sessionIdx);
    session_summary.choice_port_2 = splitapply(@(x) sum(x==2)/sum(~isnan(x)), trial_data_mouse.ChoicePort, sessionIdx);
    %session_summary.choice_port_1_bpci = get_bpci(session_summary.bias, session_summary.numTrials);

end