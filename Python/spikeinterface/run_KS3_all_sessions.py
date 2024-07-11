# Dependencies: spikeinterface, probeinterface, matplotlib, scipy
print('Run script for KS2.5 and KS3 spike sorting')
from spikeinterface.preprocessing import phase_shift, bandpass_filter, common_reference
from spikeinterface.sorters import run_sorter
from pathlib import Path
import pandas as pd
import os
import glob
from spikeinterface.sorters import Kilosort3Sorter
from spikeinterface.sorters import Kilosort2_5Sorter
import sys

# import custom functions
import spikeinterface_utils as su

# -----------------------------------------------------------------------------
# Section 0: Define directory and analysis params
# -----------------------------------------------------------------------------

# Set path to spike sorters
Kilosort2_5Sorter.set_kilosort2_5_path(r"C:\Users\megan\Documents\GitHub\Kilosort25")
Kilosort3Sorter.set_kilosort3_path(r"C:\Users\megan\Documents\GitHub\Kilosort3")

root_dir = Path(
    r"W:\projects\FlexiVexi\behavioural_data"
)

animal_ID = 'FNT099'

# List all session folders within root_dir which contain raw OpenEphys data
animal_folder = os.path.join(root_dir, animal_ID)
sessionList = [d for d in os.listdir(animal_folder) 
               if os.path.isdir(os.path.join(animal_folder, d)) 
               and glob.glob(os.path.join(animal_folder, d, '**', 'continuous.dat'), 
                             recursive=True)]

for session_idx, session_ID in enumerate(sessionList):
    
    print(f"Start analyzing session {session_idx+1} of {len(sessionList)}: {animal_ID}/{session_ID} ")
    
    #-----------------------------------------------------------------------------------------
    # Load and pre-process the data
    #-----------------------------------------------------------------------------------------

    # replace first two characters (e.g. 'W:') with '/ceph/sjones'
    session_folder = os.path.join(root_dir, animal_ID, session_ID)
    raw_recording = su.get_raw_recording(session_folder)

    # Run the preprocessing steps.
    shifted_recording = phase_shift(raw_recording)
    filtered_recording = bandpass_filter(shifted_recording, freq_min=300, freq_max=6000)
    preprocessed_recording = common_reference(
        filtered_recording, reference="global", operator="median"
    )

    #-----------------------------------------------------------------------------------------
    # Run Kilosort 3
    #-----------------------------------------------------------------------------------------

    # Check if the Kilosort 3 output folder and preprocessed recording exist
    if (not os.path.exists(os.path.join(session_folder, "Kilosort3"))) and \
       ('preprocessed_recording' in locals()):
        print('Starting Kilosort3 spike sorting...')
        # Run Kilosort3 spike sorting 
        sorting = run_sorter(
            "kilosort3",
            preprocessed_recording,
            output_folder=(os.path.join(session_folder,"Kilosort3")),
            car=False,
            freq_min=150,
        )
        print('Finished Kilosort3 spike sorting.')
    elif os.path.exists(os.path.join(session_folder, "Kilosort3")):
        print('Kilosort3 output folder already exists. Skipping Kilosort3 spike sorting.')
    elif not ('preprocessed_recording' in locals()):
        print('No preprocessed recording found. Skipping Kilosort3 spike sorting.')