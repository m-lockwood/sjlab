import pandas as pd
import numpy as np

# -----------------------------------------------------------------------------
# General utils
# -----------------------------------------------------------------------------

# Retrieve trial start times based on either
#  - audio cues (for stage 5), or
#  - dot onset times (for stage 4)
def get_trial_start_times(stage, **kwargs):

    """
    Retrieve trial start times based on the specified stage.

    Parameters:
    stage (int): The stage of the trial. Only stages 4 and 5 are supported.
        - Stage 4: Requires 'dot_onset_times' in kwargs.
        - Stage 5: Requires 'bin_sound_path' and 'sound_reader' in kwargs.
    **kwargs: Additional keyword arguments required based on the stage.
        - dot_onset_times (list or array-like): Onset times of dots for stage 4.
        - bin_sound_path (str): Path to the binary sound file for stage 5.
        - sound_reader (callable): Function to read the sound file for stage 5.

    Returns:
    pd.Series: A series of trial start times.

    Raises:
    ValueError: If required arguments for the specified stage are not provided or if an invalid stage is specified.

    Notes:
    - For stage 4, the function directly returns the provided 'dot_onset_times'.
    - For stage 5, the function processes the sound events to derive trial start times.
      It removes events for playing silence and considers the start of each audio cue as the trial start time.
    - There might be a need to introduce a check for trials in stage 5 where the sound starts playing but the trial is not completed. In such cases, the last trial should be discarded.
    """

    if stage == 4:
        dot_onset_times = kwargs.get('dot_onset_times')
        if dot_onset_times is None:
            raise ValueError("Stage 4 requires 'dot_onset_times' argument.")
        # Process dot onset and offset times
        trial_start_times = dot_onset_times
        return trial_start_times

    elif stage == 5:
        bin_sound_path = kwargs.get('bin_sound_path')
        sound_reader = kwargs.get('sound_reader')
        if bin_sound_path is None or sound_reader is None:
            raise ValueError("Stage 5 requires 'bin_sound_path' and 'sound_reader' arguments.")
        # Derive the sound of all audio events
        sound_of_all_audio_events = sound_reader(bin_sound_path)
        print(f"Processing stage 5 with sound_of_all_audio_events: {sound_of_all_audio_events}")
        all_sounds = hu.get_all_sounds(sound_reader, bin_sound_path)
        # remove events for playing silence
        all_sounds = all_sounds[all_sounds['PlaySoundOrFrequency'] != soundOffIdx]
        # take trial start time is the start of each audio (since there is one audio cue per trial)
        trial_start_times = all_sounds['timestamp']
        # NOTE: might need to introduce a check for trials in stage 5 where the sound starts playing 
        # but the trial is not completed. In this case we should discard the last trial.
        return trial_start_times
    else:
        raise ValueError("Invalid stage. Only stages 4 and 5 are supported.")

# -----------------------------------------------------------------------------
# TTL utils
# -----------------------------------------------------------------------------

# Get a data frame with timestamps of all instances of initiating and 
# terminating a TTL pulse
def get_ttl_state_df(behavior_reader):

  # Get data frame with timestamps of all instances of initiating TTL pulse
    ttl_on  = behavior_reader.OutputSet.read(keep_type=True)['DO2']
    ttl_on = ttl_on[ttl_on==True]
    ttl_on_df = pd.DataFrame({
        'timestamp': ttl_on.index,
        'state': 1
    })

    # Get data frame with timestamps of all instances of terminating a TTL pulse
    ttl_off = behavior_reader.OutputClear.read(keep_type=True)['DO2']
    ttl_off = ttl_off[ttl_off==True]
    ttl_off_df = pd.DataFrame({
        'timestamp': ttl_off.index,
        'state': 0
    })

    # Concatenate data frames into single stream of events describing state of TTL
    ttl_state_df = pd.concat([ttl_on_df,ttl_off_df], ignore_index=True)
    ttl_state_df = ttl_state_df.sort_values(by='timestamp')
    ttl_state_df = ttl_state_df.reset_index(drop=True)
    
    return ttl_state_df

# Get dot onset and offset times given by TTL pulses
def get_dot_times_from_ttl(behavior_reader,t0):
    
    ttl_state_df = get_ttl_state_df(behavior_reader)
    ## Find index of TTL timestamp closest to the first dot_onset_time in df_trials
    idx = (np.abs(ttl_state_df['timestamp'] - t0)).idxmin()

    ## Remove all TTL pulses that occur before the index found above
    ttl_state_df = ttl_state_df.iloc[idx:]

    ## Remove last rows such that df has a length that is a multiple of 6
    n = len(ttl_state_df) % 6
    ttl_state_df = ttl_state_df.iloc[:-n]
    
    dot_times_ttl = pd.DataFrame({
        'DotOnsetTime_ttl': ttl_state_df['timestamp'].iloc[::6].tolist(),
        'DotOffsetTime_ttl': ttl_state_df['timestamp'].iloc[2::6].tolist()
    })
    return(dot_times_ttl)

def get_square_wave(df): 

    # Create a new DataFrame with repeated elements
    square_wave = {'timestamp': df['timestamp'].repeat(2).tolist()[1:],
        'state': df['state'].repeat(2).tolist()[:-1]
        }
    square_wave = pd.DataFrame(square_wave)
    return square_wave

# -----------------------------------------------------------------------------
# Nose poke utils
# -----------------------------------------------------------------------------

# Get a data frame 'all_pokes' with the timestamp of all nosepoke events in the 
# behavior harp stream. This includes the timestamps and IDs of entering and 
# exiting a nose port, denoted by True and False, respectively.

def get_all_pokes(behavior_reader, ignore_dummy_port=True):

    # Read the behavior harp stream, Digital Input states for the nosepoke 
    # timestamps and IDs.
    all_pokes = behavior_reader.DigitalInputState.read()

    if ignore_dummy_port:
        # remove all nose pokes to dummy port
        all_pokes.drop(columns=['DI3','DIPort2'],inplace = True) 
    else:
        all_pokes.drop(columns=['DIPort2'],inplace = True)

    return all_pokes

# Get a data frame with information about port choice for each trial in trials_df.
# This includes:
# - Whether the trial was aborted
# - The port choice (-1 in aborted trials)
# - The timestamp of the first nosepoke (NaN in aborted trials)

def get_port_choice(trials_df, behavior_reader, ignore_dummy_port=True):

    all_pokes = get_all_pokes(behavior_reader, ignore_dummy_port=ignore_dummy_port)

    # Flag all trials for which 'TrialCompletionCode' contains the string 'Aborted' or 'DotTimeLimitReached' as aborted
    AbortTrial = trials_df['TrialCompletionCode'].str.contains('Aborted|DotTimeLimitReached')
    completed_trials = ~AbortTrial

    # Pre-index ChoicePort and NosepokeInTime_harp
    ChoicePort = np.full(trials_df.shape[0], -1, dtype=int)  # Initialize with -1 to represent aborted trials
    NosepokeInTime_harp = np.full(trials_df.shape[0],np.nan)

    # Get timestamp of first nose poke in response window of non-aborted trials)
    for trial, row in trials_df.iterrows():
        if completed_trials[trial]: # Skip aborted trials
            # Define start of response window as dot offset time
            response_window_start = row['DotOffsetTime_harp']
            
            # Define trial end as simultaneous with the start of the next trial
            # NOTE: # if last trial, take first response in 10s window after dot offset
            if trial == trials_df.shape[0]-1: 
                trial_end = trials_df.loc[trial, 'DotOnsetTime_harp']+100
            else:
                trial_end = trials_df.loc[trial+1, 'DotOnsetTime_harp'] 

            # Get all pokes in each trial between start of response window and trial end
            trial_pokes = all_pokes[(all_pokes.index >= response_window_start) & (all_pokes.index <= trial_end)]

            if not trial_pokes.empty:
                first_poke = trial_pokes.iloc[0]
                # mark choice port row t with 0 = left, 1 = right)
                ChoicePort[trial] = (0 if first_poke['DIPort0'] else 1)
                NosepokeInTime_harp[trial] = first_poke.name
            else:
                Warning('No nosepoke detected in trial ' + str(trial))
                ChoicePort[trial] = np.nan
                NosepokeInTime_harp[trial] = np.nan

    # Convert numpy arrays to pandas Series
    AbortTrial = pd.Series(AbortTrial, name='AbortTrial')
    ChoicePort = pd.Series(ChoicePort, name='ChoicePort')
    NosepokeInTime_harp = pd.Series(NosepokeInTime_harp, name='NosepokeInTime_harp')

    # Create data frame with port choice information
    port_choice_df = pd.concat([AbortTrial, ChoicePort, NosepokeInTime_harp], axis=1)
    
    return port_choice_df

# -----------------------------------------------------------------------------
# Sound card utils
# -----------------------------------------------------------------------------

def get_all_sounds(sound_reader, bin_sound_path):
    
    # Read the harp sound card stream, for the timestamps and audio ID
    all_sounds = sound_reader.PlaySoundOrFrequency.read(bin_sound_path)
    all_sounds.reset_index(inplace=True)

    # Filter to only keep events (when sound actually happened, not write commands to the board) 
    all_sounds = all_sounds.loc[all_sounds['MessageType'] == 'EVENT']

    return all_sounds

def parse_trial_sounds(trials_df, sound_reader, bin_sound_path, OFF_index=18):

    # Read the harp sound card stream, for the timestamps and audio ID
    all_sounds = get_all_sounds(sound_reader, bin_sound_path)

     # Create lists to store the poke IDs and timestamps for all trials
    ON_S, OFF_S, ID_S = [], [], []

    # Iterate through trials (rows) and extract data from harp stream
    for _, trial in trials_df.iterrows():

        # Extract events that occur within the time range of this trial
        trial_events=all_sounds[(all_sounds.Time >= trial.TrialStart) & (all_sounds.Time <= trial.TrialEnd)]

        # Create trial lists for sounds this trial
        ON, OFF, ID = [], [], []
        for _, sound in trial_events.iterrows():
            event_time = sound.Time
            sound = sound[['PlaySoundOrFrequency']]
            sound = int(sound.iloc[0])

            # find audio IDs from the value. Only find ID for OFFSET
            if sound != OFF_index:
                ON.append(event_time)
                ID.append(sound)

            else:
                OFF.append(event_time)

        ON_S.append(ON)
        OFF_S.append(OFF)
        ID_S.append(ID)
        
    trial_sounds_df = pd.DataFrame({'AudioCueStart_harp': ON_S, 'AudioCueEnd_harp': OFF_S, 'AudioCueIdentity_harp': ID_S}) # create dataframe from all nosepoke events

    return trial_sounds_df