from pylsl import StreamInlet, resolve_stream, local_clock
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque
import time
import pandas as pd


EMG_CHANNELS = np.arange(0,8)
TRIGGER_CHANNEL = 9
IMU_CHANNELS = np.arange(10,16)

DATA_PATH = 'data'

def main():
    # Informative message to indicate the commencement of the process of locating an EMG stream.
    print("Initiating search for an Electromyography (EMG) stream...")

    # Resolve available streams on the network
    available_streams = resolve_stream()
    print(*[stream_info.as_xml() for stream_info in available_streams])
    
    # Establish connection with the EMG stream
    inlet = StreamInlet(available_streams[0])

    # get the number of channels in the stream
    n_channels = inlet.info().channel_count()

    # Create empty data queues for each channel to store incoming data
    data_buffers = [deque(maxlen=150) for _ in range(n_channels)]
    time_buffer = deque(maxlen=150)


    start_time = local_clock()
    chunks_recieved = 0
     
    # continually recieve data and record it
    while True:

        # Pull a chunk of data from the LSL stream
        samples, timestamps = inlet.pull_chunk()
        samples = np.array(samples).T
        timestamps = np.array(timestamps)

        # Extend time buffer with timestamps
        time_buffer.extend(timestamps)

        # Extend data buffers for each channel with incoming data
        for i, channel_data in enumerate(samples):
            data_buffers[i].extend(channel_data)

        # check if a trigger was send in the last 300 ms (150 samples)
        trigger_data = data_buffers[TRIGGER_CHANNEL]

        chunks_recieved += 1

        # store data every 60s
        if local_clock() - start_time >= 60:
            store_data(DF)
            start_time = local_clock()

        time.sleep(0.100) # sleep for 100 ms


def store_data(DF : pd.DataFrame):
    print(f'Storing DF with {len(DF)} chunks.')
    DF.to_csv(DATA_PATH)

if __name__ == "__main__":
    print(EMG_CHANNELS, TRIGGER_CHANNEL, IMU_CHANNELS)

    #main()
