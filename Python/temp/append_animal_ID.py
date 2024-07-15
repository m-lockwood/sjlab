import os
import glob

root_dir = "W:\\projects\\FlexiVexi\\behavioural_data"
animal_ID = "FNT108"
animal_dir = os.path.join(root_dir, animal_ID)

#==============================================================================
# Change '[session_ID]_video.avi' to '[animal_ID]_[session_ID]_video.avi'
#==============================================================================

# Get all files in animal directory called '[session_ID]_video.avi' and their 
# corresponding session level folder (one level down from animal_dir)   

video_files_and_sessions = [
    (file, os.path.basename(os.path.dirname(os.path.dirname(file))))
    for file in glob.glob(os.path.join(animal_dir, '**', 'Video', '*_*video.avi'), recursive=True)
]

# Assuming animal_ID is defined and accessible
for video_file, session_ID in video_files_and_sessions:
    video_dir = os.path.dirname(video_file)
    # Extract the original filename without the directory
    original_filename = os.path.basename(video_file)
    # Construct the new filename with animal_ID
    new_video_file = os.path.join(video_dir, f"{animal_ID}_{original_filename}")
    os.rename(video_file, new_video_file)
    print(f"Renamed {video_file} to {new_video_file}")

#==============================================================================
# Change '[session_ID]_video.csv' to '[animal_ID]_[session_ID]_video.csv'
#==============================================================================
video_files_and_sessions = [
    (file, os.path.basename(os.path.dirname(os.path.dirname(file))))
    for file in glob.glob(os.path.join(animal_dir, '**', 'Video', '*_*video.csv'), recursive=True)
]

# Assuming animal_ID is defined and accessible
for video_file, session_ID in video_files_and_sessions:
    video_dir = os.path.dirname(video_file)
    # Extract the original filename without the directory
    original_filename = os.path.basename(video_file)
    # Construct the new filename with animal_ID
    new_video_file = os.path.join(video_dir, f"{animal_ID}_{original_filename}")
    os.rename(video_file, new_video_file)
    print(f"Renamed {video_file} to {new_video_file}")

#==============================================================================
# Change '[session_ID]_video_tracking.csv' to '[animal_ID]_[session_ID]_video_tracking.csv'
#==============================================================================

video_files_and_sessions = [
    (file, os.path.basename(os.path.dirname(os.path.dirname(file))))
    for file in glob.glob(os.path.join(animal_dir, '**', 'Video', '*_*video_tracking.csv'), recursive=True)
]

# Assuming animal_ID is defined and accessible
for video_file, session_ID in video_files_and_sessions:
    video_dir = os.path.dirname(video_file)
    # Extract the original filename without the directory
    original_filename = os.path.basename(video_file)
    # Construct the new filename with animal_ID
    new_video_file = os.path.join(video_dir, f"{animal_ID}_{original_filename}")
    os.rename(video_file, new_video_file)
    print(f"Renamed {video_file} to {new_video_file}")