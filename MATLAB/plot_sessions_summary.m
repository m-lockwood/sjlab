function fig = plot_sessions_summary(para, sessions_summary)

    % Plot params
    plot_dayNum = false; % determines whether to plot data against date or session number
    titleFontSize=16;
    faceAlpha = 0.15;
    accuracy_ylims = [0.2 1];
    choice_ylims = [0 1];
    
    %% configure plot layout

    fig = figure('Visible','on', 'Position', [278 79 928 883]);
    tl = tiledlayout(2,1);
    tl.Padding = "compact";

    Animal_ID = sessions_summary.Animal_ID{1,1};

    title(tl,[strcat("Mouse ", Animal_ID, " Session Summary Data") ""], "FontSize", titleFontSize+2);
    xlabel(tl, 'Days since training started', "FontSize",titleFontSize);
    
    % define x-axis data
    if plot_dayNum
        dayNum = (sessions_summary.Session_ID');
        dayNum = datenum(dayNum, 'yyyy-mm-dd');
        dayNum = dayNum-dayNum(1);
        x = dayNum;
    else
        x = 1:height(sessions_summary);
        x = x';
    end

    ephys_data_available = ~(sessions_summary.electrodeConfiguration=="");

    %% plot accuracy of all non-aborted trials
    ax1 = nexttile;
        hold on;
        title(ax1, 'Plot performance over sessions', 'FontSize',titleFontSize)
        pl1 = plot_shaded_error_bar(x, sessions_summary.accuracy_completed_trials, ...
            sessions_summary.accuracy_completed_trials_bpci, para.colour_accuracy, faceAlpha);

        pl3 = mark_condition(x,sessions_summary.accuracy_completed_trials, ...
            ephys_data_available,para.colour_accuracy);

        pl2 = plot(x, sessions_summary.accuracy_all_trials, 'LineWidth', 2, 'Color', ...
            para.colour_accuracy, 'LineStyle','--');
        yline(0.5, '--', "LineWidth",1);
        yline(0.7, ':', "LineWidth",1);
        ylim(accuracy_ylims)
        xlim([min(x) max(x)]);
        ylabel('Fraction of Correct Trials', "FontSize",titleFontSize);
        legend([pl1 pl2 pl3], {'Fraction of Completed Trials', 'Fraction of All Trials', ...
            'Ephys Data Available'}, 'FontSize', titleFontSize, 'Location','southeast');
    
    %% plot choice bias on all non-aborted trials (for which choice was port 0 or port 1)
    
    ax2 = nexttile;
        hold on;
        title(ax2, 'Plot choice bias over sessions', 'FontSize',titleFontSize);
        pl1 = plot_shaded_error_bar(x, sessions_summary.choice_bias, ...
            sessions_summary.choice_bias_bpci, para.colour_choice, faceAlpha);
        %pl2 = plot(x, session_summary.abortTrialRate, 'LineWidth',2, 'Color',para.colour_abortRate);
        yline(0.5, '--', "LineWidth",1);
        ylim(choice_ylims)
        xlim([min(x) max(x)]);
        ylabel('Choice Ratio Port 1 / Port 0', "FontSize",titleFontSize);

end