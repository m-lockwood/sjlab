import os
import glob
import deeplabcut

# NOTE: Videos will be copied due to administrator issues in Windows. 'Run as 
#  administrator' doesn't work as it prevents access to ceph. To avoid this, 
#  run the script from the cluster for now...

# -----------------------------------------------------------------------------
# Section 0: Define directory and analysis params
# -----------------------------------------------------------------------------

project_name='flexible-navigation-task-ephys'
experimenter_name = 'Megan'

# Directory under which DLC project will be saved
project_dir='W:\\projects\\FlexiVexi\\deeplabcut_models'

# Directory containing behavioural and ephys data
input_dir='W:\\projects\\FlexiVexi\\behavioural_data'

# -----------------------------------------------------------------------------
# Section 1: Get list of ephys video filepaths
# -----------------------------------------------------------------------------

# Return list of session folders in input_dir contain ephys data (given by 
# 'continuous.dat')
ephys_session_list = [
    os.path.join(animal_folder, d)
    for animal_folder in [os.path.join(input_dir, animal) for animal in os.listdir(input_dir) 
                          if os.path.isdir(os.path.join(input_dir, animal))]
    for d in os.listdir(animal_folder) 
    if os.path.isdir(os.path.join(animal_folder, d)) 
    and glob.glob(os.path.join(animal_folder, d, '**', 'continuous.dat'), recursive=True)
]

# Return filepaths for all .avi files filepaths in ephys_session_list
video_list = [
    file
    for session_folder in ephys_session_list
    for file in glob.glob(os.path.join(session_folder, '**', '*.avi'), recursive=True)
]

# -----------------------------------------------------------------------------
# Section 2: Create a new DeepLabCut project
# -----------------------------------------------------------------------------

# Create new project with the given name, user, video list, and working 
# directory
config_path = deeplabcut.create_new_project(
    project_name, 
    experimenter_name, 
    video_list, 
    working_directory=project_dir, 
    copy_videos=True, 
    multianimal=False
)