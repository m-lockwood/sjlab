clear

para = CONFIG;
Animal_ID = '98';

filelist = dir(fullfile(para.output_folder, 'intermediate_variables', Animal_ID, '*trial_data.csv'));

% plot params
titleFontSize=16;
faceAlpha = 0.15;
accuracy_ylims = [0.2 1];
choice_ylims = [0 1];

plot_against_time = false;
plot_aborted_trials = false;
w=10; 

for sessionNum=1:length(filelist)

%% get plot variables

trial_data_session = read_trial_data(fullfile(filelist(sessionNum).folder, filelist(sessionNum).name));
Session_ID = trial_data_session.Session_ID(1,:);

output_folder = fullfile(para.output_folder, 'plot_performance_across_trials', Animal_ID);
filename = strcat('plot_trial_bias_accuracy_', Animal_ID, '_', Session_ID);

if ~isfile(fullfile(output_folder, strcat(filename, '.png')))
    %trial_data_session(trial_data_session.AbortTrial==1,:) = [];

    disp(strcat("Plotting session ", Session_ID, " ..."));

    correctTrial = double(trial_data_session.CorrectTrial);
    correctCompletedTrial = correctTrial; 
    correctCompletedTrial(trial_data_session.AbortTrial==1)=nan;
    
    accuracy_movmean_all_trials = movmean_omitnan(correctTrial, w);
    accuracy_movmean_completed_trials = movmean_omitnan(correctCompletedTrial, w);
    
    choice_bias_movmean = movmean_omitnan(trial_data_session.ChoicePort, w);
    
    if plot_against_time
        x = NosepokeInTime;
        x(trial_data_session.AbortTrial==1)=nan;
    else
        x = 1:height(trial_data_session);
    end
    
    if ~plot_aborted_trials
        abortTrial = logical(trial_data_session.AbortTrial);
        x=1:sum(~abortTrial);
        accuracy_movmean_completed_trials(abortTrial) = [];
        accuracy_movmean_all_trials(abortTrial) = [];
        choice_bias_movmean(abortTrial) = [];
    end
    
    %% plot local accuracy and choice bias
    
    fig = figure('Visible','on', 'Position', [278 79 928 883]);
    tl = tiledlayout(2,1);
    tl.Padding = "compact";
    
    title(tl,[strcat("Mouse ", Animal_ID), Session_ID, ""], "FontSize", titleFontSize+2);
    xlabel(tl, 'Trial Number', "FontSize",titleFontSize);
    
    ax1 = nexttile;
        hold on;
        title(ax1, strcat('Plot accuracy over sliding window, length m=', num2str(w)), 'FontSize',titleFontSize)
        pl1 = plot(x, accuracy_movmean_completed_trials, 'LineWidth', 2, 'color', ...
            para.colour_accuracy);
        pl2 = plot(x, accuracy_movmean_all_trials, 'LineWidth', 2, 'Color', ...
            para.colour_accuracy, 'LineStyle','--');
        yline(0.5, '--', "LineWidth",1);
        ylim(accuracy_ylims)
        xlim([min(x) max(x)]);
        ylabel('Fraction of Correct Trials', "FontSize",titleFontSize);
        legend([pl1 pl2], {'Fraction of Completed Trials', 'Fraction of All Trials'}, ...
            'FontSize', titleFontSize, 'Location','southoutside');
    
    ax2 = nexttile;
        hold on;
        title(ax2, strcat('Plot local choice bias over sliding window, length m=', num2str(w)), 'FontSize',titleFontSize);
        pl1 = plot(x, choice_bias_movmean, 'color', para.colour_choice, 'LineWidth', 2);
        yline(0.5, ':', "LineWidth",1);
        ylim(choice_ylims)
        xlim([min(x) max(x)]);
        ylabel('Choice Ratio Port 1 / Port 0', "FontSize",titleFontSize);
    
    % save plot
    save_figure(fig, output_folder, filename);
    close
    disp("Done.")
else
    disp(strcat("Skipping ", Session_ID, " session plot as it already exists."))
end

end