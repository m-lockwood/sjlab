from kilosort import run_kilosort
from kilosort import io
import numpy as np
import os
import glob
import spikeinterface.extractors as se
from probeinterface import ProbeGroup, write_prb
from probeinterface.plotting import plot_probe

###############################################################################
animal_ID = 'FNT098'
session_ID = '2024-04-11T10-45-54'

base_folder = r"Z:\projects\FlexiVexi\behavioural_data"
session_folder = os.path.join(base_folder, animal_ID, session_ID)
output_folder = os.path.join(session_folder, 'kilosort4')

###############################################################################

# ANALYSIS PARAMS
n_chan_bin = 384
fs = 30000

###############################################################################

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

# get probe
probe = recording.get_probe()
pg = ProbeGroup()
pg.add_probe(probe)

# Write probe file
print(os.path.join(output_folder, 'probe.prb'))
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
write_prb(os.path.join(output_folder, 'probe.prb'), pg)

# Convert raw data to binary
dtype = np.int16
filename, N, c, s, fs, probe_path = io.spikeinterface_to_binary(
    recording, output_folder, data_name='data.bin', dtype=dtype,
    chunksize=60000, export_probe=True, probe_name='probe.prb'
    )

# NOTE: 'n_chan_bin' is a required setting, and should reflect the total number
#       of channels in the binary file, while probe['n_chans'] should reflect
#       the number of channels that contain ephys data. In many cases these will
#       be the same, but not always. For example, neuropixels data often contains
#       385 channels, where 384 channels are for ephys traces and 1 channel is
#       for some other variable. In that case, you would specify
#       'n_chan_bin': 385.
settings = {'fs': fs, 'n_chan_bin': n_chan_bin, 'dminx': 350}
# NOTE: set 'dminx' to half total probe width to address issue with multiple shanks 
#       in kilsort4 (https://kilosort.readthedocs.io/en/stable/multi_shank.html)

# Specify probe configuration.
assert probe_path is not None, 'No probe information exported by SpikeInterface'
probe_path = os.path.join(output_folder, 'probe.prb')
probe = io.load_probe(probe_path)

# This command will both run the spike-sorting analysis and save the results to
# `DATA_DIRECTORY`.
ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate = run_kilosort(
    settings=settings, probe=probe, filename=filename
    )