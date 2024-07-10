# Dependencies: spikeinterface, probeinterface, matplotlib, scipy
print('Run script for KS2.5 and KS3 spike sorting')
from spikeinterface.preprocessing import phase_shift, bandpass_filter, common_reference
from spikeinterface.sorters import run_sorter
from pathlib import Path
import pandas as pd
import os
from spikeinterface.sorters import Kilosort3Sorter
from spikeinterface.sorters import Kilosort2_5Sorter

# import custom functions
import spikeinterface_utils as su

##############################################################################################
good_sessions_filepath = Path(
    r"W:/projects/FlexiVexi/Data Analysis/intermediate_variables/good_sessions.xlsx"
)
good_sessions = pd.read_excel(good_sessions_filepath)

# Set paths to spike sorters
Kilosort2_5Sorter.set_kilosort2_5_path(r"C:/Users/megan/Documents/GitHub/Kilosort25")
Kilosort3Sorter.set_kilosort3_path(r"C:/Users/megan/Documents/GitHub/Kilosort3")

##############################################################################################

for session_idx, row in good_sessions.iterrows():
    print(f"Start analyzing session {session_idx+1} of {len(good_sessions)}: {row['session_folder_ceph']}...")
    #-----------------------------------------------------------------------------------------
    # Pre-process the data
    #-----------------------------------------------------------------------------------------

    # This reads OpenEphys 'Binary' format.
    session_folder = row["session_folder_ceph"]
    raw_recording = su.get_raw_recording(session_folder)

    # Run the preprocessing steps.
    shifted_recording = phase_shift(raw_recording)
    filtered_recording = bandpass_filter(shifted_recording, freq_min=300, freq_max=6000)
    preprocessed_recording = common_reference(
        filtered_recording, reference="global", operator="median"
    )

    #-----------------------------------------------------------------------------------------
    # Run Kilosort 2.5
    #-----------------------------------------------------------------------------------------

    print('Starting Kilosort2.5 spike sorting...')
    if not os.path.exists(os.path.join(session_folder,"kilosort2_5")):
        # Run Kilosort2.5 spike sorting
        sorting = run_sorter(
            "kilosort2_5",
            preprocessed_recording,
            output_folder=(os.path.join(session_folder,"kilosort2_5")),
            car=False,
            freq_min=150,
        )
    else:
        print('Kilosort2.5 output folder already exists. Skipping Kilosort2.5 spike sorting...')

    print('Finished Kilosort25 spike sorting...')

    #-----------------------------------------------------------------------------------------
    # Run Kilosort 3
    #-----------------------------------------------------------------------------------------

    print('Starting Kilosort3 spike sorting...')

    # Check if the Kilosort 3 output folder exists
    if not os.path.exists(os.path.join(session_folder,"kilosort3")):
        # Run Kilosort3 spike sorting 
        sorting = run_sorter(
            "kilosort3",
            preprocessed_recording,
            output_folder=(os.path.join(session_folder,"kilosort3")),
            car=False,
            freq_min=150,
        )
    else:
        print('Kilosort3 output folder already exists. Skipping Kilosort3 spike sorting...')

    print('Finished Kilosort3 spike sorting...')