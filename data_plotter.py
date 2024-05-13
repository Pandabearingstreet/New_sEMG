"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_stream, local_clock
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque


def main():
    # first resolve an EEG stream on the lab network
    print("looking for an EMG stream...")
    streams = resolve_stream()
    print(streams)
    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    # Initialize your figure and axes
    fig, axs = plt.subplots(nrows=17, ncols=1)

    # Set up empty data arrays for each channel
    data_queues = [deque(maxlen=5000) for _ in range(17)]
    time_queue = deque(maxlen=5000)
    # Set up the initial plots
    plots = [ax.plot([], [])[0] for ax in axs]

    # Define a function to update the plot
    def update_plot(frame):
        # Pull a chunk of data from the LSL stream
        samples, timestamps = inlet.pull_chunk()
        samples = np.array(samples).T
        timestamps = np.array(timestamps)

        time_queue.extend(timestamps)
        for i, channel in enumerate(samples):
            
            data_queues[i].extend(channel)
        

        # Update the plots with the new data
        for i, line in enumerate(plots):
            line.set_data(time_queue, data_queues[i])
            axs[i].relim()
            axs[i].autoscale_view()

        return plots

    # Set up the animation
    ani = animation.FuncAnimation(fig, update_plot, interval=0.1)


    # Show the plot
    plt.show()




if __name__ == "__main__":
    main()