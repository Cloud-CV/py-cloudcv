from  pcloudcv import PCloudCV
import os
login_required = True
config_dict = {}
path_to_config_file = os.path.join(os.getcwd(), "config.json")
pvc  = PCloudCV(path_to_config_file, config_dict, login_required)
pvc.start()

