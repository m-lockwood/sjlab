"""
Description:
    This script is designed to run spike sorting across all sessions for a given animal using Kilosort.
    It utilizes the spikeinterface library to preprocess the data, run the sorting algorithm, and manage the outputs.

Python dependencies:
- spikeinterface
- yaml
- os
- glob

Prerequisites:
- The spikeinterface library and its dependencies are installed.
- Kilosort (version 2.5 or 3) is installed and configured properly on the system. This can be done via cloning the 
    Kilosort (https://github.com/MouseLand/Kilosort) and following the instructions in the README. To create local 
    directories containing distinct versions of Kilosort, this can be achieved by cloning the repository into two 
    separate directories and using 'git checkout <kilosort version>' to switch between versions.
- An external .xlsx file containing a list of sessions to be analyzed is present in the same directory as this script.
- A configuration file named 'run_kilosort_config.yaml' is present in the same directory as this script,
  specifying necessary parameters such as the animal ID, the base folder for data, and the filepaths pointing 
  towards the relevant Kilosort code and the external .xlsx file containing a list of sessions to be analyzed.

Inputs:
- The script reads the configuration file 'run_kilosort_config.yaml' to obtain the necessary parameters.
- The script requires raw OpenEphys data to be present in the specified data repository. The data should be organized such 
    that each session folder contains the raw OpenEphys data files (of the form 'continuous.dat').
- The script reads an external .xlsx file containing a list of sessions to be analyzed. This file should contain the collumns
    'Animal_ID' and 'Session_ID' specifying the animal and session IDs, respectively. The name of this .xlsx file should be 
    specified in the configuration file.

Outputs:
- The script will output sorted spike data into specified subdirectories within the session folder of the data repository 
    (containing raw OpenEphys data). The output folders will be named 'Kilosort2_5' or 'Kilosort3' depending on the version 
    specified in the configuration file.
    based on the configuration.
"""


from spikeinterface.preprocessing import phase_shift, bandpass_filter, common_reference
from spikeinterface.sorters import run_sorter
from pathlib import Path
import pandas as pd
import os
from spikeinterface.sorters import Kilosort3Sorter
from spikeinterface.sorters import Kilosort2_5Sorter
import yaml

# import custom functions
import spikeinterface_utils as su


#===========================================================================================================
# Load parameters from config file
#===========================================================================================================

# Get the directory of the current script
script_dir = Path(__file__).resolve().parent

# Construct the path to the configuration file relative to the script's parent directory
config_file_path = script_dir / 'run_kilosort_config.yaml'
print(config_file_path)

# Load the configuration file
with open(config_file_path, 'r') as file:
    config = yaml.safe_load(file)

animal_ID = config['animal_ID']
base_folder_data = config['base_folder_data']

#===========================================================================================================
# Main script: run Kilosort on all sessions specified in an external .xlsx file
#===========================================================================================================

sessions_list_df = pd.read_excel(config['sessions_list_filepath'])

for session_idx, row in sessions_list_df.iterrows():
    
    # This reads OpenEphys 'Binary' format.
    session_ID = row["Session_ID"]
    animal_ID = row["Animal_ID"]

    print(f"Start analyzing session {session_idx+1} of {len(sessions_list_df)}: {animal_ID}/{session_ID} ")
    
    #-----------------------------------------------------------------------------------------
    # Load and pre-process the data
    #-----------------------------------------------------------------------------------------

    # replace first two characters (e.g. 'W:') with '/ceph/sjones'
    session_folder = os.path.join(root_dir, animal_ID, session_ID)
    raw_recording = su.get_raw_recording(session_folder)

    # Run the preprocessing steps.
    if raw_recording is None:
        print(f"No raw recording found.")
    else:
        shifted_recording = phase_shift(raw_recording)
        filtered_recording = bandpass_filter(shifted_recording, freq_min=300, freq_max=6000)
        preprocessed_recording = common_reference(
            filtered_recording, reference="global", operator="median"
    )

   #-----------------------------------------------------------------------------------------
    # Run Kilosort
    #-----------------------------------------------------------------------------------------

    if config['kilosort_version'] == 3:

        # Set path to kilosort 3 code
        Kilosort3Sorter.set_kilosort3_path(config['Kilosort3_path'])

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

    elif config['kilosort_version'] == 2.5:

        # Set path to kilosort 2.5 code
        Kilosort2_5Sorter.set_kilosort2_5_path(config['Kilosort2_5_path'])

        # Check if the Kilosort 2.5 output folder and preprocessed recording exist
        if (not os.path.exists(os.path.join(session_folder, "Kilosort2_5"))) and \
        ('preprocessed_recording' in locals()):
            print('Starting Kilosort2.5 spike sorting...')
            # Run Kilosort2.5 spike sorting 
            sorting = run_sorter(
                "kilosort2_5",
                preprocessed_recording,
                output_folder=(os.path.join(session_folder,"Kilosort2_5")),
                car=False,
                freq_min=150,
            )
            print('Finished Kilosort2.5 spike sorting.')
        elif os.path.exists(os.path.join(session_folder, "Kilosort2_5")):
            print('Kilosort2.5 output folder already exists. Skipping Kilosort2.5 spike sorting.')
        elif not ('preprocessed_recording' in locals()):
            print('No preprocessed recording found. Skipping Kilosort2.5 spike sorting.')