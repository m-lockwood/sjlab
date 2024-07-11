import pandas as pd
import numpy as np
import os
import glob
import spikeinterface.extractors as se

# -----------------------------------------------------------------------------
# Open Ephys utils
# -----------------------------------------------------------------------------

# Get dot onset and offset times given by TTL pulses
def get_raw_recording(session_folder, npx_stream_name = 'Record Node 102#Neuropix-PXI-100.ProbeA'):

    # Get path to Open-Ephys Record Node within session folder
    matching_files = glob.glob(os.path.join(session_folder, '**', 'settings.xml'), recursive=True)
    if matching_files:
        # Get the first matching file
        first_matching_file = matching_files[0]

        # Get the directory of the first matching file
        path_to_recording = os.path.dirname(first_matching_file)

        # Get recording from open ephys
        recording = se.read_openephys(folder_path=path_to_recording, stream_name = npx_stream_name)
    else:
        print("No 'settings.xml' file found in the specified path.")
        recording = None
    
    return(recording)