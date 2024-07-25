import os
import yaml
from pathlib import Path
import deeplabcut

# Open config file
# Get the directory of the current script
script_dir = Path(__file__).resolve().parent

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

print('Analyzing videos for project:', project_name)

# Choose videos to be analyzed
video_dir = os.path.join(root_dir, project_name, 'videos')
videos = config.get('videos', [])

# Analyze videos
deeplabcut.analyze_videos(config_path, videos, 
                          videotype='avi', 
                          shuffle=1, 
                          trainingsetindex=0, 
                          save_as_csv=True,
                          destfolder=video_dir, 
                          )

#create labelled videos
deeplabcut.create_labeled_video(config_path, videos, 
                                shuffle=1, 
                                trainingsetindex=0, 
                                filtered=True, 
                                destfolder=video_dir, 
                                draw_skeleton=True
                                )