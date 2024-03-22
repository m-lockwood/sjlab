import pandas as pd

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
    
    return ttl_state_df