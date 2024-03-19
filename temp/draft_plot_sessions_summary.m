clc
close all
clear

%% CONFIG

% Analysis params
output_folder = ['C:\Users\megan\Documents\sjlab\flexible-navigation-task\' ...
    'Data Analysis'];
Animal_ID = "98";

% Plot params
plot_dayNum = false; % determines whether to plot data against date or session number
plot_errorbars = false; % determines whether to plot error bars
titleFontSize=16;
faceAlpha = 0.15;
accuracy_ylims = [0.2 1];
choice_ylims = [0 1];

para.colour_accuracy = [0.4660 0.6740 0.1880];
para.colour_choice = [0 0.4470 0.7410];
para.colour_abortRate = [0.9290 0.6940 0.1250];

%% define plot
session_summary = read_session_summary(output_folder, Animal_ID);

fig = figure('Visible','on', 'Position', [278 79 928 883]);
tl = tiledlayout(2,1);
tl.Padding = "compact";

title(tl,[strcat("Mouse ", Animal_ID, " Session Summary Data") ""], "FontSize", titleFontSize+2);
xlabel(tl, 'Days since training started', "FontSize",titleFontSize);

% define x-axis data
if plot_dayNum
    dayNum = (session_summary.Session_ID');
    dayNum = datenum(dayNum, 'yyyy-mm-dd');
    dayNum = dayNum-dayNum(1);
    x = dayNum;
else
    x = 1:height(session_summary);
    x = x';
end

%% plot accuracy of all non-aborted trials
ax1 = nexttile;
    hold on;
    title(ax1, 'Plot performance over sessions', 'FontSize',titleFontSize)
    pl1 = plot_shaded_error_bar(x, session_summary.accuracy_completed_trials, ...
        session_summary.accuracy_completed_trials_bpci, para.colour_accuracy, faceAlpha);
    pl2 = plot(x, session_summary.accuracy_all_trials, 'LineWidth', 2, 'Color', ...
        para.colour_accuracy, 'LineStyle','--');
    yline(0.5, '--', "LineWidth",1);
    ylim(accuracy_ylims)
    xlim([min(x) max(x)]);
    ylabel('Fraction of Correct Trials', "FontSize",titleFontSize);
    legend([pl1 pl2], {'Fraction of Completed Trials', 'Fraction of All Trials'}, ...
        'FontSize', titleFontSize, 'Location','southeast');

%% plot choice bias on all non-aborted trials (for which choice was port 0 or port 1)

ax2 = nexttile;
    hold on;
    title(ax2, 'Plot choice bias over sessions', 'FontSize',titleFontSize);
    pl1 = plot_shaded_error_bar(x, session_summary.choice_bias, ...
        session_summary.choice_bias_bpci, para.colour_choice, faceAlpha);
    %pl2 = plot(x, session_summary.abortTrialRate, 'LineWidth',2, 'Color',para.colour_abortRate);
    yline(0.5, '--', "LineWidth",1);
    ylim(choice_ylims)
    xlim([min(x) max(x)]);
    ylabel('Choice Ratio Port 1 / Port 0', "FontSize",titleFontSize);

%% save plot
filename = strcat('plot_session_summary_', Animal_ID);
%save_figure(fig, output_folder, filename);