"""
save_quality_metrics.py

Description:
    This script is designed to give an overview of the quality of neuropixels data across 
    sessions, calculated from the output from spike sorting in Kilosort. The script iterates 
    through all sessions of a specified animal, extracting quality metrics for each session. 
    The metrics include various statistical measures of spike sorting quality, such as L-ratio, 
    isolation distance, and d-prime values. The results are saved for further analysis.

Usage:
    This script is intended to be run in a Python environment with the necessary dependencies 
    installed. It requires manual setting of the animal ID, base data folders, and other 
    configurations in 'save_quality_metrics_config.yaml. If overwrite is set to 'false', the script 
    will load any pre-existing sorting analyzer objects and quality metrics for the session. 
        NOTE: the configuration file 'save_quality_metrics_config.yaml must be in the same directory 
        as the script.

Dependencies:
    - spikeinterface: For handling spike data and calculating quality metrics.
    - numpy: For numerical operations.
    - matplotlib: For plotting (if needed).
    - pandas: For data manipulation and storage.
    - pathlib and os: For file and directory operations.
    - glob: For pattern matching in file paths.
    - yaml: For reading configuration files.

Configuration:
    Before running the script, ensure the following variables are correctly set in the config 
    file 'save_quality_metrics_config.yaml':
    - animal_ID: The ID of the animal being analyzed.
    - base_folder_data: The base folder where raw data is stored.
    - base_folder_data_analysis: The folder where analysis results will be saved.
    - kilosort_subfolder: The name of the subfolder containing Kilosort output.
    - qm_keystring, sa_keystring: Keystrings for naming output files.
    - overwrite: Whether to overwrite existing files, or load them if they exist.

Output:
    Key outputs:
    - metadata_all_sessions: master CSV file with summary metrics for all sessions., including:
        - session_ID: The ID of the session.
        - num_units: The number of units in the session.
        - num_spikes_total: The total number of spikes in the session.
        - l_ratio_average: The average L-ratio across units.
        - l_ratio_median: The median L-ratio across units.
        - isolation_distance_average: The average isolation distance across units.
        - isolation_distance_median: The median isolation distance across units.
        - d_prime_average: The average d-prime across units.
        - d_prime_median: The median d-prime across units.
    Intermediate variables:
    - session_quality_metrics: A CSV file containing quality metrics for each unit in a session, including:
        - unit_id: The ID of the unit.
        - num_spikes: The number of spikes in the unit.
        - firing_rate: The firing rate of the unit.
        - presence_ratio: The presence ratio of the unit.
        - isi_violation: The ISI violation of the unit.
        - amplitude_cutoff: The amplitude cutoff of the unit.
        - snr: The signal-to-noise ratio of the unit.
        - drift: The drift of the unit.
        - max_drift: The maximum drift of the unit.
        - cumulative_drift: The cumulative drift of the unit.
        - silhouette_score: The silhouette score of the unit.
        - isolation_distance: The isolation distance of the unit.
        - l_ratio: The L-ratio of the unit.
        - d_prime: The d-prime of the unit.
    - sorting_analyzer: The sorting analyzer object containing spike sorting information.

Author:
    Megan Lockwood, Github @m-lockwood
Date:
    12.06.2024
Version:
    1.0
"""

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
import yaml

#===========================================================================================================
# Load parameters from config file
#===========================================================================================================

# Get the directory of the current script
script_dir = Path(__file__).resolve().parent

# Construct the path to the configuration file relative to the script's parent directory
config_file_path = script_dir / 'save_quality_metrics_config.yaml'
print(config_file_path)

# Load the configuration file
with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)

# Extract parameters set in config file
animal_ID = config['animal_ID']
base_folder_data = config['base_folder_data']
base_folder_data_analysis = config['base_folder_data_analysis']
kilosort_subfolder = config['kilosort_subfolder']
qm_keystring = config['qm_keystring']
sa_keystring = config['sa_keystring']
overwrite = config['overwrite']

#===========================================================================================================
# Iterate through all sessions and save quality metrics
#===========================================================================================================

animal_folder = os.path.join(base_folder_data, animal_ID)
sessionList = [d for d in os.listdir(animal_folder) 
               if os.path.isdir(os.path.join(animal_folder, d)) 
               and glob.glob(os.path.join(animal_folder, d, '**',kilosort_subfolder,'**', 'amplitudes.npy'), 
                             recursive=True)]
print(sessionList)

# create empty metadata_all_sessions
metadata_all_sessions = pd.DataFrame(columns=[
    'session_ID', 
    'num_units', 
    'num_spikes_total', 
    'l_ratio_average', 
    'l_ratio_median', 
    'isolation_distance_average', 
    'isolation_distance_median', 
    'd_prime_average', 
    'd_prime_median'
])

# Iterate through all sessions saving quality metrics as intermediate variables
for session_ID in sessionList:
    print('Starting analysis of session ' + session_ID + ' for ' + animal_ID + '...')
    session_folder = os.path.join(animal_folder, session_ID)
    output_folder = os.path.join(session_folder, 'spikeinterface')

    # Path to Kilosort output files within session folder
    kilosort_folder = os.path.join(session_folder, kilosort_subfolder, 'sorter_output')

    # Get output from spike sorting using Kilosort, keeping only good units
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
        session_quality_metrics = pd.read_csv(os.path.join(output_folder, filename_qm))
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
        session_quality_metrics = sqm.compute_quality_metrics(sorting_analyzer, load_if_exists=None) 
        
        # Save quality metrics to a .csv file
        filename_qm = qm_keystring+'_'+session_ID+'.csv'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        session_quality_metrics.to_csv(os.path.join(output_folder, filename_qm))

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
    l_ratio_average = session_quality_metrics['l_ratio'].mean()
    l_ratio_median = session_quality_metrics['l_ratio'].median()
    isolation_distance_average = session_quality_metrics['isolation_distance'].mean()
    isolation_distance_median = session_quality_metrics['isolation_distance'].median()
    d_prime_average = session_quality_metrics['d_prime'].mean()
    d_prime_median = session_quality_metrics['d_prime'].median()

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
metadata_all_sessions.to_csv(os.path.join(output_folder_metadata, qm_keystring + '_metadata_' + animal_ID + '.csv'), index=False)