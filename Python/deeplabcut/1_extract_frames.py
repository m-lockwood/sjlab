"""
1_extract_frames_auto.py

Description:
    This script extracts frames from videos in the 'videos' directory 
    using the cropping parameters specified in config.yaml    

Dependencies:
    - deeplabcut
    - os
    - glob
    - yaml

Usage:
    - This script is intended to run after a project has been created using 0_create_project.py
    - Check the project config.yaml file to ensure that the 'numframes2pick' parameter is set to the desired
        value.

    Parameters
    ----------

    crop:
        (i) 'True', the cropping parameters [x1 x2 y1 y2] must be specified in the 
            corresponding config.yaml for each video.
            (NOTE: If no parameters have been specified for a given video, the code will run as normal
            without cropping the corresponding video.)
        (ii) 'False', cropping will not be applied.
        (iii) 'GUI', the user will be prompted to manually crop each video before the frames are extracted.
            (NOTE: This will not be possible when running this script from the cluster.)

    userfeedback:
        (i) 'True', the user will be prompted on whether to extract frames on each session 
            in the videos directory for the specified DeepLabCut project.
        (ii) 'False', frames will be extracted from all videos in the videos directory without user input.

Input:
    The input parameters are specified in the config.yaml file. 
    The script will read the video files from the 'videos' directory.

Output:
    The script will output the n frames for each video in [project path]\\videos, where n is specified 
    under 'numframes2pick' in config.yaml. These will be saved under [project path]\\labeled-data\\[video name]
    for every video.

"""

import os
import deeplabcut
from pathlib import Path

project_path = os.path.join(root_dir, project_name)
video_dir = os.path.join(project_path, 'videos')

# Extract frames from videos in video_list
config_path = os.path.join(project_path, 'config.yaml')

# Automatically extract frames from all videos in video_dir
deeplabcut.extract_frames(
    config=config_path,
    mode='automatic',
    algo='kmeans',
    crop=True,  # This enables manual cropping via the GUI
    userfeedback=False
)