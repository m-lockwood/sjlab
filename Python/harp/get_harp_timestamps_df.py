import numpy as np
import harp
import pandas as pd
from harp.model import Model, Register, Access
import os
import matplotlib.pyplot as plt

# Import custom functions
import harp_utils as hu
                
# -----------------------------------------------------------------------------
# Section 0: Define directory and analysis params
# -----------------------------------------------------------------------------

# Define animal and session ID
animal_ID = 'FNT098'
session_ID = '2024-03-19T13-15-30'

# path behavioural data on Ceph repo
input_dir = r"W:\projects\FlexiVexi\behavioural_data" 
output_dir = (r"C:\Users\megan\Documents\sjlab\flexible-navigation-task" +
              r"\Data Analysis\intermediate_variables")

# Specify mapping from sound index to reward port
soundIdx0 = 14
soundIdx1 = 10
soundOffIdx = 18

# -----------------------------------------------------------------------------
# Section 1: Import data
# -----------------------------------------------------------------------------

# Create reader for behavior.
bin_b_path = os.path.join(input_dir, animal_ID, session_ID, "Behavior.harp")
## print debug info
behaviour_reader = harp.create_reader(bin_b_path)

# Create reader for sound card.
# NOTE: explicitly defined model will be deprecated or redundant in future
bin_s_path = os.path.join(input_dir, animal_ID, session_ID, "SoundCard.harp", "SoundCard_32.bin")
model = Model(
    device='Soundcard', 
    whoAmI=1280,
    firmwareVersion='2.2',
    hardwareTargets='1.1',
    registers={
        'PlaySoundOrFrequency': Register(
            address=32, 
            type="U16", 
            access=Access.Event
        )
    }
)
sound_reader = harp.create_reader(model, keep_type=True)


# Import behavioural data as data frame
session_path = os.path.join(input_dir, animal_ID, session_ID)
filepath = os.path.join(session_path, 'Experimental-data', \
                        session_ID + '_experimental-data.csv')
df_trials = pd.read_csv(filepath)

# -----------------------------------------------------------------------------
# Section 2: Create data frame df_trials with trial summary info and 
#            harp timestamps
# -----------------------------------------------------------------------------

# Get dot onset and offset times given by TTL pulses
ttl_state_df = hu.get_ttl_state_df(behaviour_reader)
first_dot_onset_time = df_trials['DotOnsetTime'].iloc[0]
dot_times_ttl = hu.get_dot_times_from_ttl(ttl_state_df, first_dot_onset_time)
df_trials = pd.concat([df_trials, dot_times_ttl], axis=1)

# Get all pokes within each trial
trial_pokes_df = hu.parse_trials_pokes(df_trials, behaviour_reader, ignore_dummy_port=True)
df_trials = pd.concat([df_trials, trial_pokes_df], axis=1)

# Get timestamp of all port choices within each trial
port_choice = hu.get_port_choice(df_trials, behaviour_reader)
df_trials = pd.concat([df_trials, port_choice], axis=1)

# Get timestamp of all sound onsets and offsets within each trial
trial_sounds_df = hu.get_all_sounds(df_trials, sound_reader, bin_s_path)
df_trials = pd.concat([df_trials, trial_sounds_df], axis=1)

# Save df_trials as pickle file
df_trials.to_pickle(os.path.join(output_dir, animal_ID, session_ID + '_trial_data_harp.pkl'))