import pandas as pd
def get_dot_times_from_ttl(df):
    # Find the remainder when dividing the current length by 6
    remainder = len(df) % 6
    # If the remainder is not 0, drop the last rows to make it a multiple of 6
    if remainder != 0:
        df = df.iloc[:-remainder]

    dot_times_ttl = pd.DataFrame({
        'DotOnsetTime_ttl': df['timestamp'].iloc[::6].tolist(),
        'DotOffsetTime_ttl': df['timestamp'].iloc[2::6].tolist()
    })
    return(dot_times_ttl)