import matplotlib.pyplot as plt

def plot_ttl_pulse(ttl_state_df):

    ttl_pulse = get_square_wave(ttl_state_df)

    plt.figure()
    ttl_pulse.plot(x = 'timestamp', y = 'state')
    plt.xlabel('timestamp (s)')
    plt.legend(loc = 'upper right')