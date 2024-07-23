import os
import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt
import time
from model import cnn


TRAINING_DATA_PATH = r"data\LSLGUI_20240613-14-03-04\MindRoveStream_b5e7c297-b318-435b-856c-3efdd84acc7c\runs"
METADATA_PATH = r"data\LSLGUI_20240613-14-03-04\MindRoveStream_b5e7c297-b318-435b-856c-3efdd84acc7c\meta_MindRoveStream_b5e7c297-b318-435b-856c-3efdd84acc7c.json"
plotfigs = True

# get metadata into a dict
with open(METADATA_PATH, 'r') as file:
    metadata_dict = json.load(file)['info']

# fill some useful variables from the metadata:
sf = metadata_dict['nominal_srate']
n_channels = metadata_dict['channel_count']
scale_channels = [float(channel['scaling_factor']) for channel in metadata_dict['desc']['channels']['channel']]
label_channels = [channel['label'] for channel in metadata_dict['desc']['channels']['channel']]
eeg_channels = label_channels[:8]

run_dfs = []
for run in os.listdir(path=TRAINING_DATA_PATH):
    run_dfs.append(pd.read_csv(os.path.join(TRAINING_DATA_PATH,run), sep='\t'))

runs_df = pd.concat(run_dfs, ignore_index=True)

runs_df['Gesture'] = runs_df['Trigger'].rolling(150).sum().shift(-150,fill_value=0).shift(150,fill_value=0)
runs_df['Relative Sample'] = runs_df.groupby((runs_df['Gesture'] != runs_df['Gesture'].shift()).cumsum()).cumcount() + 1

melted_df = runs_df.melt(id_vars=['Timestamp','N','Gesture','Relative Sample'], var_name='channels')

data_gesture_1 = melted_df[melted_df['Gesture']==1].copy()
data_gesture_2 = melted_df[melted_df['Gesture']==2].copy()


if plotfigs:
    
    data_gesture_1['shifted values'] = data_gesture_1['value']
    data_gesture_2['shifted values'] = data_gesture_2['value']

    eeg_values_gesture_1 = data_gesture_1[data_gesture_1['channels'].isin(eeg_channels)]['value'].abs() - (
        500 * data_gesture_1[data_gesture_1['channels'].isin(eeg_channels)]['channels'].str[-1].astype(int))
    eeg_values_gesture_2 = data_gesture_2[data_gesture_2['channels'].isin(eeg_channels)]['value'].abs() - (
        500 * data_gesture_2[data_gesture_2['channels'].isin(eeg_channels)]['channels'].str[-1].astype(int))

    data_gesture_1['shifted values'] = eeg_values_gesture_1
    data_gesture_2['shifted values'] = eeg_values_gesture_2

    now = time.time()
    sns.lineplot(data=data_gesture_1[data_gesture_1['channels'].isin(eeg_channels)], x='Relative Sample', y='value', hue='channels')
    plt.savefig(f'figures/gesture_1_{now}.png')
    plt.clf()
    sns.lineplot(data=data_gesture_2[data_gesture_2['channels'].isin(eeg_channels)], x='Relative Sample', y='value', hue='channels')
    plt.savefig(f'figures/gesture_2_{now}.png')
    plt.clf()


# classify
