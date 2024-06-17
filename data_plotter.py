"""
Data_plotter.py

This script visualizes Electromyography (EMG) data streamed over a network using the Lab Streaming Layer (LSL) protocol.
It connects to an EMG stream, pulls data chunks, and continuously updates plots to display real-time EMG signals for each channel.

Requirements:
- pylsl: Python library for Lab Streaming Layer (LSL) communication
- matplotlib: Python plotting library for creating static, animated, and interactive visualizations
- numpy: Python library for numerical computing
- collections: Python module providing specialized container datatypes

Functions:
    main(): Main function to initialize the script and execute the data visualization process.
            It resolves the EMG stream, establishes a connection, initializes the plot, and sets up animation for real-time data updating.

    update_plot(frame): Function responsible for updating the plots with incoming data.
                        It pulls a chunk of data from the LSL stream, extends data buffers with new samples,
                        and updates the plots accordingly.

Usage:
    Run this script to visualize real-time EMG data.
"""
from pylsl import StreamInlet, resolve_stream
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque
import xmltodict
import pandas as pd

def main():
    # Informative message to indicate the commencement of the process of locating an EMG stream.
    print("Initiating search for an Electromyography (EMG) stream...")

    # Resolve available streams on the network
    available_streams = resolve_stream()
    print(*[stream_info.as_xml() for stream_info in available_streams])
    
    # Establish connection with the EMG stream
    inlet = StreamInlet(available_streams[0])
    info_dict = xmltodict.parse(inlet.info().as_xml())
 
    # get the number of channels in the stream
    n_channels = inlet.info().channel_count()
    # Get channel information
    channels = []
    if 'desc' in info_dict['info']:
        if info_dict['info']['desc'] is not None:
            if 'channels' in info_dict['info']['desc']:
                ch = info_dict['info']['desc']['channels']['channel']
                if type(ch) is list:
                    channels.append([c['label'] for c in ch])
                else:
                    channels.append([ch['label']])
                channel_DF = pd.DataFrame(ch)
    print(channel_DF.drop(['label', 'type', 'hardware', 'filtering'],axis=1, inplace=True))
    # Initialize the plot figure and its axes
    fig, axes = plt.subplots(n_channels, ncols=1)

    # Create empty data queues for each channel to store incoming data
    data_buffers = [deque(maxlen=5000) for _ in range(n_channels)]
    time_buffer = deque(maxlen=5000)

    # Initialize the plots
    lines = [ax.plot([], [])[0] for ax in axes]

    # Define a function to update the plots with incoming data
    def update_plot(frame):

        # Pull a chunk of data from the LSL stream
        samples, timestamps = inlet.pull_chunk()
        samples = np.array(samples).T
        timestamps = np.array(timestamps)

        # Extend time buffer with timestamps
        time_buffer.extend(timestamps)

        # Extend data buffers for each channel with incoming data
        for i, channel_data in enumerate(samples):
            data_buffers[i].extend(channel_data)

        # Update the plots with the new data
        for i, line in enumerate(lines):
            line.set_data(time_buffer, data_buffers[i])
            axes[i].relim()
            axes[i].autoscale_view()

        return lines

    # Set up the animation with the update function
    animation_setup = animation.FuncAnimation(fig, update_plot, interval=200)

    # Display the plot
    plt.show()

if __name__ == "__main__":
    main()