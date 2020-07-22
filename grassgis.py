import os
import grass.script as grass


CURRENT_DATABASE = grass.gisenv()['GISDBASE']
CURRENT_LOCATION = grass.gisenv()['LOCATION_NAME']
CURRENT_MAPSET = grass.gisenv()['MAPSET']
CURRENT_MAPSET_PATH = os.path.join(CURRENT_DATABASE, CURRENT_LOCATION, CURRENT_MAPSET)
