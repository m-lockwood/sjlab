import pandas as pd
import numpy as np
import os

# -----------------------------------------------------------------------------
# TTL utils
# -----------------------------------------------------------------------------

# Get dot onset and offset times given by TTL pulses
def get_dot_times_from_ttl(df,t0):
    
    ## Find index of TTL timestamp closest to the first dot_onset_time in df_trials
    idx = (np.abs(df['timestamp'] - t0)).idxmin()

    ## Remove all TTL pulses that occur before the index found above
    df = df.iloc[idx:]

    ## Remove last rows such that df has a length that is a multiple of 6
    n = len(df) % 6
    df = df.iloc[:-n]
    
    dot_times_ttl = pd.DataFrame({
        'DotOnsetTime_ttl': df['timestamp'].iloc[::6].tolist(),
        'DotOffsetTime_ttl': df['timestamp'].iloc[2::6].tolist()
    })
    return(dot_times_ttl)

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

def get_all_pokes(behavior_reader, ignore_dummy_port=True):

    # Read the behavior harp stream, Digital Input states for the nosepoke 
    # timestamps and IDs.
    all_pokes = behavior_reader.DigitalInputState.read()

    if ignore_dummy_port:
        # remove all nose pokes to dummy port
        all_pokes.drop(columns=['DI3','DIPort2'],inplace = True) 
    else:
        all_pokes.drop(columns=['DIPort2'],inplace = True)

    # reset index to get timestamps as a column   
    all_pokes.reset_index(inplace=True)

    return all_pokes

# Get first nose poke in response window of trial timestamped to harp clock
def get_port_choice(df_trials, behavior_reader):
    
    # Get raw harp output containing all pokes in session
    all_pokes = get_all_pokes(behavior_reader)

    # Flag all trials for which 'TrialCompletionCode' contains the string 'Aborted' or 'DotTimeLimitReached' as aborted
    AbortTrial = df_trials['TrialCompletionCode'].str.contains('Aborted|DotTimeLimitReached')
    completed_trials = ~AbortTrial

    # Pre-index ChoicePort and NosepokeInTime_harp
    ChoicePort = np.full(df_trials.shape[0],np.nan)
    NosepokeInTime_harp = np.full(df_trials.shape[0],np.nan)

    # Get timestamp of first nose poke in response window of non-aborted trials)
    for t, row in df_trials.iterrows():

        if completed_trials[t]: # Skip aborted trials
            # Define start of response window as dot offset time
            response_window_start = row['DotOffsetTime_ttl']
            
            # Define trial end as simultaneous with the start of the next trial
            # NOTE: # if last trial, take first response in 10s window after dot offset
            if t == df_trials.shape[0]: 
                trial_end = df_trials.loc[t, 'DotOnsetTime_ttl']+10
            else:
                trial_end = df_trials.loc[t+1, 'DotOnsetTime_ttl'] 

            # Get all pokes in each trial between start of response window and trial end
            trial_pokes = all_pokes[(all_pokes.Time >= response_window_start) & (all_pokes.Time <= trial_end)]

            if not trial_pokes.empty:
                first_poke = trial_pokes.iloc[0]
                # mark choice port row t with 0 = left, 1 = right)
                ChoicePort[t] = (0 if first_poke['DIPort0'] else 1)
                NosepokeInTime_harp[t] = first_poke.name
            else:
                Warning('No nosepoke detected in trial ' + str(t))
                ChoicePort[t] = np.nan
                NosepokeInTime_harp[t] = np.nan

    # Convert numpy arrays to pandas Series
    AbortTrial = pd.Series(AbortTrial, name='AbortTrial')
    ChoicePort = pd.Series(ChoicePort, name='ChoicePort')
    NosepokeInTime_harp = pd.Series(NosepokeInTime_harp, name='ChoiceTime_harp')

    df_choice = pd.concat([ChoicePort, NosepokeInTime_harp], axis=1)

    return df_choice

def parse_trial_pokes(df_trials, behavior_reader, ignore_dummy_port=True):

    # Read the behavior harp stream, Digital Input states for the nosepoke timestamps and IDs.
    all_pokes = get_all_pokes(behavior_reader, ignore_dummy_port=True)

    # Create lists to store the poke IDs and timestamps for all trials
    PokeON_S, PokeOFF_S, PokeID_S = [], [], []

    # Iterate through trials (rows) and extract data from harp stream
    for index, trial in df_trials.iterrows():

        # Extract events that occur within the time range of this trial
        trial_events=all_pokes[(all_pokes.Time >= trial.TrialStart) & (all_pokes.Time <= trial.TrialEnd)]

        # Create trial lists for ll pokes this trial
        PokeON, PokeOFF, PokeID = [], [], []
        for _, poke in trial_events.iterrows():
            event_time = poke.Time
            if ignore_dummy_port:
                poke = poke[['DIPort0','DIPort1']]
            else:
                poke = poke[['DIPort0','DIPort1','DIPort2']]

            # find poke IDs from which column the timestamp is in. Only find ID for PokeOFFSET
            if poke.any():
                PokeON.append(event_time)
                true_column_index = int(poke.idxmax()[-1]) # find which port
            else:
                PokeOFF.append(event_time)
                PokeID.append(true_column_index) # should be safe unless the state of a nosepoke is already True at the start of a trial (shouldn't ever be true; ports should be initialised in low state)
        PokeON_S.append(PokeON)
        PokeOFF_S.append(PokeOFF)
        PokeID_S.append(PokeID)

    trial_pokes_df = pd.DataFrame({'NosepokeInTimes': PokeON_S, 'NosepokeOutTimes': PokeOFF_S, 'PokeID': PokeID_S}) # create dataframe from all nosepoke events
    return trial_pokes_df

# -----------------------------------------------------------------------------
# Sound card utils
# -----------------------------------------------------------------------------
def get_all_sounds(sound_reader, bin_s_path):
    
    # Read the harp sound card stream, for the timestamps and audio ID
    all_sounds = sound_reader.PlaySoundOrFrequency.read(bin_s_path)
    all_sounds.reset_index(inplace=True)

    # Filter to only keep events (when sound actually happened, not write commands to the board) 
    all_sounds = all_sounds.loc[all_sounds['MessageType'] == 'EVENT']

    return all_sounds

def parse_trial_sounds(df_trials, sound_reader, bin_s_path):

    # Read the harp sound card stream, for the timestamps and audio ID
    all_sounds = get_all_sounds(sound_reader, bin_s_path)

    # Create lists to store the sound IDs and timestamps for all trials
    SoundON_S, SoundOFF_S, SoundID_S = [], [], []

    # Iterate through trials (rows) and extract data from harp stream
    for index, trial in df_trials.iterrows():

        # Extract events that occur within the time range of this trial
        trial_events=all_sounds[(all_sounds.Time >= trial.TrialStart) & (all_sounds.Time <= trial.TrialEnd)]

        # Create trial lists for all sounds this trial
        SoundON, SoundOFF, SoundID = [], [], []
        for _, sound in trial_events.iterrows():
            event_time = sound.Time
            sound_id = sound.PlaySoundOrFrequency
            if sound_id == 0:
                SoundOFF.append(event_time)
            else:
                SoundON.append(event_time)
                SoundID.append(sound_id)
        SoundON_S.append(SoundON)
        SoundOFF_S.append(SoundOFF)
        SoundID_S.append(SoundID)

    trial_sounds_df = pd.DataFrame({'SoundInTimes': SoundON_S, 'SoundOutTimes': SoundOFF_S, 'SoundID': SoundID_S}) # create dataframe from all sound events
    return trial_sounds_df