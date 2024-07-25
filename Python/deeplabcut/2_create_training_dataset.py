
import os
import deeplabcut
from pathlib import Path
import yaml


#=============================================================================#
# CONFIG
#=============================================================================#

# Get the directory of the current script
script_dir = Path(__file__).resolve().parent

# Open analysis config file
config_path_analysis = os.path.join(script_dir, 'config_analysis.yaml')
with open(config_path_analysis, 'r') as file:
    config = yaml.safe_load(file)

# Load config params
root_dir = config['root_dir']
project_name = config['project_name']
config_path = config['config_path']

#=============================================================================#
# Main Script
#=============================================================================#

# Function to identify labeled videos
def get_labeled_videos(project_path):
    labeled_videos = []
    labeled_data_path = Path(os.path.join(project_path,'labeled-data'))
    for session_dir in labeled_data_path.iterdir():
        if session_dir.is_dir() and any(session_dir.glob('CollectedData*.csv')):  
            labeled_videos.append(session_dir.name)
    return labeled_videos

# Open config file
config_path = os.path.join(root_dir, project_name, 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Filter videos based on labeled data
labeled_videos = get_labeled_videos(project_path)
print(labeled_videos)
config['video_sets'] = {video: config['video_sets'][video] for video in labeled_videos if video in config['video_sets']}

print(help(deeplabcut.create_training_dataset))
# Automatically extract frames from all videos in video_dir
deeplabcut.create_training_dataset(config=config, num_shuffles=1, net_type='resnet_50', augmenter_type='imgaug')