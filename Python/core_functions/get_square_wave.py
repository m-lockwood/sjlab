import pandas as pd
def get_square_wave(df): # make names of x,y variables parameterised 
    #so function can be generalised to other variables / data frames?
    # Create a new DataFrame with repeated elements
    square_wave = {'timestamp': df['timestamp'].repeat(2).tolist()[1:],
        'state': df['state'].repeat(2).tolist()[:-1]
        }
    square_wave = pd.DataFrame(square_wave)
    return square_wave