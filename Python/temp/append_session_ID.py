import os
import glob

root_dir = "W:\\projects\\FlexiVexi\\behavioural_data"
animal_ID = "FNT101"
animal_dir = os.path.join(root_dir, animal_ID)

#==============================================================================
# Change 'video.avi' to '[session_ID]_video.avi'
#==============================================================================

# Get all files in animal directory called 'video.avi' and their corresponding 
# session level folder (one level down from animal_dir)
video_files_and_sessions = [
    (file, os.path.basename(os.path.dirname(os.path.dirname(file))))
    for file in glob.glob(os.path.join(animal_dir, '**', 'Video', 'video.avi'), 
                          recursive=True)
]

# rename all video files in the format [animal_ID]_[session_ID]_video.avi
for video_file, session_ID in video_files_and_sessions:
    video_dir = os.path.dirname(video_file)
    new_video_file = os.path.join(video_dir, f"{session_ID}_video.avi")
    os.rename(video_file, new_video_file)
    print(f"Renamed {video_file} to {new_video_file}")

#==============================================================================
# Change 'video.csv' to '[session_ID]_video.csv'
#==============================================================================

# Get all files in animal directory called 'video.csv' and their corresponding 
# session level folder (one level down from animal_dir)
video_files_and_sessions = [
    (file, os.path.basename(os.path.dirname(os.path.dirname(file))))
    for file in glob.glob(os.path.join(animal_dir, '**', 'Video', 'video.csv'), 
                          recursive=True)
]

# rename all video files in the format [animal_ID]_[session_ID]_video.csv
for video_file, session_ID in video_files_and_sessions:
    video_dir = os.path.dirname(video_file)
    new_video_file = os.path.join(video_dir, f"{session_ID}_video.csv")
    os.rename(video_file, new_video_file)
    print(f"Renamed {video_file} to {new_video_file}")
