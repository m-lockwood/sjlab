function [xCoord, yCoord] = XYCoord20(elecInd)


    nElec = 1280;   % per shank; pattern repeats for the four shanks
    vSep  = 15;     % in um
    hSep  = 32;

    elecPos = zeros(nElec, 2);

    elecPos(1:2:end,1) = 0;         % sites 0,2,4...
    elecPos(2:2:end,1) = hSep;      % sites 1,3,5...

    % fill in y values
    viHalf = (0:(nElec/2-1))';                % row numbers
    elecPos(1:2:end,2) = viHalf * vSep;       % sites 0,2,4...
    elecPos(2:2:end,2) = elecPos(1:2:end,2);  % sites 1,3,5...

    xCoord = elecPos(elecInd+1,1);
    yCoord = elecPos(elecInd+1,2);

    % four shank probe, no multiple connections
    figure(1)
    shankSep = 250;
    for sI = 0:3
        cc = find(shankind == sI);
        scatter( shankSep*sI + elecPos(:,1), elecPos(:,2), 30, 'k', 'square' ); hold on;
        scatter( shankSep*sI + xCoord(cc), yCoord(cc), 20, 'b', 'square', 'filled' ); hold on;
    end
    xlim([-16,3*shankSep+64]);
    ylim([-10,10000]);
    title('NP2.0 MS shank view');
    hold off;
