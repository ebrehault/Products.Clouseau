unique_id = "clouseau_tool"
product_name = "Clouseau"
layer_name = "clouseau"
layer_location = "Clouseau/skins/Clouseau"

product_globals = globals()

# see README.txt, here's your chance to disable Clouseau
enabled = True
enabled_only_in_debug_mode = True

import os
curdir = os.path.dirname(__file__)

save_directory = os.path.join(curdir, "saved", "local")
load_directories = [save_directory, os.path.join(curdir, "saved", "global")]
