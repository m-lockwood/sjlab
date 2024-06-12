import spikeinterface.core as sc
import spikeinterface.extractors as se
import spikeinterface.qualitymetrics as sqm
import spikeinterface.widgets as sw

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import os
import glob

############################################################################################################
animal_ID = 'FNT099'
base_folder_data = r"W:\projects\FlexiVexi\behavioural_data"
base_folder_data_analysis = r"C:\Users\megan\Documents\sjlab\flexible-navigation-task\Data Analysis\v0p1p1"
kilosort_subfolder = 'kilosort3_v3'
qm_keystring = 'quality_metrics'
sa_keystring = 'sorting_analyzer'
overwrite=False
############################################################################################################

animal_folder = os.path.join(base_folder_data, animal_ID)
sessionList = [d for d in os.listdir(animal_folder) 
               if os.path.isdir(os.path.join(animal_folder, d)) 
               and glob.glob(os.path.join(animal_folder, d, '**',kilosort_subfolder, 'amplitudes.npy'), recursive=True)]
print(sessionList)

# create empty metadata_all_sessions
metadata_all_sessions = pd.DataFrame(columns=['session_ID', 'num_units', 'num_spikes_total', 'l_ratio_average', 'l_ratio_median', 'isolation_distance_average', 'isolation_distance_median', 'd_prime_average', 'd_prime_median'])

# Iterate through all sessions saving quality metrics as intermediate variables
for session_ID in sessionList:
    print('Starting analysis of session ' + session_ID + ' for ' + animal_ID + '...')
    session_folder = os.path.join(animal_folder, session_ID)
    output_folder = os.path.join(session_folder, 'spikeinterface')

    # Path to Kilosort3 output files within session folder
    kilosort_folder = os.path.join(session_folder, kilosort_subfolder)

    # Get output from spike sorting using Kilosort3, keeping only good units
    sorting_KS = se.read_kilosort(folder_path=kilosort_folder,keep_good_only=True)
    print(sorting_KS)

    # Get path to Open-Ephys Record Node within session folder
    matching_files = glob.glob(os.path.join(session_folder, '**', 'settings.xml'), recursive=True)
    if matching_files:
        # Get the first matching file
        first_matching_file = matching_files[0]

        # Get the directory of the first matching file
        path_to_recording = os.path.dirname(first_matching_file)
    else:
        print("No 'settings.xml' file found in the specified path.")
        
    # Get recording from open ephys
    recording = se.read_openephys(folder_path=path_to_recording, stream_name = 'Record Node 102#Neuropix-PXI-100.ProbeA')

    # Get Sorting Analyzer

    output_folder = os.path.join(session_folder, 'spikeinterface')

    if os.path.exists(os.path.join(output_folder, sa_keystring)) and overwrite==False:

        # load sorting analyzer from file
        sorting_analyzer = sc.load_sorting_analyzer(folder=os.path.join(output_folder, sa_keystring))
        print('Loaded Sorting Analyzer from ' + os.path.join(output_folder, sa_keystring) + '.')
        
        # load qm from file
        filename_qm = qm_keystring+'_'+session_ID+'.csv'
        qm = pd.read_csv(os.path.join(output_folder, filename_qm))
        print('Loaded quality metrics from ' + os.path.join(output_folder, filename_qm) + '.')

    else:
        print('Creating sorting analyzer for ' + session_ID)
        # Create a sorting analyzer
        sorting_analyzer = sc.create_sorting_analyzer(sorting_KS, recording)

        # Compute sorting analyzer info
        sorting_analyzer.compute("random_spikes")
        sorting_analyzer.compute("waveforms")

        sorting_analyzer.compute("templates")
        sorting_analyzer.compute("noise_levels")
        all_pcs = sorting_analyzer.compute("principal_components")

        all_pcs = sorting_analyzer.get_extension('principal_components').get_data()
        sorting_analyzer.get_extension('templates').get_data()

        # Save sorting analyzer to a .pkl file
        sorting_analyzer = sorting_analyzer.save_as(format="binary_folder",folder=os.path.join(output_folder, sa_keystring)) 

        # depends on "waveforms", "templates", "noise_levels", and "pca" (if computing pca metrics)
        print('Computing quality metrics for ' + session_ID)
        qm = sqm.compute_quality_metrics(sorting_analyzer, load_if_exists=None) 
        
        # Save quality metrics to a .csv file
        filename_qm = qm_keystring+'_'+session_ID+'.csv'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        qm.to_csv(os.path.join(output_folder, filename_qm))

    # append session meta-data to table

    ## Get recording metadata
    #num_channels = recording.get_num_channels()
    #reference_channels = recording.get_reference_channels()
    #channel_config = recording.get_channel_groups()

    ## get sorting metadata
    num_units = se.KiloSortSortingExtractor.get_num_units(sorting_KS)
    num_spikes_per_unit = se.KiloSortSortingExtractor.count_num_spikes_per_unit(sorting_KS)
    num_spikes_total = sum(num_spikes_per_unit)

    ## get QM metadata
    l_ratio_average = qm['l_ratio'].mean()
    l_ratio_median = qm['l_ratio'].median()
    isolation_distance_average = qm['isolation_distance'].mean()
    isolation_distance_median = qm['isolation_distance'].median()
    d_prime_average = qm['d_prime'].mean()
    d_prime_median = qm['d_prime'].median()

    # Append QM metadata to session metadata table
    metadata_session = pd.DataFrame({'session_ID': [session_ID],
                                     'num_units': [num_units],
                                     'num_spikes_total': [num_spikes_total],
                                     'l_ratio_average': [l_ratio_average],
                                     'l_ratio_median': [l_ratio_median],
                                     'isolation_distance_average': [isolation_distance_average],
                                     'isolation_distance_median': [isolation_distance_median],
                                     'd_prime_average': [d_prime_average],
                                     'd_prime_median': [d_prime_median]})
    metadata_all_sessions = pd.concat([metadata_all_sessions, metadata_session])
    metadata_all_sessions.reset_index(drop=True, inplace=True)
    print('Finished analysis of session ' + session_ID + ' for ' + animal_ID + '.')

# Save metadata to data analysis folder
output_folder_metadata = os.path.join(base_folder_data_analysis, 'ephys_signal_quality')
if not os.path.exists(output_folder_metadata):
    os.makedirs(output_folder_metadata)
metadata_all_sessions.to_csv(os.path.join(output_folder_metadata, 'ephys_signal_quality_metadata_' + animal_ID + '.csv'), index=False)