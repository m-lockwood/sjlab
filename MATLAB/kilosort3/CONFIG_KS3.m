function para = CONFIG_KS3

    % analysis params
    para.stack_channels = false;
    para.include_sync_line = false;

    % directory params
    para.output_folder = 'kilosort3_v3';
    para.chanMap_filename = 'chanMap_Npx2p0';

    % overwrite pre-existing analysis
    para.overwrite = false;

end