import spikeinterface.extractors as se
import spikeinterface.sorters as sorters

filepath_experiment_1 = r"Z:\projects\FlexiVexi\NP_recordings\98_2024-04-10_14-42-47_recording_banks1-4\Record Node 102\experiment1\kilosort3"

# Is this just to load a raw recording ? -- maybe this is if I want to run Kilosort from spikeinterface?
recording = se.read_kilosort(filepath_experiment_1)

# This looks like it's for getting the results AFTER I run Kilosort3??
sorters.Kilosort3Sorter.get_result_from_folder()