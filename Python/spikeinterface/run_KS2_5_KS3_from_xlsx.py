"""
run_KS2_5_KS3_from_xlsx.py

Description:
    This script is designed to automate the spike sorting process for neural data using Kilosort2.5 and Kilosort3 algorithms. 
    It reads session data from an Excel file, performs preprocessing steps, and then runs the specified spike sorter on each session.

Dependencies:
    - spikeinterface: For handling spike sorting workflows.
    - probeinterface: For probe information handling.
    - matplotlib: For plotting and visualization.
    - scipy: For scientific computing and technical computing.
    - pandas: For data manipulation and analysis.
    - os: For operating system dependent functionality.
    - pathlib: For object-oriented filesystem paths.

Usage:
    Ensure all dependencies are installed and paths to Kilosort2.5 and Kilosort3 are correctly set.
    Run the script in an environment where all dependencies are available.
    The script expects a path to an Excel file containing session information under 'good_sessions_filepath'.

Input:
    An Excel file located at 'good_sessions_filepath' with at least the following columns:
    - session_folder_ceph: Path to the session's data folder.

Output:
    The script will output the results of the spike sorting process for each session listed in the Excel file.
    Results include sorted spike data and potentially figures or logs, depending on the configuration of the spike sorters.

Author:
    Megan Lockwood, Github @m-lockwood
Date:
    10.06.2024
Version:
    1.0

Notes:
    - This script is configured for Windows paths. Adjustments may be needed for other operating systems.
    - Ensure that the paths to Kilosort2.5 and Kilosort3 are accessible and correctly set in the script.
"""

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

#=================================================================================================
good_sessions_filepath = Path(
    r"W:/projects/FlexiVexi/Data Analysis/intermediate_variables/good_sessions.xlsx"
)
good_sessions = pd.read_excel(good_sessions_filepath)

# Set paths to spike sorters
Kilosort2_5Sorter.set_kilosort2_5_path(r"C:/Users/megan/Documents/GitHub/Kilosort25")
Kilosort3Sorter.set_kilosort3_path(r"C:/Users/megan/Documents/GitHub/Kilosort3")

#=================================================================================================

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