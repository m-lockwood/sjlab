import os
import deeplabcut
from pathlib import Path

#--------------------------------------------------------------------------------------------------#
# CONFIG
#--------------------------------------------------------------------------------------------------#

root_dir = Path("ceph/sjones/projects/FlexiVexi/deeplabcut_models")
project_name = "flexible-navigation-task-ephys-Megan-2024-07-15"
project_path = os.path.join(root_dir, project_name)
config_path = os.path.join(project_name, 'config.yaml')

#--------------------------------------------------------------------------------------------------#
# Train Network
#--------------------------------------------------------------------------------------------------#

deeplabcut.train_network(config_path)
