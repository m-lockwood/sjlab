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

#######################################################################
animal_ID = '98'

base_folder = r"W:\projects\FlexiVexi\behavioural_data"
#######################################################################

animal_folder = os.path.join(base_folder, animal_ID)
sessionList = [d for d in os.listdir(animal_folder) 
               if os.path.isdir(os.path.join(animal_folder, d)) 
               and glob.glob(os.path.join(animal_folder, d, '**', 'amplitudes.npy'), recursive=True)]
print(sessionList)

for session_ID in sessionList:
    session_folder = os.path.join(animal_folder, session_ID)

    # Path to Kilosort3 output files within session folder
    kilosort_folder = os.path.join(session_folder, 'kilosort3')

    # Get output from spike sorting using Kilosort3, keeping only good units
    sorting_KS = se.read_kilosort(folder_path=kilosort_folder,keep_good_only=False)
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

    # depends on "waveforms", "templates", "noise_levels", and "pca" (if computing pca metrics)
    qm = sqm.compute_quality_metrics(sorting_analyzer, load_if_exists=None) 

    # Save quality metrics to a .csv file
    output_folder = os.path.join(session_folder, 'spikeinterface')
    filename = 'quality_metrics_'+session_ID+'.csv'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    qm.to_csv(os.path.join(output_folder, filename))